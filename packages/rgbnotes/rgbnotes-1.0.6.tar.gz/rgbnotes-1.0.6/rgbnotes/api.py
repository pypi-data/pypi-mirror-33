import requests
import simplejson
from functools import partial
from collections import namedtuple

import api_config


_CREATED_USERS_ = []


field_filter = namedtuple('filter', ['field', 'op', 'value'])


class RGB_API_Error(Exception):
    '''RGB Notes API Error base class'''


def init_http_logger():
    '''initialize logging, otherwise you will not see anything from requests'''
    import logging
    import httplib
    httplib.HTTPConnection.debuglevel = 1

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


class RGB_API(object):
    '''Python interface for RGB Notes API'''

    DEFAULT_CACHE_TIMEOUT = 60
    DEFAULT_TIMEOUT = (3.05, 27)

    def __init__(self,
                 config=None,
                 api_url='https://rgbnotes.com/api/v1',
                 client_key=None,
                 client_id=None,
                 debug_http=False,
                 timeout=None):

        self._cache_timeout = RGB_API.DEFAULT_CACHE_TIMEOUT
        self._timeout = timeout or RGB_API.DEFAULT_TIMEOUT
        self._debug_http = debug_http

        if not api_url:
            try:
                self._config = config or api_config.get_config()

            except api_config.RGB_ConfigError as e:
                raise RGB_API_Error('"api_url" not passed and not '
                                    'found in any config: {}'.format(e))

        self.api_url = api_url or self._config.get('rgbnotes',
                                                   'api_url')

        if not client_id:
            try:
                self._config = config or api_config.get_config()

            except api_config.RGB_ConfigError as e:
                raise RGB_API_Error('"client_id" not passed and not '
                                    'found in any config: {}'.format(e))

        self._client_id = client_id or self._config.get('rgbnotes',
                                                        'client_id')

        if not client_key:
            try:
                self._config = config or api_config.get_config()

            except api_config.RGB_ConfigError as e:
                raise RGB_API_Error('"client_key" not passed and not '
                                    'found in any config: {}'.format(e))

        self._client_key = client_key or self._config.get('rgbnotes',
                                                          'client_key')

        if self._debug_http:
            init_http_logger()

        self._init_credentials()

        if _CREATED_USERS_:
            for user in _CREATED_USERS_:
                self.created_user(user)

    def _init_credentials(self):
        self._credentials = dict(
            client_id=self._client_id,
            client_key=self._client_key)
        handler = self.client_token_request
        self.client_token = handler
        self.client_token_header = self.client_token

    @property
    def client_token(self):
        '''API token getter'''
        data = getattr(self, '__client_token', None)
        if data:
            return data.get('token', None)

    @client_token.setter
    def client_token(self, handler):
        '''API token setter'''
        self._set_response_data(handler, '__client_token')

    @property
    def client_token_header(self):
        '''client token header data used in requests'''
        return getattr(self, '__client_token_header', None)

    @client_token_header.setter
    def client_token_header(self, token):
        '''Compose the header data using token'''
        setattr(self, '__client_token_header',
                {'Rgb-Client-Token': token})

    @property
    def project_member_token(self):
        '''API token getter'''
        data = getattr(self, '__project_member_token', None)
        if data:
            return data.get('token', None)

    @project_member_token.setter
    def project_member_token(self, handler):
        '''API token setter'''
        self._set_response_data(handler, '__project_member_token')

    @property
    def project_member_token_header(self):
        '''client token header data used in requests'''
        return getattr(self, '__project_member_token_header', None)

    @project_member_token_header.setter
    def project_member_token_header(self, token):
        '''Compose the header data using token'''
        setattr(self, '__project_member_token_header',
                {'Rgb-Project-Member-Token': token})

    @property
    def projects(self):
        '''Projects list getter'''
        return getattr(self, '__projects', None)

    @projects.setter
    def projects(self, handler):
        '''Projects list setter'''
        self._set_response_data(handler, '__projects')

    @property
    def project_files(self):
        '''Project_files list getter'''
        return getattr(self, '__project_files', None)

    @project_files.setter
    def project_files(self, handler):
        '''Project_files list setter'''
        self._set_response_data(handler, '__project_files')

    @property
    def project_notes(self):
        '''Project_notes list getter'''
        return getattr(self, '__project_notes', None)

    @project_notes.setter
    def project_notes(self, handler):
        '''Project_notes list setter'''
        self._set_response_data(handler, '__project_notes')

    @property
    def users(self):
        '''Users list getter'''
        return getattr(self, '__users', None)

    @users.setter
    def users(self, handler):
        '''Users list setter'''
        self._set_response_data(handler, '__users')

    @property
    def last_created_user(self):
        '''Get the latest user created'''
        return getattr(self, '__last_user_created', None)

    @property
    def created_users(self):
        ''''''
        return getattr(self, '__created_users', None)

    def created_user(self, userdata, reset=False):
        if reset:
            setattr(self, '__created_users', None)
        elif self.created_users:
            self.created_users.append(userdata)
        else:
            setattr(self, '__created_users', [userdata])

    def _set_response_data(self, handler, attr):
        '''
        For internal use: Set internally the data received from a
        GET request handler
        '''
        if callable(handler):
            r = handler()
        else:
            r = None

        if isinstance(r, requests.Response):
            if 'application/json' in r.headers['content-type']:
                try:
                    d = r.json()
                except simplejson.scanner.JSONDecodeError:
                    try:
                        # try and clean up junk
                        d = simplejson.loads(r.content.split('\n')[0])
                    except simplejson.scanner.JSONDecodeError as e:
                        raise RGB_API_Error('There was an issue decoding the server response!')
                    else:
                        if 'error' in d:
                            raise RGB_API_Error(d['error'])
                        else:
                            setattr(self, attr, d)
                else:
                    setattr(self, attr, d)

    '''Methods'''

    def fetch(self, items):
        if isinstance(items, basestring):
            if items == 'all':
                items = ['projects', 'users']
            else:
                items = [items]
        items = list(set([i for i in items if i in ('projects', 'users')]))
        if not items:
            return
        while items:
            item = items.pop()
            if item == 'projects':
                req = self.projects_request
                self.projects = req
            if item == 'users':
                req = self.users_request
                self.users = req

    def create_user(self, name, **kwargs):
        if not self.users:
            self.fetch('users')
        kwargs['name'] = name
        create = False
        if not self.users and not self.created_users:
            create = True
        if self.users:
            if any(name in user.values() for user in self.users):
                print('User "{}" already exists'.format(name))
                create = False
            else:
                create = True
        if self.created_users:
            if any(name in cr_user.values() for cr_user in self.created_users):
                print('User "{}" already exists'.format(name))
                create = False

        if create:
            handler = partial(self.create_user_request, kwargs)
            self._set_response_data(handler, '__last_user_created')
            self.created_user(self.last_created_user)

    def find(self, typ, f):
        if typ == 'project':
            if not self.projects:
                self.fetch('projects')
            _filter = field_filter(*f)
            src = '[p for p in self.projects if p.get(_filter.field, None) {} _filter.value]'.format(_filter.op)
            return eval(src)
        if typ == 'user':
            if not self.users:
                self.fetch('users')
            _filter = field_filter(*f)
            src = '[p for p in self.users if p.get(_filter.field, None) {} _filter.value]'.format(_filter.op)
            return eval(src)

    def find_one(self, typ, f):
        return self.find(typ, f)[-1]

    def get_project_member_token(self, user_id, project_id):
        '''
        Get project member token data using the user's id and project id

        :param int user_id: numerical user id
        :param int project_id: numerical project id
        '''
        params = dict(user_id=user_id, project_id=project_id)
        handler = partial(self.project_member_token_request, params)
        self.project_member_token = handler
        self.project_member_token_header = self.project_member_token

    def get_project_files(self, project_id, **kwargs):
        params = dict(project_id=project_id, **kwargs)
        handler = partial(self.project_files_request, params)
        self.project_files = handler

    def get_project_notes(self, project_id, **kwargs):
        params = dict(project_id=project_id, **kwargs)
        handler = partial(self.project_notes_request, params)
        self.project_notes = handler

    '''GET'''

    def get_request(self, params=None, endpoint=None):
        '''GET Request for getting project data'''
        if self.client_token_header:
            try:
                r = requests.get(self.api_url + endpoint,
                                 headers=self.client_token_header,
                                 params=params,
                                 timeout=self._timeout)
            except requests.RequestException as e:
                raise RGB_API_Error(str(e))
            else:
                if r.status_code == requests.codes.ok:
                    return r
                else:
                    print r.text
                    print 'That\'s an error: {}'.format(r.status_code)
        else:
            raise RGB_API_Error('Request client token first')

    def projects_request(self, endpoint='/projects'):
        '''GET Request for project data'''
        return self.get_request(endpoint=endpoint)

    def users_request(self, endpoint='/users'):
        '''GET Request for users data'''
        return self.get_request(endpoint=endpoint)

    def project_files_request(self, proj_data, endpoint='/project_files'):
        '''GET Request for listing project files'''
        return self.get_request(params=proj_data, endpoint=endpoint)

    def project_notes_request(self, proj_data, endpoint='/project_notes'):
        '''GET Request for listing project notes'''
        return self.get_request(params=proj_data, endpoint=endpoint)

    '''POST'''

    def post_request(self, data, endpoint=None):
        '''POST requests on behalf of the project admin'''
        if self.client_token_header and isinstance(data, dict):
            try:
                r = requests.post(self.api_url + endpoint,
                                  headers=self.client_token_header,
                                  data=data,
                                  timeout=self._timeout)
            except requests.RequestException as e:
                raise RGB_API_Error(str(e))
            else:
                if r.status_code == requests.codes.ok:
                    return r
                else:
                    print r.text
                    raise RGB_API_Error('Request returned an error: {}'.format(
                        r.status_code))
        else:
            raise RGB_API_Error('Request client token first')

    def project_post_request(self, data, file_data=None, endpoint=None):
        '''POST requests on behalf of a project member'''
        if self.project_member_token_header and isinstance(data, dict):
            try:
                r = requests.post(self.api_url + endpoint,
                                  headers=self.project_member_token_header,
                                  data=data,
                                  files=file_data,
                                  timeout=self._timeout)
            except requests.RequestException as e:
                raise RGB_API_Error(str(e))
            else:
                if r.status_code == requests.codes.ok:
                    return r
                else:
                    print r.text
                    raise RGB_API_Error('Request returned an error: {}'.format(
                        r.status_code))
        else:
            raise RGB_API_Error('Request project member token first')

    def token_request(self, params=None, headers=None, endpoint=None):
        '''POST Request for API token'''
        if self._client_key:
            if isinstance(params, dict):
                params.update(self._credentials)
            else:
                params = self._credentials

            try:
                r = requests.post(self.api_url + endpoint,
                                  headers=headers,
                                  data=params,
                                  timeout=self._timeout)
            except requests.RequestException as e:
                raise RGB_API_Error(str(e))
            else:
                if r.status_code == requests.codes.ok:
                    return r
                else:
                    raise RGB_API_Error(['Error: {}'.format(r.status_code),
                                         r.text])

    def client_token_request(self, endpoint='/token/client'):
        '''POST Request for an RGB client token'''
        return self.token_request(endpoint=endpoint)

    def create_user_request(self, user_data, endpoint='/user_create'):
        '''POST Request for creating users'''
        return self.post_request(data=user_data, endpoint=endpoint)

    '''Project MGMT'''

    def project_member_token_request(self, params,
                                     endpoint='/token/project_member'):
        '''POST Request for RGB project member token'''
        return self.token_request(params=params, endpoint=endpoint)

    def create_project_request(self, proj_data, endpoint='/project_create'):
        '''POST Request for creating projects'''
        return self.post_request(data=proj_data, endpoint=endpoint)

    def edit_project_request(self, proj_data, endpoint='/project_edit'):
        '''POST Request for editing projects'''
        return self.post_request(data=proj_data, endpoint=endpoint)

    '''File MGMT'''

    def upload_file_request(self, data, file_data, endpoint='/upload'):
        '''POST Request for uploading files'''
        return self.project_post_request(data, file_data=file_data,
                                         endpoint=endpoint)
