import re
import six
import time
import json
import requests
from datetime import datetime
import avi_okta.OktaError as OktaError

API_PATH = '/api/v1/'
INTERNAL_API_PATH = '/api/internal/'
HOME_PATH = '/app/UserHome'
SESSION_COOKIE_PATH = '/login/sessionCookieRedirect'


class ApiClient(object):

    def __init__(self, base_url, token=None, username=None, password=None, max_retries=3):
        if not token and not (username and password):
            raise ValueError('An API token or username and password are required')

        self.base_url = base_url
        self.api_url = base_url + API_PATH
        self.max_attemps = max_retries + 1

        self.sessions = {}
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json, application/xml',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
        })

        if token:
            self.session.headers.update({'Authorization': 'SSWS ' + token})
            self.sessions['token'] = self.session
            return

        # Authenticate to get a session token
        data = {'username':username, 'password':password}
        rsp = self.post('authn', data=data)
        session_token = rsp.json()['sessionToken']

        # Trade session token for a session cookie and CSRF token
        params = {
            'token': session_token,
            'redirectUrl': base_url + HOME_PATH,
        }
        rsp = self._get(base_url + SESSION_COOKIE_PATH, params=params)
        match = re.search(r'xsrfToken">(.+?)<', rsp.content)
        csrf_token = match.group(1)
        self.session.headers.update({"X-Okta-XsrfToken": csrf_token})
        self.sessions['cookie'] = self.session

    def _init_internal_api_session(self):
        session = requests.Session()
        session.headers.update(self.session.headers)
        session.cookies.update(self.session.cookies)

        # Get a session token
        session.headers.update({"Accept": "*/*"})
        rsp = session.get(self.base_url + "/app/admin/sso/saml")
        match = re.search(r'token":\["(.+?)"', rsp.content)
        session_token = match.group(1)

        # Trade session token for a session cookie and CSRF token
        parts = self.base_url.split('.', 1)
        self.base_admin_url = "%s-admin.%s" % (parts[0], parts[1])
        session.cookies.clear()
        session.headers.update({
            'Content-Type': 'application/x-www-form-urlencoded',
        })
        data = {"token": session_token}
        rsp = session.post(self.base_admin_url + "/admin/sso/request", data=data)
        match = re.search(r'xsrfToken">(.+?)<', rsp.content)
        csrf_token = match.group(1)

        # Reset headers to standard values
        session.headers.update({
            'Accept': 'application/json, application/xml',
            'Content-Type': 'application/json',
            'X-Okta-XsrfToken': csrf_token,
        })
        self.sessions['cookie-internal'] = session

    def target_standard_api(self):
        self.session = self.sessions['cookie']
        self.api_url = self.base_url + API_PATH

    def target_internal_api(self):
        if not self.sessions.get('cookie-internal'):
            self._init_internal_api_session()
        self.session = self.sessions['cookie-internal']
        self.api_url = self.base_admin_url + INTERNAL_API_PATH

    def close_sessions(self):
        if not self.sessions.get('cookie'):
            return
        self.target_standard_api()
        for s in self.sessions.values():
            session_id = s.cookies.get('sid')
            try:
                self.delete("sessions/" + session_id)
            except Exception:
                pass

    def _get(self, url, params=None, attempts=0):
        params_str = self._dict_to_query_params(params)
        rsp = self.session.get(url + params_str)
        attempts += 1
        if self._check_response(rsp, attempts):
            return rsp
        else:
            return self._get(url, params, attempts)

    def get(self, path, params=None):
        return self._get(self.api_url + path, params)


    def _post(self, url, data=None, params=None, attempts=0):
        if data:
            data = json.dumps(data, cls=Serializer, separators=(',', ':'))
        params_str = self._dict_to_query_params(params)
        rsp = self.session.post(url + params_str, data=data)
        attempts += 1
        if self._check_response(rsp, attempts):
            return rsp
        else:
            return self._post(url, data, params, attempts)

    def post(self, path, data=None, params=None):
        return self._post(self.api_url + path, data, params)

    def _put(self, url, data=None, params=None, attempts=0):
        if data:
            data = json.dumps(data, cls=Serializer)
        params_str = self._dict_to_query_params(params)
        rsp = self.session.put(url + params_str, data=data)
        attempts += 1
        if self._check_response(rsp, attempts):
            return rsp
        else:
            return self._put(url, data, params, attempts)

    def put(self, path, data=None, params=None):
        return self._put(self.api_url + path, data, params)

    def _delete(self, url, params=None, attempts=0):
        params_str = self._dict_to_query_params(params)
        rsp = self.session.delete(url + params_str)
        attempts += 1
        if self._check_response(rsp, attempts):
            return rsp
        else:
            return self._delete(url, params, attempts)

    def delete(self, path, params=None):
        return self._delete(self.api_url + path, params)

    def _check_response(self, rsp, attempts=1):
        if rsp is None:
            raise ValueError("A response wasn't received")

        if 200 <= rsp.status_code < 300:
            return True

        # If we made it this far, we need to handle an exception
        if attempts >= self.max_attemps or rsp.status_code != 429:
            raise OktaError.factory(json.loads(rsp.text))

        # Assume we're going to retry with exponential backoff
        time.sleep(2 ** (attempts - 1))

        return False

    @staticmethod
    def _dict_to_query_params(d):
        if d is None or len(d) == 0:
            return ''

        param_list = [param + '=' + (str(value).lower() if type(value) == bool else str(value))
                      for param, value in six.iteritems(d) if value is not None]
        return '?' + "&".join(param_list)


class Serializer(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('dt(%Y-%m-%dT%H:%M:%SZ)')
        elif isinstance(obj, object):
            no_nulls = self._remove_nulls(obj.__dict__)
            formatted = self._replace_alt_names(obj, no_nulls)
            return formatted
        else:
            return json.JSONEncoder.default(self, obj)

    def _remove_nulls(self, d):
        built = {}
        for k, v in six.iteritems(d):
            if v is None:
                continue

            if isinstance(v, dict):
                built[k] = self._remove_nulls(v)

            if isinstance(v, object) and hasattr(v, '__dict__'):
                built[k] = self._remove_nulls(v.__dict__)

            else:
                built[k] = v
        return built

    def _replace_alt_names(self, d):
        built = d.copy()
        if hasattr(obj, 'alt_names'):
            for key, value in six.iteritems(obj.alt_names):
                if value in built:
                    built[key] = built[value]
                    del built[value]
        return built