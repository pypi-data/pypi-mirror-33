..
  <!---
  Copyright 2018 StreamSets Inc.

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License. See accompanying LICENSE file.
  --->

StreamSets Test Environments
============================
This repository is home to the **StreamSets Test Environments (STE)**. It is designed to be run as a command line
program. STE provides mechanism to start and stop environments which you can use to test against.
For example, a command such as
```
ste start CDH_5.12.0
```
will start a 2 node clusterdock CDH 5.12.0 cluster without requiring knowledge of the specific arguments to pass to
clusterdock. Similarly
```
ste stop CDH_5.12.0
```
will stop the clusterdock CDH 5.12.0 cluster and do any necessary cleanup.
The goal of STE is to simplify starting and stopping environments so as they can be easily used for
testing or development.

Installation
------------
**Pre-requisites**

- Python 3.X
- A recent version of Docker

**Installation**

To install STE, simply use `pip <https://github.com/pypa/pip>`_ (or pipenv):

.. code-block:: bash

    $ pip3 install streamsets-testenvironments

Commands
--------
The following are some commands you can use with STE. In the examples here, we'll use MySQL_5.7

Start an environment:

.. code-block:: bash

    $ ste start MySQL_5.7

Stop an environment:

.. code-block:: bash

    $ ste stop MySQL_5.7

Dry run without starting an environment (and also running in verbose mode):

.. code-block:: bash

    $ ste -v start --dry-run MySQL_5.7

STE general help:

.. code-block:: bash

    $ ste -h

STE start environment help (lists available environments which can be started):

.. code-block:: bash

    $ ste start -h

STE stop environment help (lists available environments which can be stopped):

.. code-block:: bash

    $ ste stop -h

STE start help for an environment:

.. code-block:: bash

    $ ste start MySQL_5.7 -h

STE stop help for an environment:

.. code-block:: bash

    $ ste stop MySQL_5.7 -h
