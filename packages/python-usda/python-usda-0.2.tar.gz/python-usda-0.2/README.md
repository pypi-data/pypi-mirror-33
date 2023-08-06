# python-usda

[![License](https://img.shields.io/pypi/l/python-usda.svg)](https://pypi.org/project/python-usda/) [![Python Package Format](https://img.shields.io/pypi/format/python-usda.svg)](https://pypi.org/project/python-usda/) [![Supported Python versions](https://img.shields.io/pypi/pyversions/python-usda.svg)](https://pypi.org/project/python-usda/) [![Package status](https://img.shields.io/pypi/status/python-usda.svg)](https://pypi.org/project/python-usda/) [![Requirements Status](https://requires.io/github/Lucidiot/python-usda/requirements.svg?branch=master)](https://requires.io/github/Lucidiot/python-usda/requirements/?branch=master) [![Maintainability](https://api.codeclimate.com/v1/badges/9a969172a5d47456376e/maintainability)](https://codeclimate.com/github/Lucidiot/python-usda/maintainability) [![Code Health](https://landscape.io/github/Lucidiot/python-usda/master/landscape.svg?style=flat)](https://landscape.io/github/Lucidiot/python-usda/master) [![Build Status](https://travis-ci.org/Lucidiot/python-usda.svg?branch=master)](https://travis-ci.org/Lucidiot/python-usda) [![Coverage Status](https://coveralls.io/repos/github/Lucidiot/python-usda/badge.svg?branch=master)](https://coveralls.io/github/Lucidiot/python-usda?branch=master) ![GitHub last commit](https://img.shields.io/github/last-commit/Lucidiot/PseudoScience.svg) [![Gitter](https://img.shields.io/gitter/room/PseudoScience/Lobby.svg?logo=gitter-white)](https://gitter.im/BrainshitPseudoScience/Lobby) ![Badge count](https://img.shields.io/badge/badge%20count-12-brightgreen.svg)

python-usda is a fork of [pygov](https://pypi.org/project/pygov/) focused on [USDA's Food Composition Database API](http://ndb.nal.usda.gov/ndb/doc/).

## Installation

```
pip install python-usda
```

## Usage

``` python
from usda.client import UsdaClient

client = UsdaClient("YOUR_API_KEY")
foods = client.list_foods(5)

for food in foods:
    print food.name
```

Result:

```
Abiyuch, raw
Acerola juice, raw
Acerola, (west indian cherry), raw
Acorn stew (Apache)
Agave, cooked (Southwest)
```
