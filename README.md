# Asciinema

[![PyPI version](https://badge.fury.io/py/asciinema.png)](http://badge.fury.io/py/asciinema)
[![Build Status](https://travis-ci.org/sickill/asciinema.png?branch=master)](https://travis-ci.org/sickill/asciinema)
[![Downloads](https://pypip.in/d/asciinema/badge.png)](https://pypi.python.org/pypi/asciinema)

Command line client for [asciinema.org](https://asciinema.org) service.

## Installation

The latest __stable version__ of asciinema can always be installed or updated
to via [pip](http://www.pip-installer.org/en/latest/index.html) (prefered) or
easy\_install:

    sudo pip install --upgrade asciinema

Alternatively:

    sudo easy_install asciinema

Or, you can install the __development version__ directly from GitHub:

    sudo pip install --upgrade https://github.com/sickill/asciinema/tarball/master

See [installation docs](https://asciinema.org/docs/installation) for more
options (Ubuntu, Fedora, Arch, Gentoo etc).

## Usage

Check the available commands and options with:

    asciinema -h

## Contributing

If you want to contribute to this project check out
[Contributing](https://asciinema.org/contributing) page.

## Authors

Developed with passion by [Marcin Kulik](http://ku1ik.com) and great open
source [contributors](https://github.com/sickill/asciinema/contributors)

## Differences

My fork of the asciinema-cli incorporates some major changes. First of all,
it can now be properly used in your project. You can record output of python
methods, and you can choose wheter or not to upload casts.

Everything is now encapsulated in the Asciicast object. All operations (recording,
uploading) will happen on this object. Check the documentation for the API reference.

In addition I moved all CLI code into it's own directory and made it clear that it's
CLI (by choosing an appropriate name for it).

Last but not least, I began working on Issue#49 (also known as "New workflow"), by adding
a local git repository for handling versions (not yet fully implemented) and local storage.

## Copyright

Copyright &copy; 2011-2013 Marcin Kulik. See LICENSE.txt for details.
