import os
import subprocess
import json
import threading

_RPROXY = os.path.join(os.path.dirname(__file__), 'rproxy')

class Rproxy(object):
  def __init__(self):
    self._command = _RPROXY
    self._lock = threading.RLock()
    self._dead = False
    self._proc = None
    self._thread = None
    self._waiting = {}
    self._replies = {}
    self._id = 0

  def _get_sink(self):
    with self._lock:
      if self._dead:
        raise Exception("Rproxy is dead")

      if self._proc:
        return self._proc.stdin

      self._proc = subprocess.Popen([self._command], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None)
      self._thread = threading.Thread(target=self._process_events, args=(self._proc.stdout, self._proc))
      self._thread.start()
      return self._proc.stdin

  def _process_events(self, source, proc):
    while True:
      try:
        line = source.readline()
      except ValueError:
        break
      if not line:
        break

      try:
        event = json.loads(line)
      except json.decoder.JSONDecodeError as ex:
        raise Exception("Error decoding %r: %s" % (line, ex))

      id = event['id']
      if id in self._waiting:
        with self._lock:
          cv = self._waiting[id]
          del self._waiting[id]
          self._replies[id] = event
        with cv:
          cv.notify_all()
      else:
        print(event)

    result = proc.wait()
    with self._lock:
      self._thread = None
      self._proc = None
      self._dead = True

  def _emit(self, command):
    sink = self._get_sink()
    sink.write(json.dumps(command).encode('utf-8'))
    sink.write(b"\n")
    sink.flush()

  def mount(self, url, default_headers={}):
    self._id += 1
    id = str(self._id)
    cv = threading.Condition()
    with cv:
      with self._lock:
        self._waiting[id] = cv
      self._emit({'action': 'mount', 'target': url, 'defaultHeaders': default_headers, 'id': id})
      cv.wait()
      with self._lock:
        reply = self._replies[id]
        del self._replies[id]
      # print(reply)
      return reply['id'], reply['localAddress']

  def unmount(self, id):
    with self._lock:
      if not self._proc:
        raise Exception("Not running. Can't unmount: %s" % id)

      if self._dead:
        return
    
    self._emit({'action': 'unmount', 'id': id})
  
  def close(self):
    with self._lock:
      if not self._proc:
        return

      self._proc.stdin.close()

    self._thread.join()
