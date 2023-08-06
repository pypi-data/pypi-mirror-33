import os
import time
import json
import jinja2
import avi_okta.OktaError as OktaError
from avi_okta.ApiClient import ApiClient

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates")
BASE_URL = "https://avinetworks.oktapreview.com"


class AviOktaClient(ApiClient):
    def __init__(self, token=None, username=None, password=None):
        super(AviOktaClient, self).__init__(
            base_url=BASE_URL,
            token=token,
            username=username,
            password=password
        )
        self.jinja2_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
            trim_blocks=True,
        )

    ### Applications ###
    def create_app(self, label, subdomain=None):
        try:
            app = self.get_app(label=label)
            app['_created'] = False
            return app
        except OktaError.NotFound:
            pass

        template = self.jinja2_env.get_template("app.template")
        variables = {
            "label": label,
            "subdomain": subdomain or label,
        }
        data = json.loads(template.render(variables))
        rsp = self.post('apps', data=data)
        app = rsp.json()
        app['_created'] = True

        template = self.jinja2_env.get_template("app_schema.template")
        data = json.loads(template.render())
        rsp = self.post('meta/schemas/apps/%s/default' % app['id'], data=data)
        return app

    def get_app(self, app_id=None, label=None):
        if app_id:
            rsp = self.get('apps/%s' % app_id)
            return rsp.json()
        apps = self.list_apps()
        for app in apps:
            if app['label'] == label:
                return app
        raise OktaError.factory({
            "errorCode": OktaError.NOT_FOUND,
            "errorSummary": "Not found: Resource not found: %s (AppInstance)" % label
        })

    def get_app_schema(self, app_id):
        rsp = self.get('meta/schemas/apps/%s/default' % app_id)
        return rsp.json()

    def get_app_metadata(self, app_id):
        rsp = self.get('apps/%s/sso/saml/metadata' % app_id)
        return rsp.content

    def list_app_users(self, app_id):
        rsp = self.get('apps/%s/users' % app_id)
        return rsp.json()

    def list_apps(self):
        rsp = self.get('apps')
        return rsp.json()

    def delete_app(self, app_id):
        self.deactivate_app(app_id)
        rsp = self.delete('apps/%s' % app_id)
        return rsp.status_code

    def deactivate_app(self, app_id):
        rsp = self.post('apps/%s/lifecycle/deactivate' % app_id)
        return rsp.status_code

    def assign_group_to_app(self, app_id, group_id):
        rsp = self.put('apps/%s/groups/%s' % (app_id, group_id))
        return rsp.json()

    def assign_user_to_app(self, app_id, user_id, attributes={}):
        user_login = self.get_user(user_id=user_id)['profile']['login']
        template = self.jinja2_env.get_template("app_user.template")
        variables = {
            "user_id": user_id,
            "username": user_login,
            "attributes": attributes,
        }
        data = json.loads(template.render(variables))
        rsp = self.post('apps/%s/users' % app_id, data=data)
        return rsp.json()

    def update_app_user_profile(self, app_id, user_id, attributes={}):
        template = self.jinja2_env.get_template("app_user.template")
        variables = {
            "attributes": attributes,
        }
        data = json.loads(template.render(variables))
        rsp = self.post('apps/%s/users/%s' % (app_id, user_id), data=data)
        return rsp.json()

    ### Users ###
    def create_user(self, first_name, last_name, email, organization=None,
            password=None, group_ids=[], activate=True):
        try:
            user = self.get_user(login=email)
            if group_ids:
                current_groups = self.get_user_groups(user['id'])
                current_group_ids = [g['id'] for g in current_groups]
                for group_id in group_ids:
                    if group_id not in current_group_ids:
                        self.assign_user_to_group(user['id'], group_id)
            user['_created'] = False
            return user
        except OktaError.NotFound:
            pass

        template = self.jinja2_env.get_template("user.template")
        variables = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'organization': organization,
            'password': password,
            'group_ids': group_ids,
        }
        data = json.loads(template.render(variables))
        rsp = self.post('users', data=data, params={'activate': activate})
        user = rsp.json()
        user['_created'] = True
        return user

    def get_user(self, user_id=None, login=None):
        identifier = user_id or login
        rsp = self.get('users/%s' % identifier)
        return rsp.json()

    def get_user_groups(self, user_id):
        rsp = self.get('users/%s/groups' % user_id)
        return rsp.json()

    def list_users(self):
        rsp = self.get('users')
        return rsp.json()

    def delete_user(self, user_id):
        self.deactivate_user(user_id=user_id)
        rsp = self.delete('users/%s' % user_id)
        return rsp.status_code

    def activate_user(self, user_id, send_email=False):
        params = {'sendEmail': send_email}
        try:
            rsp = self.post('users/%s/lifecycle/activate' % user_id, params=params)
            return rsp.json()
        except OktaError.UserAlreadyActivated:
            return None

    def deactivate_user(self, user_id):
        rsp = self.post('users/%s/lifecycle/deactivate' % user_id)
        return rsp.status_code

    def expire_user_password(self, user_id):
        rsp = self.post('users/%s/lifecycle/expire_password' % user_id)
        return rsp.status_code

    def assign_group_admin_role_to_user(self, user_id, group_id):
        try:
            data = {'type': 'USER_ADMIN'}
            rsp = self.post('users/%s/roles' % user_id, data=data)
            role = rsp.json()
        except OktaError.RoleAlreadyAssigned:
            rsp = self.get('users/%s/roles' % user_id)
            roles = rsp.json()
            for r in roles:
                if r['type'] == 'USER_ADMIN':
                    role = r
        rsp = self.put('users/%s/roles/%s/targets/groups/%s' %
                (user_id, role['id'], group_id))
        return rsp.status_code

    ### Groups ###
    def create_group(self, name):
        try:
            group = self.get_group(name=name)
            group['_created'] = False
            return group
        except OktaError.NotFound:
            pass

        template = self.jinja2_env.get_template("group.template")
        variables = {
            'name': name,
        }
        data = json.loads(template.render(variables))
        rsp = self.post('groups', data=data)
        group = rsp.json()
        group['_created'] = True
        return group

    def get_group(self, group_id=None, name=None):
        if group_id:
            rsp = self.get('groups/%s' % group_id)
            return rsp.json()
        rsp = self.get('groups', params={'q': name})
        groups = rsp.json()
        if groups:
            return groups[0]
        raise OktaError.factory({
            "errorCode": OktaError.NOT_FOUND,
            "errorSummary": "Not found: Resource not found: %s (UserGroup)" % name
        })

    def get_group_users(self, group_id):
        rsp = self.get("groups/%s/users" % group_id)
        return rsp.json()

    def list_groups(self):
        rsp = self.get('groups')
        return rsp.json()

    def delete_group(self, group_id):
        rsp = self.delete('groups/%s' % group_id)
        return rsp.status_code

    def assign_user_to_group(self, user_id, group_id):
        rsp = self.put('groups/%s/users/%s' % (group_id, user_id))
        return rsp.status_code

    ### Trusted Origins ###
    def create_trusted_origin(self, name, origin, cors=True, redirect=True):
        try:
            trusted_origin = self.get_trusted_origin(name=name)
            trusted_origin['_created'] = False
            return trusted_origin
        except OktaError.NotFound:
            pass

        scopes = []
        if cors:
            scopes.append('CORS')
        if redirect:
            scopes.append('REDIRECT')
        template = self.jinja2_env.get_template("trusted_origin.template")
        variables = {
            'name': name,
            'origin': origin,
            'scopes': scopes,
        }
        data = json.loads(template.render(variables))
        rsp = self.post('trustedOrigins', data=data)
        trusted_origin = rsp.json()
        trusted_origin['_created'] = True
        return trusted_origin

    def get_trusted_origin(self, trusted_origin_id=None, name=None):
        if trusted_origin_id:
            rsp = self.get('trustedOrigins/%s' % trusted_origin_id)
            return rsp.json()
        trusted_origins = self.list_trusted_origins()
        for trusted_origin in trusted_origins:
            if trusted_origin['name'] == name:
                return trusted_origin
        raise OktaError.factory({
            "errorCode": OktaError.NOT_FOUND,
            "errorSummary": "Not found: Resource not found: %s (TrustedOrigin)" % name
        })

    def list_trusted_origins(self):
        rsp = self.get('trustedOrigins')
        return rsp.json()

    def delete_trusted_origin(self, trusted_origin_id):
        self.deactivate_trusted_origin(trusted_origin_id)
        rsp = self.delete('trustedOrigins/%s' % trusted_origin_id)
        return rsp.status_code

    def deactivate_trusted_origin(self, trusted_origin_id):
        rsp = self.post('trustedOrigins/%s/lifecycle/deactivate' % trusted_origin_id)
        return rsp.status_code

    ### API Tokens ###
    def create_token(self, name):
        try:
            token = self.get_token(name=name)
            token['_created'] = False
            return token
        except OktaError.NotFound:
            pass

        try:
            self.target_internal_api()
            rsp = self.post('tokens', data={'name': name})
            token = rsp.json()
            token['_created'] = True
            return token
        finally:
            self.target_standard_api()

    def get_token(self, token_id=None, name=None):
        try:
            self.target_internal_api()
            if token_id:
                rsp = self.get('tokens/%s' % token_id)
                return rsp.json()
            tokens = self.list_tokens()
            for token in tokens:
                if token['name'] == name:
                    return token
            raise OktaError.factory({
                "errorCode": OktaError.NOT_FOUND,
                "errorSummary": "Not found: Resource not found: %s (Token)" % name
            })
        finally:
            self.target_standard_api()

    def list_tokens(self):
        try:
            self.target_internal_api()
            rsp = self.get('tokens')
            return rsp.json()
        finally:
            self.target_standard_api()

    def delete_token(self, token_id):
        try:
            self.target_internal_api()
            rsp = self.post("tokens/%s/revoke" % token_id)
            return rsp.status_code
        finally:
            self.target_standard_api()
