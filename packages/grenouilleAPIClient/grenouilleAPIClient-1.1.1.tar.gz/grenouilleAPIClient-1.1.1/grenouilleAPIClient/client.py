import requests
import json

class GrenouilleAPIClient:
    host = ''
    key = ''
    refresh_token = ''
    auth_token = ''

    def __init__(self, host, key):
        self.host = host
        self.key = key
        self.get_refresh_token()
        self.get_auth_token() # TODO dynamically call this

    def get_refresh_token(self):
        r = requests.get(self.host + '/api/auth/login/key', headers={'API_KEY': self.key}, json={})
        response = r.json()
        if response['success'] == 'yes':
            self.refresh_token = response['payload']['token']

    def get_auth_token(self):
        r = requests.get(self.host + '/api/auth/token', headers={'Authorization': 'Bearer {0}'.format(self.refresh_token)}, json={})
        response = r.json()
        if response['success'] == 'yes':
            self.auth_token = response['payload']['token']

    # Wrappers

    def get(self, endpoint, payload):
        r = requests.get(self.host + endpoint,
                         headers={'Authorization': 'Bearer {0}'.format(self.auth_token)}, json=payload)
        return r.json()

    def post(self, endpoint, payload):
        r = requests.post(self.host + endpoint,
                         headers={'Authorization': 'Bearer {0}'.format(self.auth_token)}, json=payload)
        return r.json()

    #################
    # EndpointCalls #
    #################

    # Auth

    def scope_list(self):
        return self.get('/api/auth/scope/list', {})

    def api_key_list(self, limit=10, offset=0):
        return self.get('/api/auth/key/list', { 'limit': limit, 'offset': offset })

    def api_key_add(self, key, description):
        return self.post('/api/auth/key/add', { 'key': key, 'description': description })

    def api_key_remove(self, key):
        return self.post('/api/auth/key/remove', { 'key': key })

    def api_key_description_update(self, key, description):
        return self.post('/api/auth/key/description/update', { 'key': key, 'description': description })

    def api_key_scope_add(self, key, scopes):
        return self.post('/api/auth/key/scope/add', { 'key': key, 'scopes': scopes })

    def api_key_scope_remove(self, key, scopes):
        return self.post('/api/auth/key/scope/remove', { 'key': key, 'scopes': scopes })

    def user_scope_list(self, limit=10, offset=0):
        return self.get('/api/auth/user/scope/list', { 'limit': limit, 'offset': offset })

    def user_scope_add(self, id, scopes):
        return self.post('/api/auth/user/scope/add', { 'id': id, 'scopes': scopes })

    def user_scope_remove(self, id, scopes):
        return self.post('/api/auth/user/scope/remove', { 'id': id, 'scopes': scopes })

    # OBS

    def OBS_status(self):
        return self.get('/api/obs/status', {})

    def OBS_list_scene(self):
        return self.get('/api/obs/scene/list', {})

    def OBS_change_scene(self, scene):
        return self.post('/api/obs/scene/update', {'scene': scene})

    def OBS_start_record(self):
        return self.post('/api/obs/record/start', {})

    def OBS_stop_record(self):
        return self.post('/api/obs/record/stop', {})

    def OBS_start_stream(self):
        return self.post('/api/obs/stream/start', {})

    def OBS_stop_stream(self):
        return self.post('/api/obs/stream/stop', {})

    def OBS_get_playlist(self):
        return self.get('/api/obs/playlist/get', {})

    def OBS_set_playlist(self, files):
        return self.post('/api/obs/playlist/update', {'files': files})
    # VOD

    def VOD_disk_usage(self):
        return self.get('/api/vod/disk_usage', {})

    def VOD_file_list(self):
        return self.get('/api/vod/file/list', {})

    def VOD_file_delete(self, filename):
        return self.post('/api/vod/file/delete', {'filename': filename })

    def VOD_dir_create(self, dir):
        return self.post('/api/vod/dir/create', {'dir': dir })

    def VOD_file_move(self, source, destination):
        return self.post('/api/vod/file/move', {'source': source, 'destination': destination })
