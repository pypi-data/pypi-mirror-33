# -*- coding: utf-8 -*-

"""
cloudcix.auth
~~~~~~~~~~~~~

This module implements the CloudCIX API Client Authentications
"""

import json
from keystoneclient import (
    access,
    exceptions,
    utils,
)
from keystoneclient.auth.identity.v3 import AuthMethod, Auth
from keystoneclient.i18n import _
import logging
from oslo_config import cfg
import requests

from cloudcix.conf import settings

_logger = logging.getLogger(__name__)


class TokenAuth(requests.auth.AuthBase):
    """
    CloudCIX Token-based authentication
    """

    def __init__(self, token: str):
        self.token = token

    def __call__(self, request):
        request.headers['X-Auth-Token'] = self.token
        return request

    def __eq__(self, other: object):
        return self.token == other.token


class AdminSession:
    """
    Requests wrapper for Keystone authentication using cloudcix credentials
    """

    def __init__(self):
        self.headers = {'content-type': 'application/json'}
        self.auth_url = settings.CLOUDCIX_AUTH_URL
        self.username = settings.CLOUDCIX_API_USERNAME
        self.password = settings.CLOUDCIX_API_PASSWORD
        self.domain = settings.CLOUDCIX_API_KEY

    def get_token(self, **kwargs):
        kwargs['headers'] = self.headers
        response = requests.post(
            self.token_url,
            data=json.dumps(self.data),
            **kwargs,
        )
        if response.status_code < 400:
            return response.headers['X-Subject-Token']
        # TODO: not sure if should return entire response, False, or status?
        return response

    @property
    def token_url(self):
        return '{}/auth/tokens'.format(self.auth_url)

    @property
    def data(self):
        return {
            'auth': {
                'identity': {
                    'methods': ['password'],
                    'password': {
                        'user': {
                            'name': self.username,
                            'password': self.password,
                            'domain': {
                                'id': self.domain,
                            },
                        },
                    },
                },
            },
        }


class ActiveDirectoryAuth:
    """
    Provides authentication for active directory backends into CloudCIX

    TODO: Deprecate or migrate to v0.3+ of python-cloudcix
    """

    def __init__(self):
        raise NotImplemented


class CloudCIXAuthMethod(AuthMethod):

    _method_parameters = ['username', 'password', 'id_member', 'token_id']

    def get_auth_data(self, session, auth, headers, **kwargs):
        if self.token_id:
            auth_data = {'token':  {'id': self.token_id}}
        else:
            auth_data = {'name': self.username, 'password': self.password}
        if self.id_member:
            auth_data['domain'] = {'id': self.id_member}
        return 'password', {'user': auth_data}


class CloudCIXAuth(Auth):

    _auth_method_class = CloudCIXAuthMethod

    @utils.positional()
    def __init__(
            self,
            auth_url,
            username=None,
            password=None,
            id_member=None,
            scope=None,
            token_id=None,
            reauthenticate=True):
        super(Auth, self).__init__(
            auth_url=auth_url,
            reauthenticate=reauthenticate)
        self._auth_method = self._auth_method_class(
            username=username,
            password=password,
            id_member=id_member,
            token_id=token_id)
        self.id_member = id_member
        self.scope = scope
        self.members = []
        self.token_id = None

    def get_auth_ref(self, session, **kwargs):
        headers = {'Accept': 'application/json'}
        body = {'auth': {'identity': {}}}
        ident = body['auth']['identity']
        rkwargs = {}

        for method in self.auth_methods:
            name, auth_data = method.get_auth_data(
                session,
                self,
                headers,
                request_kwargs=rkwargs)
            ident.setdefault('methods', []).append(name)
            ident[name] = auth_data

        if not ident:
            raise exceptions.AuthenticationRequired(_(
                'Authentication method required (i.e. password)'))

        if self.scope:
            body['auth']['scope'] = self.scope

        _logger.info(
            'Making authentication request to {}'.format(self.token_url))
        try:
            resp = session.post(
                self.token_url,
                json=body,
                headers=headers,
                authenticated=False,
                log=False,
                **rkwargs)
        except exceptions.HTTPError as e:
            try:
                resp = e.response.json()['error']['identity']['password']
            except (KeyError, ValueError):
                pass
            else:
                self.members = resp['members']
                self.token_id = resp['token']['id']
            finally:
                raise e

        try:
            resp_data = resp.json()['token']
        except (KeyError, ValueError):
            raise exceptions.InvalidResponse(response=resp)
        else:
            self.members = []
            self.token_id = None
        finally:
            return access.AccessInfoV3(
                resp.headers['X-Subject-Token'],
                **resp_data)

    @property
    def additional_auth_required(self):
        return self.token_id and self.members

    @property
    def auth_methods(self):
        return [self._auth_method]

    def select_account(self, id_member):
        id_member = str(id_member)
        assert id_member in [m['id_member'] for m in self.members]
        self.id_member = str(id_member)
        self._auth_method.token_id = self.token_id
        self._auth_method.id_member = id_member

    @classmethod
    def get_options(cls):
        options = super(Auth, cls).get_options()
        options.extend([
            cfg.StrOpt('username', help='Username'),
            cfg.StrOpt('password', secret=True, help='User\'s Password'),
            cfg.StrOpt('id_member', help='ID of the User\'s Member'),
            cfg.StrOpt(
                'scope',
                help='Dict containing a scope for this auth request',
            ),
        ])
        return options
