# python-usda

[![Requirements Status](https://requires.io/github/Lucidiot/python-usda/requirements.svg?branch=master)](https://requires.io/github/Lucidiot/python-usda/requirements/?branch=master) [![Maintainability](https://api.codeclimate.com/v1/badges/9a969172a5d47456376e/maintainability)](https://codeclimate.com/github/Lucidiot/python-usda/maintainability) [![Code Health](https://landscape.io/github/Lucidiot/python-usda/master/landscape.svg?style=flat)](https://landscape.io/github/Lucidiot/python-usda/master) [![Build Status](https://travis-ci.org/Lucidiot/python-usda.svg?branch=master)](https://travis-ci.org/Lucidiot/python-usda) [![Coverage Status](https://coveralls.io/repos/github/Lucidiot/python-usda/badge.svg?branch=master)](https://coveralls.io/github/Lucidiot/python-usda?branch=master) ![GitHub last commit](https://img.shields.io/github/last-commit/Lucidiot/PseudoScience.svg) [![GitHub license](https://img.shields.io/github/license/Lucidiot/PseudoScience.svg)](https://github.com/Lucidiot/PseudoScience/blob/master/LICENSE) [![Gitter](https://img.shields.io/gitter/room/PseudoScience/Lobby.svg?logo=gitter-white)](https://gitter.im/BrainshitPseudoScience/Lobby)

python-usda is a fork of [pygov](https://pypi.org/project/pygov/) focused on [USDA's Food Composition Database API](http://ndb.nal.usda.gov/ndb/doc/).

## Installation

python-usda is in active development. When it will be listed on the Python Package Index, you will be able to install it using:

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
