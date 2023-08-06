import base64
import hashlib
import json
import os
import requests
import threading
import urllib.parse

from bravado.exception import HTTPInternalServerError
from bravado.requests_client import RequestsClient
from bravado.client import SwaggerClient

from tqdm import tqdm
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

class CredentialStorage(object):
  def __init__(self, host):
    self._host = host
    self._auth_file = os.environ.get('TESSERAI_AUTH', os.path.expanduser('~/.tesserai-auth'))
    self._auth_http_client = None
    self._cached_auth = None
    self._lock = threading.RLock()

  def auth_exists(self):
    return os.path.exists(self._auth_file)

  def get_auth(self):
    return dict(self._cached_auth)

  def save(self, auth):
    with self._lock:
      # Force auth client to be recreated next time we need it.
      self._auth_http_client = None
      self._cached_auth = None

      auth = {
        'id': auth.id,
        'secret': auth.secret,
      }
      with open(self._auth_file, 'w') as f:
        json.dump(auth, f)

  def http_client(self):
    with self._lock:
      if not self._auth_http_client:
        auth = self._get_auth()
        auth_http_client = RequestsClient()
        auth_http_client.set_basic_auth(
            self._host,
            auth['id'], auth['secret'],
        )
        self._auth_http_client = auth_http_client
      return self._auth_http_client

  def _get_auth(self):
    with self._lock:
      if not self._cached_auth:
        self._cached_auth = self._read()
      return self._cached_auth

  def _read(self):
    if not self.auth_exists():
      raise Exception("Missing auth, need to run auth init")

    with open(self._auth_file) as f:
      return json.load(f)

class Client(object):
  def __init__(self, host=None):
    if host is None:
      self._host = os.environ.get('TESSERAI_HOST', 'us-central-1.tesseraiml.com')
    self._scheme = "https"
    self._cred_storage = CredentialStorage(self._host.split(':')[0])
    self._lock = threading.RLock()
    self._clients = {}

  def _get_client(self, api_name, *, use_auth=True):
    with self._lock:
      key = (api_name, use_auth)
      if key not in self._clients:
        http_client = self._cred_storage.http_client() if use_auth else None
        url = "%s://%s/%s/swagger.json" % (self._scheme, self._host, api_name)
        self._clients[key] = SwaggerClient.from_url(url, http_client=http_client)
      return self._clients[key]

  def auth_headers(self):
    auth = self._cred_storage.get_auth()
    username, password = auth['id'], auth['secret']
    authorization_raw = base64.b64encode(('%s:%s' % (username, password)).encode('utf-8')).decode('utf-8')
    authorization_header = "Basic %s" % authorization_raw.replace('\n', '')
    return {
      "authorization": authorization_header,
    }

  def auth_init(self, overwrite=False, subscription_id=None):
    if self._cred_storage.auth_exists() and not overwrite:
      raise Exception("Already have auth, can't init again.")

    auth = self._get_client('v1', use_auth=False).authorization.create(body={'subscriptionId': subscription_id}).result()
    self._cred_storage.save(auth)
    with self._lock:
      # Drop our existing cache of clients.
      self._clients.clear()

    return auth

  def cluster_create(self, cluster_request):
    ac = self._get_client('v1')
    ClusterRequest = ac.get_model('ClusterRequest')
    ClusterSpec = ac.get_model('ClusterSpec')
    cr = ClusterRequest._unmarshal(cluster_request)
    try:
      cl = ac.cluster.create(body=cr).result()
      return cl, ClusterSpec._marshal(cl.clusterSpec)
    except HTTPInternalServerError as e:
      print(e.response.text)
      raise e

  def cluster_list(self):
    return self._get_client('v1').cluster.list().result()

  def cluster_destroy(self, cluster_id):
    return self._get_client('v1').cluster.delete(clusterId=cluster_id).result()

  def cluster_get(self, cluster_id):
    return self._get_client('v1').cluster.get(clusterId=cluster_id).result()

  def tensorboard_create(self, tensorboard_request):
    ac = self._get_client('v1')
    TensorBoardRequest = ac.get_model('TensorBoardRequest')
    tr = TensorBoardRequest._unmarshal(tensorboard_request)
    try:
      tr = ac.tensorboard.create(body=tr).result()
      return tr
    except Exception as e:
      print(e.response.text)
      raise e

  def tensorboard_list(self):
    return self._get_client('v1').tensorboard.list().result()

  def tensorboard_destroy(self, tensorboard_id):
    return self._get_client('v1').tensorboard.delete(tensorboardId=tensorboard_id).result()

  def tensorboard_get(self, tensorboard_id):
    return self._get_client('v1').tensorboard.get(tensorboardId=tensorboard_id).result()

  def saga_create(self, saga_request):
    ac = self._get_client('sagas/v1')
    SagaRequest = ac.get_model('SagaRequest')
    tr = SagaRequest._unmarshal(saga_request)
    tr = ac.saga.create(body=tr).result()
    return tr

  def saga_list(self):
    return self._get_client('sagas/v1').saga.list().result()

  def saga_destroy(self, saga_id):
    return self._get_client('sagas/v1').saga.delete(sagaId=saga_id).result()

  def saga_get(self, saga_id):
    return self._get_client('sagas/v1').saga.get(sagaId=saga_id).result()

  def model_create(self, model_file):
    ac = self._get_client('models/v1')
    ModelRequest = ac.get_model('ModelRequest')

    with open(model_file, 'rb') as file:
      filesize, sha256 = self._sha256_for_file(file)

      d = ModelRequest._unmarshal({
        'runtime': 'tensorflow',
        'artifactSha256': sha256,
      })
      try:
        print(ac.model, dir(ac.model))
        md = ac.model.create(body=d).result()
        print("md", md)
        upload_url = "%s://%s%s" % (self._scheme, self._host, md.artifactUploadUrl)
        a = self._model_upload_artifact(upload_url, filesize, file)
        print("a", a)
        m = ac.model.update(modelId=md.id).result()
        print("m", m)
        return m
      except Exception as e:
        print(e.response.text)
        raise e

  def model_list(self):
    try:
      return self._get_client('models/v1').model.list().result()
    except Exception as e:
      print(e.response.text)

  def model_destroy(self, model_id):
    return self._get_client('models/v1').model.delete(modelId=model_id).result()

  def model_get(self, model_id):
    return self._get_client('models/v1').model.get(modelId=model_id).result()

  def _sha256_for_file(self, f, buf_size=65536):
      pos = f.tell()
      dgst = hashlib.sha256()
      while True:
          data = f.read(buf_size)
          if not data:
              break
          dgst.update(data)
      size = f.tell() - pos
      f.seek(pos)

      return size, dgst.hexdigest()

  def _model_upload_artifact(self, upload_url, filesize, file):
    progress = tqdm(
            total=filesize,
            desc="Uploading",
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            leave=True)

    last_bytes_read = 0
    def update_progress(monitor):
        # Your callback function
        nonlocal last_bytes_read
        progress.update(monitor.bytes_read - last_bytes_read)
        last_bytes_read = monitor.bytes_read

    e = MultipartEncoder(fields={'uploadfile': ('uploaded', file, 'text/plain')})
    m = MultipartEncoderMonitor(e, update_progress)
    headers = {
      "X-File-Size": str(filesize),
      'Content-Type': m.content_type,
    }
    headers.update(self.auth_headers())
    print("headers", headers)
    print("upload_url", upload_url)
    
    update_progress(m)
    archive_response = requests.post(upload_url,
            data=m,
            headers=headers)
    update_progress(m)

    # archive_id = archive_response.json()['id']
    print(" done", flush=True)
    print(archive_response.text)

