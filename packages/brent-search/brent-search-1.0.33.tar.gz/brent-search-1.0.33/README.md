# brent-search

[![Travis](https://img.shields.io/travis/limix/brent-search.svg?style=flat-square&label=linux%20%2F%20macos%20build)](https://travis-ci.org/limix/brent-search) [![AppVeyor](https://img.shields.io/appveyor/ci/Horta/brent-search.svg?style=flat-square&label=windows%20build)](https://ci.appveyor.com/project/Horta/brent-search) [![Read the Docs (version)](https://img.shields.io/readthedocs/brent-search/stable.svg?style=flat-square)](http://brent-search.readthedocs.io/)

Brent's method for univariate function optimization.

## Example

```python
from brent_search import brent

def func(x, s):
  return (x - s)**2 - 0.8

r = brent(lambda x: func(x, 0), -10, 10)
print(r)
```

The output should be

```python
(0.0, -0.8, 6)
```

## Install

From command line, enter

```bash
pip install brent-search
```

## Running the tests

Install dependencies

```bash
pip install -U pytest pytest-pep8
```

then run

```python
python -c "import brent_search; brent_search.test()"
```

## Authors

* [Danilo Horta](https://github.com/horta)

## Acknowledgements

- http://people.sc.fsu.edu/~jburkardt/c_src/brent/brent.c
- Numerical Recipes 3rd Edition: The Art of Scientific Computing
- https://en.wikipedia.org/wiki/Brent%27s_method


## License

This project is licensed under the [MIT License](https://raw.githubusercontent.com/limix/brent-search/master/LICENSE.md).
