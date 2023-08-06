# [sshreader][]

## Overview

[sshreader][] is a Python Module for multi-processing/threading ssh connections in order to make ssh operations
across multiple servers parallel.  It utilizes the [Paramiko](http://www.paramiko.org/) module for its ssh client.

As of version 3.6, sshreader is supported under Python 2.7 and 3.6.

## License

[sshreader][] is released under the [GNU Lesser General Public License v3.0][],
see the file LICENSE and LICESE.lesser for the license text.

## Installation

The most straightforward way to get the sshreader module working for you is:

> pip install sshreader

or

> python setup.py install

This will ensure that all the requirements are met.

### Development Installation

If you are wanting to work on development of sshreader perform the following:

> pip install -U -r requirements.txt

To ensure all development requirements are met. This will allow you to build the Sphinx Documentation for sshreader!

## Documentation

The documentation for sshreader can be found at http://sshreader.readthedocs.io/

### Building Docs

If you have installed the requirements for sshreader you can build its Sphinx Documentation simply by:

> cd docs;
> make html

Then simply open **docs/build/html/index.html** in your browser.

## Contributing

Comments and enhancements are very welcome.

Report any issues or feature requests on the [BitBucket bug
tracker](https://bitbucket.org/isaiah1112/sshreader/issues?status=new&status=open). Please include a minimal
(not-) working example which reproduces the bug and, if appropriate, the
 traceback information.  Please do not request features already being worked
towards.

Code contributions are encouraged: please feel free to [fork the
project](https://bitbucket.org/isaiah1112/sshreader) and submit pull requests to the develop branch.

## Extras

Included with sshreader is a binary called **pydsh** (generally installed in /usr/local/bin/).  This works very similar to
[pdsh](https://computing.llnl.gov/linux/pdsh.html) but uses sshreader at its core to perform ssh commands in parallel
and return the results.  The output of *pydsh* can also be piped through the **dshbak** tool that comes with pdsh.

Pydsh uses [hostlist expressions](https://www.nsc.liu.se/~kent/python-hostlist/) to get its list of hosts
to process.


[GNU Lesser General Public License v3.0]: http://choosealicense.com/licenses/lgpl-3.0/ "LGPL v3"

[sshreader]: https://bitbucket.org/isaiah1112/sshreader "sshreader Module"
