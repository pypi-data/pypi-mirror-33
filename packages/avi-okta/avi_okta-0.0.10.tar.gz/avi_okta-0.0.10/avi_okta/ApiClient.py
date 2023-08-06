import re
import time
import json
import backoff
import requests
from requests.exceptions import RequestException
from datetime import datetime
import avi_okta.OktaError as OktaError

API_PATH = '/api/v1/'
INTERNAL_API_PATH = '/api/internal/'
HOME_PATH = '/app/UserHome'
SESSION_COOKIE_PATH = '/login/sessionCookieRedirect'


def _failure_code(rsp):
    return rsp.status_code < 200 or rsp.status_code >= 300


def _fatal_code(e):
    if not e.response:
        return False
    return 400 <= e.response.status_code < 500


def _giveup_handler(details):
    rsp = details['value']
    raise OktaError.factory(json.loads(rsp.text))


class ApiClient(object):

    def __init__(self, base_url, token=None, username=None, password=None):
        if not token and not (username and password):
            raise ValueError('An API token or username and password are required')

        self.base_url = base_url
        self.api_url = base_url + API_PATH

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
        data = {
            'username':username,
            'password':password
        }
        rsp = self.post('authn', data=data)
        session_token = rsp.json()['sessionToken']

        # Trade session token for a session cookie and CSRF token
        params = {
            'token': session_token,
            'redirectUrl': base_url + HOME_PATH,
        }
        rsp = self.session.get(base_url + SESSION_COOKIE_PATH, params=params)
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

    @backoff.on_predicate(backoff.expo, _failure_code,
        max_tries=3,
        on_giveup=_giveup_handler
    )
    @backoff.on_exception(backoff.expo, RequestException,
        max_tries=3,
        giveup=_fatal_code
    )
    def get(self, path, params=None):
        url = self.api_url + path
        params = self._format_params(params)
        return self.session.get(url, params=params)


    @backoff.on_predicate(backoff.expo, _failure_code,
        max_tries=3,
        on_giveup=_giveup_handler
    )
    @backoff.on_exception(backoff.expo, RequestException,
        max_tries=3,
        giveup=_fatal_code
    )
    def post(self, path, data=None, params=None):
        url = self.api_url + path
        params = self._format_params(params)
        if data:
            data = json.dumps(data, cls=Serializer, separators=(',', ':'))
        return self.session.post(url, params=params, data=data)


    @backoff.on_predicate(backoff.expo, _failure_code,
        max_tries=3,
        on_giveup=_giveup_handler
    )
    @backoff.on_exception(backoff.expo, RequestException,
        max_tries=3,
        giveup=_fatal_code
    )
    def put(self, path, data=None, params=None):
        url = self.api_url + path
        params = self._format_params(params)
        if data:
            data = json.dumps(data, cls=Serializer)
        return self.session.put(url, params=params, data=data)


    @backoff.on_predicate(backoff.expo, _failure_code,
        max_tries=3,
        on_giveup=_giveup_handler
    )
    @backoff.on_exception(backoff.expo, RequestException,
        max_tries=3,
        giveup=_fatal_code
    )
    def delete(self, path, params=None):
        url = self.api_url + path
        params = self._format_params(params)
        return self.session.delete(url, params=params)

    @staticmethod
    def _format_params(params):
        if not params:
            return None
        formatted = {}
        for key, val in params.iteritems():
            if val is None:
                continue
            if type(val) == bool:
                val = str(val).lower()
            formatted[key] = val
        return formatted


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
        for k, v in d.iteritems():
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
            for key, value in obj.alt_names.iteritems():
                if value in built:
                    built[key] = built[value]
                    del built[value]
        return built