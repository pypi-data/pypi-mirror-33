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

"""This module contains model abstractions used by STE."""

import logging
import os
import subprocess

logger = logging.getLogger(__name__)


class Command:
    """Command information for later execution by subprocess.

    Args:
        args (:obj:`str`): Command (`str`) to run.
        env (:obj:`dict`, optional): Dictionary of environment variables to set before running command.
            Default: ``None``
    """
    def __init__(self, args, env=None):
        self.args = args
        # When setting the `env` attribute, we merge the arguments passed with the environment variables
        # in our current shell session. This is needed to pass through things like AWS credentials.
        self.env = dict(env or {}, **os.environ)

    def execute(self, dry_run=False):
        """Execute command.

        Args:
            dry_run (:obj:`bool`, optional): If ``True``, don't actually execute command (but display what it is).
                Default: ``False``
        """
        logger.debug('Running command: %s (environment variables: %s)', self.args,
                     ', '.join('{}={}'.format(key, value)
                               for key, value in self.env.items()) if self.env else 'none')
        if not dry_run:
            subprocess.run(self.args, executable='/bin/bash', env=self.env, check=True, shell=True)
