# T3 Python Core Library

[![pipeline status](https://gitlab.t-3.com/sunoco/t3-python-core/badges/master/pipeline.svg)](https://gitlab.t-3.com/sunoco/t3-python-core/commits/master)
[![coverage report](https://gitlab.t-3.com/sunoco/t3-python-core/badges/master/coverage.svg)](https://gitlab.t-3.com/sunoco/t3-python-core/commits/master)
[![PyPI version](https://badge.fury.io/py/t3-core.svg)](https://badge.fury.io/py/t3-core)

## Install

### Setup Virtualenv (optional)
```sh
python -m venv .venv
source .venv/bin/activate

# There is a bug in pip 9.x  go ahead and upgrade to make sure that you're pip 10.x
pip install --upgrade pip
```

### Install
```sh
# Install from pypi
pip install t3-core

# Install in the `src` dir of your python environment
pip install -e git+ssh://git@gitlab.t-3.com:t3-core/t3-core-python.git

# Choose where the clone lives
git clone ssh://git@gitlab.t-3.com:t3-core/t3-core-python.git
pip install -e ./t3-python-core
```

## Testing & Linting
### Test & Coverage Report
```sh
pytest
```

### Lint
```sh
pylama
```
