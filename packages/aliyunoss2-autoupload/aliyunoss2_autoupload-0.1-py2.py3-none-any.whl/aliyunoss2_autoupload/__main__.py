#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals, print_function

import argparse
import logging
import sys
from time import sleep, time

from marshmallow import ValidationError
from yaml import YAMLError

from . import conf
from . import glb
from . import version
from .performer import Performer

_parser = None  # type: argparse.ArgumentParser
_arguments = None  # type: argparse.Namespace


def parse_arguments(args=None):  # type:()->argparse.Namespace
    global _parser
    _parser = argparse.ArgumentParser(
        prog=version.NAME,
        description='Watch files in a directory and upload them to Aliyun OSS on file writing completed')
    _parser.add_argument(
        '--version', action='version',
        version='%(prog)s {0}'.format(version.__version__)
    )

    subparsers = _parser.add_subparsers(
        dest='sub_command',
        description='',
        help='<sub_command --help> Print the help of sub_commands'
    )

    parser_run = subparsers.add_parser(
        'run',
        help='Start to run then program. It will monitor and upload files continuously.')
    parser_run.add_argument(
        '--only-once', '-o', action='store_true',
        help='Upload only once, then exit. Will NOT monitor files. (default=%(default)s)'
    )
    parser_run.add_argument(
        '--config-file', '-c', type=str, default='',
        help='''The program configuration file.
        The program will first try to load configuration file by environment variable ${ALIYUNOSS2_AUTOUPLOAD_CONF}.
        If the environment variable not assigned, then try to load configuration file "conf/aliyunoss2-autoupload.yml"
        ''')
    parser_run.add_argument(
        '--logging-config-file', '-l', type=str, default='',
        help='''The logging configuration file.
        The program will first try to load logging configuration file by environment variable ${ALIYUNOSS2_AUTOUPLOAD_LOG_CONF}.
        If the environment variable not assigned, then try to load configuration file "conf/aliyunoss2-autoupload.log.yml"
        ''')

    parser_echo_config_sample = subparsers.add_parser(
        'echo_config_sample',
        help='Echo configure file sample')
    parser_echo_config_sample.add_argument(
        'config', type=str, choices=['prog', 'log'],
        help='Configure file to echo')

    global _arguments
    _arguments = _parser.parse_args(args)
    return _arguments


def main():
    if _arguments is None:
        parse_arguments(sys.argv[1:])

    if _arguments.sub_command == 'echo_config_sample':
        conf.print_config(_arguments.config)

    elif _arguments.sub_command == 'run':
        conf.load_logging_config(_arguments.logging_config_file)
        logger = get_logger()

        logger.info('-' * 60)
        logger.info('Starting')
        logger.info('-' * 60)

        initialed = False

        try:
            while True:
                ts = time()

                try:
                    conf.load_program_config(_arguments.config_file)
                except (YAMLError, ValidationError) as err:
                    err_msg = 'Invalid config file: {0}'.format(err)
                    print('-' * 60, file=sys.stderr)
                    print(err_msg, file=sys.stderr)
                    print('-' * 60, file=sys.stderr)
                    logger.fatal(err_msg)
                    sys.exit(1)
                else:
                    logger.info('configuration: %s', glb.config)

                if not initialed:
                    Performer.initial()
                    initialed = True
                Performer.run_once()

                if _arguments.only_once:
                    break

                interval = float(glb.config['watcher']['interval'])
                sleep_secs = interval - (time() - ts)
                if sleep_secs > 0:
                    sleep(sleep_secs)

        except KeyboardInterrupt:
            logger.warning('SIGINT')
        except Exception:
            logger.exception('')
            raise
        finally:
            if initialed:
                Performer.release()
            logger.info('=' * 60)
            logger.info('Stopped')
            logger.info('=' * 60)

    else:
        _parser.print_help()


def get_logger():
    return logging.getLogger(version.NAMESPACE)


if __name__ == '__main__':
    main()
