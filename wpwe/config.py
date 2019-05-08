#!/usr/bin/env python3


def main():
    import yaml
    import argparse
    import logging as log
    parser = argparse.ArgumentParser(description="RTFM")
    parser.add_argument('-d', '--debug', action='count', default=0,
                        help='Increases to DEBUG logging')
    parser.add_argument('-c', '--config', type=str, default='./config.yaml',
                        help="Absolute path to the config")
    args = parser.parse_args()
    try:
        with open(args.config, 'r') as rawconfig:
            loadedConfig = yaml.load(rawconfig)
            rawconfig.close()
    except Exception:
        loadedConfig = {}
    levels = [log.INFO, log.DEBUG]
    level = levels[min(len(levels)-1, args.debug)]
    log.basicConfig(level=level,
                    format="%(asctime)s %(levelname)s %(message)s")
    config = configOveride(loadedConfig)
    return args, config, log


def configOveride(loadedConfig):
    import os
    codedDefaults = {'server_ipv4': '0.0.0.0', 'server_port': 80,
                     'access_log_path': '/var/log/wpwe/access.log',
                     'error_log_path': '/var/log/wpwe/error.log',
                     'methods': ['HEAD', 'GET', 'OPTIONS'],
                     'server_name': 'localhost', 'user': 'wpwe-data',
                     'webroot': '/var/www/html',
                     'custom_error_pages': False,
                     'default_indexes': ['index.html', 'index.htm',
                                         'index.txt'],
                     'error_pages': {403: 'docs/403.html',
                                     404: 'docs/404.html',
                                     405: 'docs/405.html',
                                     500: 'docs/500.html'},
                     'listen_mode': False,
                     'file_ext': ['html', 'htm', 'png', 'txt',
                                  'jpeg', 'jpg', 'gif', 'css']}
    mypath = os.path.dirname(os.path.realpath(__file__))
    # Set some defaults that a user cant override
    for k in loadedConfig.keys():
        codedDefaults[k] = loadedConfig[k]
    codedDefaults['server_working_dir'] = mypath
    return codedDefaults


if __name__ == '__main__':
    print("You are running this package incorrectly. RTFM.")
    exit(1)
