# Copyright 2017 StreamSets Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module works in unison with environments.yaml file to provide a YAML driven subprocess command execution for
environments. High level points to understand how this module and environments.yaml work together:
    1.  The built in environments.yaml can be over-ridden with user provided one (via --environments-yaml-file option).
        The user provided one does not supercede the built in one but instead it overrides matching YAML keys.
    2.  Once command line args (args/arg_items) and YAML have been parsed (config_defaults from YAML's 'defaults' key),
        these 2 dicts of arguments are used for substitution in any command string. The order is that args
        replacement happens before config_defaults replacement.
    3.  YAML parsing (load) at this time does not support list merges. We support this by way of our own custom
        convention. Please look into environments.yaml file for a description of usage.
    4.  environments.yaml is laid out as a dict of environments with `start` and `stop` commands.
        Additionally we support `environment_start` and `environment_stop` lists which are executed before and after
        an environment starts and stops respectively.
"""

import argparse
import importlib
import json
import logging
import os
import textwrap
from string import ascii_letters, Formatter

import docker
import yaml

from .utils import get_random_string, infinitedict, yaml_merge_collections


class ArgumentHybridFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass


FORMATTER_CLASS = ArgumentHybridFormatter

# Note that while we use a `logging.Logger` instance throughout (to make tracing easier),
# we set the logging level on the root logger based on whether -v/--verbose is passed.
logger = logging.getLogger(__name__)

client = docker.from_env()


def main():
    # To prevent a -h argument from halting parsing prematurely, we disable
    # help in the parser, but then add it manually after parse_known_args is run.
    parser = argparse.ArgumentParser(formatter_class=FORMATTER_CLASS, add_help=False)
    parser.add_argument('-e', '--environments-yaml-file', metavar='file', help='Use custom environments YAML file')
    parser.add_argument('-n', '--docker-network', metavar='nw', help='Docker network to use', default='cluster')
    parser.add_argument('-c', '--testenvironments-config-directory', metavar='dir',
                        help='Testenvironments config directory',
                        default=os.path.realpath(os.path.expanduser('~/.streamsets/testenvironments')))
    parser.add_argument('-v', '--verbose', action='store_true', help='Be noisier')

    # Parse known args the first time to set the logger level early on. Note that
    # argparse.ArgumentParser.parse_known_args returns a tuple where the first element is a
    # Namespace.
    args, unknown_args = parser.parse_known_args()
    logging.getLogger().setLevel(logging.DEBUG if args.verbose else logging.INFO)

    with open(os.path.join(os.path.dirname(__file__), 'environments.yaml')) as defaults_file:
        logger.debug('Reading default environments.yaml file ...')
        environment_configs = yaml.load(defaults_file.read())

    if args.environments_yaml_file:
        with open(os.path.realpath(args.environments_yaml_file)) as custom_environments_file:
            logger.debug('Reading custom environments file from %s ...',
                         os.path.realpath(args.environments_yaml_file))
            custom_env_configs = yaml.load(custom_environments_file.read())

        new_env_configs = infinitedict()
        new_env_configs.update(environment_configs)
        # pop 'args' so as to not apply for entire 'defaults' update
        new_env_configs['defaults']['args'] = {}
        new_env_configs['defaults']['args'].update(custom_env_configs.get('defaults', {}).pop('args', {}))
        new_env_configs['defaults'].update(custom_env_configs.get('defaults', {}))
        new_env_configs['environments'].update(custom_env_configs.get('environments', {}))
        if 'environment_start' in custom_env_configs:
            new_env_configs['environment_start'] = custom_env_configs.get('environment_start')
        if 'environment_stop' in custom_env_configs:
            new_env_configs['environment_stop'] = custom_env_configs.get('environment_stop')
        environment_configs = new_env_configs

    # Why merge wont work without this? STF-508 to investigate and resolve.
    environment_configs = json.loads(json.dumps(environment_configs))
    yaml_merge_collections(environment_configs)

    config_arg_defaults = environment_configs.get('defaults', {}).get('args', {})
    config_defaults = environment_configs.get('defaults', {})
    config_defaults.pop('args', None)
    config_environments = environment_configs.get('environments', {})
    start_environments = [name for name, environment in config_environments.items() if 'start' in environment]
    stop_environments = [name for name, environment in config_environments.items() if 'stop' in environment]
    print_environments = ('''
        StreamSets Test Environments (STE): Spin Test Environments

        Applicable environments
        -----------------------
        {}
    ''').format('\n        '.join(environment for environment in sorted(config_environments.keys())))
    print_start_environments = ('''
        StreamSets Test Environments (STE): Spin Test Environments

        Applicable start environments
        -----------------------------
        {}
    ''').format('\n        '.join(sorted(start_environments)))
    print_stop_environments = ('''
        StreamSets Test Environments (STE): Spin Test Environments

        Applicable stop environments
        ----------------------------
        {}
    ''').format('\n        '.join(sorted(stop_environments)))

    parser.description = textwrap.dedent(print_environments)

    # Since some actions (e.g. start, stop) have command line interfaces, we
    # parse what's available so far to get that environment's name.
    action_subparsers = parser.add_subparsers(dest='action')

    # Start by creating parsers for each action we support (i.e. start, stop). We also
    # add the minimum arguments needed by the parser to function (e.g. for the start action,
    # we need to know the environment to be able to load the correct environment configs).

    # Show this help only if its a 'start' and not a 'start' with environment
    show_help = 'start' in unknown_args and not [arg for arg in unknown_args if arg in start_environments]
    start_parser = action_subparsers.add_parser('start', formatter_class=FORMATTER_CLASS,
                                                add_help=show_help,
                                                description=textwrap.dedent(print_start_environments))
    start_parser.add_argument('environment', help='Environment to start')
    start_parser.add_argument('--dry-run', action='store_true', help="Don't actually perform actions")

    # Show this help only if its a 'stop' and not a 'stop' with environment
    show_help = 'stop' in unknown_args and not [arg for arg in unknown_args if arg in stop_environments]
    stop_parser = action_subparsers.add_parser('stop', formatter_class=FORMATTER_CLASS,
                                               add_help=show_help,
                                               description=textwrap.dedent(print_stop_environments))
    stop_parser.add_argument('environment', help='Environment to stop')
    stop_parser.add_argument('--dry-run', action='store_true', help="Don't actually perform actions")

    # Parse known args the second time to figure out which action the user wants to do and,
    # if it supports it, which environment to use.
    args, unknown_args = parser.parse_known_args()

    # We can now add a -h/--help argument to the top-level parser without affecting the ability to
    # get help once an environment is selected.
    _add_help(parser)

    if hasattr(args, 'environment'):
        config_environment = config_environments.get(args.environment, {})
        environment_args = config_environment.get('args', {})
        default_args = {arg_name: arg_parameters for arg_name, arg_parameters in config_arg_defaults.items()
                        if arg_name not in environment_args.keys()}

        # Start parser
        # ~~~~~~~~~~~~
        applicable_start_environment_args = _get_applicable_arguments(config_environment.get('start', []), vars(args),
                                                                      default_args, config_defaults, environment_args)
        start_environment_args = {arg_name: arg_parameter for arg_name, arg_parameter in environment_args.items()
                                  if (arg_name[2:] if arg_name.startswith('--') else arg_name)
                                  in applicable_start_environment_args}
        start_parser.description = '\n'.join(['Start {} environment'.format(args.environment),
                                              config_environment.get('start_help', '')])
        _add_help(start_parser)
        _add_group_args('Default', default_args, start_parser)
        _add_group_args(args.environment, start_environment_args, start_parser)

        # Stop parser
        # ~~~~~~~~~~~
        applicable_stop_environment_args = _get_applicable_arguments(config_environment.get('stop', []), vars(args),
                                                                     default_args, config_defaults, environment_args)
        stop_environment_args = {arg_name: arg_parameter for arg_name, arg_parameter in environment_args.items()
                                 if (arg_name[2:] if arg_name.startswith('--') else arg_name)
                                 in applicable_stop_environment_args}
        stop_parser.description = '\n'.join(['Stop {} environment'.format(args.environment),
                                             config_environment.get('stop_help', '')])
        _add_help(stop_parser)
        _add_group_args('Default', default_args, stop_parser)
        _add_group_args(args.environment, stop_environment_args, stop_parser)

    args = parser.parse_args()
    logger.debug('Parsed args (%s).', '; '.join('{}="{}"'.format(k, v) for k, v in vars(args).items()))

    if not args.action:
        parser.print_help()
        parser.exit()

    try:
        # Check for whether the Docker network we need exists already, creating it if it doesn't.
        client.networks.create(name=args.docker_network, driver='bridge', check_duplicate=True)
        logger.debug('Successfully created network (%s).', args.docker_network)
    except docker.errors.APIError as api_error:
        if api_error.explanation == 'network with name {} already exists'.format(args.docker_network):
            logger.debug('Network (%s) already exists. Continuing without creating ...', args.docker_network)
        else:
            raise

    logger.debug('Creating (%s) STE config directory if it does not exist ...', args.testenvironments_config_directory)
    if not os.path.exists(os.path.realpath(os.path.expanduser(args.testenvironments_config_directory))):
        os.makedirs(os.path.realpath(os.path.expanduser(args.testenvironments_config_directory)))

    action = importlib.import_module('streamsets.testenvironments.actions.{}'.format(args.action))
    arg_items = vars(args)
    arg_items['random-name'] = get_random_string(ascii_letters, 10)
    action.main(environment_configs, args.environment, config_environment, arg_items, config_defaults)


def _get_applicable_arguments(commands, args, default_args, config_defaults, environment_args):
    """Give a list of commands, return a set of applicable arguments for those commands.

    Args:
        commands (:obj:`list`): List of commands.
        args (:obj:`dict`): Top level command line arguments. Arguments have _ (e.g., docker_network)
        default_args (:obj:`dict`): Arguments of `defaults` minus environment args
        config_defaults (:obj:`dict`): `defaults` of environments.yaml file.
        environment_args (:obj:`dict`): Arguments of an environment. Arguments are typically prefixed with --
            (e.g., --container-name)
    """
    return {name for command in commands
            for _, name, _, _ in
            Formatter().parse(command.format(**{**config_defaults,
                                                **default_args,
                                                **{key.replace('_', '-'): key for key in args.keys()},
                                                **{(key[2:] if key.startswith('--') else key):
                                                   '{{{}}}'.format((key[2:] if key.startswith('--') else key))
                                                   for key in environment_args.keys()}}))
            if name}


def _add_group_args(group_name, group_args, parser):
    """Adds arguments for an action to a parser based on values provided.

    Args:
        group_name (:obj:`str`): Argument group to add.
        group_args (:obj:`dict`): Dictionary of args to use for the argument group.
        parser (:py:obj:`argparse.ArgumentParser`): Parser instance.
    """
    group = parser.add_argument_group('{} arguments'.format(group_name))
    for arg_name, arg_parameters in group_args.items():
        arg_names = arg_name.replace(' ', '').split(',')
        group.add_argument(*arg_names, **arg_parameters)
        logger.debug('Adding %s with parameters (%s) ...',
                     ('argument ({})'.format(arg_names[0])
                      if len(arg_names) == 1
                      else 'arguments ({})'.format(', '.join(arg_names))),
                     '; '.join('{}="{}"'.format(k, v) for k, v in arg_parameters.items()))


def _add_help(parser):
    """Utility method that adds a help argument to whichever parser is passed to it. This is
    needed to correctly handle display of help messages through the various parsers we create
    dynamically at runtime.

    Args:
        parser (:py:obj:`argparse.ArgumentParser`): Parser instance.
    """
    parser.add_argument('-h', '--help',
                        action='help',
                        default=argparse.SUPPRESS,
                        help='show this help message and exit')
