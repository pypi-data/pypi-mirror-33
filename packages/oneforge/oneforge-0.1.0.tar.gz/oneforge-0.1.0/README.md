# oneforge

[![image](https://img.shields.io/pypi/v/oneforge.svg?style=flat-square)](https://pypi.org/project/oneforge)
[![image](https://img.shields.io/pypi/pyversions/oneforge.svg?style=flat-square)](https://pypi.org/project/oneforge)
[![image](https://img.shields.io/pypi/l/oneforge.svg?style=flat-square)](https://pypi.org/project/oneforge)

---

1Forge REST API wrapper

## Instalation
oneforge is distributed on PyPI and is available on Linux/macOS and Windows and supports Python 3.6+.

``` bash
$ pip install -U oneforge
```

## Usage

``` python
from oneforge import OneForge, SYMBOLS

oforge = OneForge(api_key='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')

# Get quotes
oforge.quotes(SYMBOLS)

# Convert currency
oforge.convert('EUR', 'USD', 100)
```