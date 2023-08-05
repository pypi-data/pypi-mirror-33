# Askky Python Client

[![PyPI Version](https://img.shields.io/pypi/v/askky.svg)](https://pypi.org/project/askky/) [![PyPI](https://img.shields.io/pypi/pyversions/askky.svg)]() [![License](https://img.shields.io/:license-mit-blue.svg)](https://opensource.org/licenses/MIT)

Python bindings for interacting with Askky API

This is primarily meant for clients who wish to perform interactions with the Askky API programatically.

## Installation

```sh
$ pip install askky
```

## Usage

You need to setup your key using the following:
You can find your Private Api key at <http://app.askky.co/account/>.

```py
import askky
client = askky.Client()
```

