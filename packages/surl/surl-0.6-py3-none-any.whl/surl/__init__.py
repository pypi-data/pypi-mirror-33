
import datetime
import getpass
import json
import os
import sys

from collections import namedtuple
import requests
from pymacaroons import Macaroon


name = 'surl'

__all__ = [
    'ClientConfig',
    'ConfigError',
    'CliError',
    'CliDone',
    'get_config_from_cli',
    'get_store_authorization',
    'get_authorization_header',
    'get_refreshed_discharge',
]


DEFAULT_HEADERS = {
    'User-Agent': 'surl/{}'.format(os.environ.get('SNAP_VERSION', 'devel')),
    'Accept': 'application/json, application/hal+json',
    'Content-Type': 'application/json',
    'Cache-Control': 'no-cache',
}

CONSTANTS = {
    'local': {
        'sso_location': os.environ.get(
            'SURL_SSO_LOCATION',
            'login.staging.ubuntu.com'),
        'sso_base_url': os.environ.get(
            'SURL_SSO_BASE_URL',
            'https://login.staging.ubuntu.com'),
        'sca_base_url': os.environ.get(
            'SURL_SCA_BASE_URL',
            'http://0.0.0.0:8000'),
    },
    'staging': {
        'sso_location': 'login.staging.ubuntu.com',
        'sso_base_url': 'https://login.staging.ubuntu.com',
        'sca_base_url': os.environ.get(
            'SURL_SCA_ROOT_URL', 'https://dashboard.staging.snapcraft.io'),
    },
    'production': {
        'sso_location': 'login.ubuntu.com',
        'sso_base_url': 'https://login.ubuntu.com',
        'sca_base_url': 'https://dashboard.snapcraft.io',
    },
}


class ConfigError(Exception):
    pass


class CliError(Exception):
    pass


class CliDone(Exception):
    pass


ClientConfig = namedtuple(
    'ClientConfig',
    ['root', 'discharge', 'store_env', 'path']
)


def load_config(path):
    with open(path) as fd:
        try:
            a = json.load(fd)
            root, discharge, store_env = (
                a['root'], a['discharge'], a['store'])
        except json.decoder.JSONDecodeError:
            raise ConfigError()
    return ClientConfig(
        root=root, discharge=discharge, store_env=store_env, path=path)


def save_config(config):
    payload = {
        'root': config.root,
        'discharge': config.discharge,
        'store': config.store_env,
    }
    with open(config.path, 'w') as fd:
        json.dump(payload, fd, indent=2)


def list_configs(path):
    candidates = [f for f in os.listdir(path) if f.endswith('.surl')]
    for f in candidates:
        try:
            config = load_config(os.path.join(path, f))
        except ConfigError:
            continue
        ident = f.replace('.surl', '')
        yield ident, config.store_env


def get_config_from_cli(parser, auth_dir):

    # Auxiliary options.
    parser.add_argument(
        '--version', action='version',
        version='surl "{}"'.format(os.environ.get('SNAP_VERSION', 'devel')))
    parser.add_argument(
        '-l', '--list-auth', action='store_true',
        help='List stored authorizations..')

    # Credential options.
    parser.add_argument(
        '-a', '--auth', metavar='IDENT',
        help='Authorization identifier (saving or reading).')
    parser.add_argument(
        '--force', action='store_true',
        help='Force re-authorization and overrides saved information.')
    parser.add_argument(
        '-e', '--email', default=os.environ.get('STORE_EMAIL'))
    parser.add_argument(
        '-s', '--store', default=os.environ.get('STORE_ENV', 'staging'),
        choices=['staging', 'production', 'local'])

    # Macarroon restricting options.
    parser.add_argument(
        '-p', '--permission', action="append", dest='permissions',
        choices=[
            'edit_account',
            'modify_account_key',
            'package_access',
            'package_manage',
            'package_metrics',
            'package_push',
            'package_purchase',
            'package_register',
            'package_release',
            'package_update',
            'package_upload',
            'package_upload_request',
            'store_admin',
            'store_review',
        ])
    parser.add_argument(
        '-c', '--channel', action="append", dest='channels',
        choices=['stable', 'candidate', 'beta', 'edge'])

    args, remainder = parser.parse_known_args()

    if args.list_auth:
        print('Available credendials:')
        for ident, store_env in list_configs(auth_dir):
            print('  {} ({})'.format(ident, store_env))
        raise CliDone()

    if args.auth:
        auth_path = os.path.join(auth_dir, args.auth + '.surl')
        legacy_path = os.path.join(auth_dir, args.auth)
        if os.path.exists(legacy_path):
            os.rename(legacy_path, auth_path)
        auth_exists = os.path.exists(auth_path)
    else:
        auth_path = None
        auth_exists = False

    if auth_exists and not args.force:
        try:
            config = load_config(auth_path)
        except ConfigError:
            raise CliError(
                '** Deprecated or Broken authentication file, '
                'please delete it and login again:\n  $ rm {}'
                .format(auth_path))

        return config, remainder

    store_env = args.store
    if args.email is None:
        raise CliError('Needs "-e <email>" or $STORE_EMAIL.')
    try:
        root, discharge = get_store_authorization(
            args.email, permissions=args.permissions,
            channels=args.channels, store_env=store_env)
    except Exception as e:
        raise CliError('Authorization failed! Double-check password and 2FA.')

    config = ClientConfig(
        root=root, discharge=discharge, store_env=store_env, path=auth_path)

    if auth_path is not None:
        save_config(config)

    return config, remainder


def get_store_authorization(
        email, permissions=None, channels=None, store_env=None):
    """Return the serialised root and discharge macaroon.

    Get a permissions macaroon from SCA and discharge it in SSO.
    """
    headers = DEFAULT_HEADERS.copy()
    # Request a SCA root macaroon with hard expiration in 180 days.
    sca_data = {
        'permissions': permissions or ['package_access'],
        'expires': (
            datetime.date.today() + datetime.timedelta(days=180)
            ).strftime('%Y-%m-%d 00:00:00')
    }
    if channels:
        sca_data.update({
            'channels': channels
        })
    response = requests.request(
        url='{}/dev/api/acl/'.format(CONSTANTS[store_env]['sca_base_url']),
        method='POST', json=sca_data, headers=headers)
    root = response.json()['macaroon']

    caveat, = [
        c for c in Macaroon.deserialize(root).third_party_caveats()
        if c.location == CONSTANTS[store_env]['sso_location']
    ]
    # Request a SSO discharge macaroon.
    sso_data = {
        'email': email,
        'password': getpass.getpass('Password for {}: '.format(email)),
        'caveat_id': caveat.caveat_id,
    }
    response = requests.request(
        url='{}/api/v2/tokens/discharge'.format(
            CONSTANTS[store_env]['sso_base_url']),
        method='POST', json=sso_data, headers=headers)
    # OTP/2FA is optional.
    if (response.status_code == 401 and
            response.json().get('code') == 'TWOFACTOR_REQUIRED'):
        sys.stderr.write('Second-factor auth for {}: '.format(store_env))
        sso_data.update({'otp': input()})
        response = requests.request(
            url='{}/api/v2/tokens/discharge'.format(
                CONSTANTS[store_env]['sso_base_url']),
            method='POST', json=sso_data, headers=headers)
    discharge = response.json()['discharge_macaroon']

    return root, discharge


def get_authorization_header(root, discharge):
    """Bind root and discharge returning the authorization header."""
    bound = Macaroon.deserialize(root).prepare_for_request(
        Macaroon.deserialize(discharge))

    return 'Macaroon root={}, discharge={}'.format(root, bound.serialize())


def get_refreshed_discharge(discharge, store_env):
    headers = DEFAULT_HEADERS.copy()
    data = {'discharge_macaroon': discharge}
    response = requests.request(
        url='{}/api/v2/tokens/refresh'.format(
            CONSTANTS[store_env]['sso_base_url']),
        method='POST', json=data, headers=headers)
    return response.json()['discharge_macaroon']
