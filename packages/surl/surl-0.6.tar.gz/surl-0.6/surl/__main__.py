import argparse
import json
import os
import sys

import requests
import surl


def main():
    auth_dir = os.path.abspath(os.environ.get('SNAP_USER_COMMON', '.'))

    parser = argparse.ArgumentParser(
        description='S(tore)URL ...'
    )

    try:
        config, remainder = surl.get_config_from_cli(parser, auth_dir)
    except surl.CliError as e:
        print(e)
        return 1
    except surl.CliDone:
        return 0

    # Extra CLI options
    parser.add_argument('-v', '--debug', action='store_true',
                        help='Prints request and response headers')

    # Request options.
    parser.add_argument('-H', '--header', action="append",
                        default=[], dest='headers')
    parser.add_argument(
        '-X', '--method', default='GET',
        choices=['GET', 'PATCH', 'POST', 'PUT'])
    parser.add_argument('-d', '--data')

    parser.add_argument('url', nargs='?')

    args = parser.parse_args(remainder)

    if args.debug:
        # # The http.client logger pollutes stdout.
        # from http.client import HTTPConnection
        # HTTPConnection.debuglevel = 1
        import logging
        handler = requests.packages.urllib3.add_stderr_logger()
        handler.setFormatter(logging.Formatter('\033[1m%(message)s\033[0m'))

    authorization = surl.get_authorization_header(
        config.root, config.discharge)
    headers = surl.DEFAULT_HEADERS.copy()
    if args.url is None:
        url = '{}/dev/api/acl/verify/'.format(
            surl.CONSTANTS[config.store_env]['sca_base_url'])
        data = {'auth_data': {'authorization': authorization}}
        method = 'POST'
    else:
        url = args.url
        if args.data is not None:
            if args.data.startswith('@'):
                with open(os.path.expanduser(args.data[1:])) as fd:
                    data = json.load(fd)
            else:
                data = json.loads(args.data)
            method = args.method
            if args.method == 'GET':
                method = 'POST'
        else:
            data = None
            method = args.method
        headers.update({'Authorization': authorization})
        for h in args.headers:
            try:
                k, v = [t.strip() for t in h.split(':')]
            except ValueError:
                print('Invalid header: "{}"'.format(h))
                return 1
            headers[k] = v

    if args.debug:
        print('\033[1m******** request headers ********\033[0m',
              file=sys.stderr, flush=True)
        for k, v in headers.items():
            print('{}: {}'.format(k, v), file=sys.stderr, flush=True)
        print('\033[1m**********************************\033[0m',
              file=sys.stderr, flush=True)

    response = requests.request(
        url=url, method=method, json=data, headers=headers, stream=True)

    # Refresh discharge if necessary.
    if response.headers.get('WWW-Authenticate') == (
            'Macaroon needs_refresh=1'):
        discharge = surl.get_refreshed_discharge(
            config.discharge, config.store_env)
        config = surl.StoreClientConfig(
            root=config.root, discharge=discharge, store_env=config.store_env,
            path=config.path)
        surl.save_config(config)
        headers.update(
            {'Authorization': surl.get_authorization_header(
                config.root, config.discharge)})
        response = requests.request(
            url=url, method=method, json=data, headers=headers, stream=True)

    if args.debug:
        print('\033[1m******** response headers ********\033[0m',
              file=sys.stderr, flush=True)
        print('HTTP/1.1 {} {}'.format(response.status_code, response.reason),
              file=sys.stderr, flush=True)
        for k, v in response.headers.items():
            print('{}: {}'.format(k, v), file=sys.stderr, flush=True)
        print('\033[1m**********************************\033[0m',
              file=sys.stderr, flush=True)

    for chunk in response.iter_content(chunk_size=1024 * 8):
        if chunk:
            sys.stdout.buffer.write(chunk)

    # Flush STDOUT carefully, because PIPE might be broken.
    def _noop(*args, **kwargs):
        pass

    try:
        sys.stdout.buffer.flush()
    except (BrokenPipeError, IOError):
        sys.stdout.write = _noop
        sys.stdout.flush = _noop
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
