# pus

[![Travis](https://img.shields.io/travis/limix/pus.svg?style=flat-square&label=linux%20%2F%20macos%20build)](https://travis-ci.org/limix/pus)

Update the required packages in setup.cfg file.

## Install

Enter

```bash
pip install pus
```

from the command-line.

## Usage

Enter

```bash
pus setup.cfg
```

## Running the tests

Enter

```python
python -c "import pus; pus.test()"
```

## Acknowledgment

This package is mostly a wrapper around the [pur](https://github.com/alanhamlett/pip-update-requirements) package.
Many thanks to its contributors!

## Authors

* [Danilo Horta](https://github.com/horta)

## License

This project is licensed under the [MIT License](https://raw.githubusercontent.com/limix/pus/master/LICENSE.md).
