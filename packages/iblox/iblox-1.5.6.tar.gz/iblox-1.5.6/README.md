## Overview

[iblox][] is a wrapper for [Infoblox's WAPI](https://www.infoblox.com/).
It uses Python's request module to handle session caching and is very flexible. In order to maintain the most amount of
compatibility we test iblox using the following versions of Python:

* Python2.7
* Python3.4
* Python3.5
* Python3.6
* Python3.7

## License

[iblox][] is released under the [GNU Lesser General Public License v3.0][],
see the file LICENSE and LICENSE.lesser for the license text.

## Installation

The most straightforward way to get the iblox module working for you is:

> pip install iblox

or

> python setup.py install

This will ensure that all the requirements are met.

### Development Installation

If you are wanting to work on development of iblox perform the following:

> pip install -U -r requirements_test.txt

To ensure all development requirements are met. This will allow you to build the Sphinx Documentation!

## Documentation

Documentation for the iblox module can be found at http://iblox.readthedocs.io/

### Building Docs

If you have installed the requirements for iblox you can build its Sphinx Documentation simply by:

> pip install -U -r requirements_docs.txt
> cd docs;
> make html

Then simply open **docs/build/html/index.html** in your browser.

## Contributing

Comments and enhancements are very welcome.

Report any issues or feature requests on the [BitBucket bug
tracker](https://bitbucket.org/isaiah1112/infoblox/issues?status=new&status=open). Please include a minimal
(not-) working example which reproduces the bug and, if appropriate, the
 traceback information.  Please do not request features already being worked
towards.

Code contributions are encouraged: please feel free to [fork the
project](https://bitbucket.org/isaiah1112/infoblox/fork) and submit pull requests to the **develop** branch.

## More information

- [Infoblox DDI](https://www.infoblox.com/)

[GNU Lesser General Public License v3.0]: http://choosealicense.com/licenses/lgpl-3.0/ "LGPL v3"

[iblox]: https://bitbucket.org/isaiah1112/infoblox "iblox Module"
