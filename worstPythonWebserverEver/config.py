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
            config = yaml.load(rawconfig)
            rawconfig.close()
    except Exception as e:
        print("Exception was thrown while loading the config: {0}".format(e))
        exit(1)
    levels = [log.INFO, log.DEBUG]
    level = levels[min(len(levels)-1, args.debug)]
    log.basicConfig(level=level,
                    format="%(asctime)s %(levelname)s %(message)s")
    return args, config, log


if __name__ == '__main__':
    print("You are running this package incorrectly. RTFM.")
    exit(1)
