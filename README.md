# jupyspace

[![PyPI - Version](https://img.shields.io/pypi/v/jupyspace.svg)](https://pypi.org/project/jupyspace)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/jupyspace.svg)](https://pypi.org/project/jupyspace)
[![Build Status](https://github.com/davidbrochart/jupyspace/workflows/CI/badge.svg)](https://github.com/davidbrochart/jupyspace/actions)

-----

**Table of Contents**

- [Installation](#installation)
- [License](#license)

## Installation

Install [micromamba](https://mamba.readthedocs.io/en/latest/installation.html#micromamba) for your platform, then:
```console
pip install jupyspace
```

## Development installation

Install [micromamba](https://mamba.readthedocs.io/en/latest/installation.html#micromamba) for your platform, then:
```console
micromamba create -n jupyspace
micromamba activate jupyspace
micromamba install -c conda-forge python

pip install -e jupyspace_api
pip install -e plugins/localspace
pip install -e plugins/spacex
pip install -e .[test]

asphalt run config.yaml
```

## Usage

```console
jupyspace --open-browser
```

## License

`jupyspace` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
