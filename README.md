![Dragonfly](https://www.ladybug.tools/assets/img/dragonfly.png)

[![Build Status](https://github.com/ladybug-tools/dragonfly-radiance/actions/workflows/ci.yaml/badge.svg)](https://github.com/ladybug-tools/dragonfly-radiance/actions)

[![Python 3.10](https://img.shields.io/badge/python-3.10-orange.svg)](https://www.python.org/downloads/release/python-3100/) [![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/) [![Python 2.7](https://img.shields.io/badge/python-2.7-green.svg)](https://www.python.org/downloads/release/python-270/) [![IronPython](https://img.shields.io/badge/ironpython-2.7-red.svg)](https://github.com/IronLanguages/ironpython2/releases/tag/ipy-2.7.8/)

# dragonfly-radiance

Dragonfly extension for Radiance simulation.

## Installation

`pip install dragonfly-radiance`

To check if the command line interface is installed correctly
use `dragonfly-radiance --help`.

## QuickStart

```python
import dragonfly_radiance
```

## [API Documentation](http://ladybug-tools.github.io/dragonfly-radiance/docs)

## Local Development

1. Clone this repo locally
```
git clone git@github.com:ladybug-tools/dragonfly-radiance

# or

git clone https://github.com/ladybug-tools/dragonfly-radiance
```
2. Install dependencies:
```
cd dragonfly-radiance
pip install -r dev-requirements.txt
pip install -r requirements.txt
```

3. Run Tests:
```
python -m pytest tests/
```

4. Generate Documentation:
```
sphinx-apidoc -f -e -d 4 -o ./docs ./dragonfly_radiance
sphinx-build -b html ./docs ./docs/_build/docs
```
