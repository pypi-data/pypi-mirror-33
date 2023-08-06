# Contributing to InSilicoSeq

Thank you for your interest in our software :heart: :tada:

## Conduct

We are committed to providing a friendly, safe and welcoming environment for
all. If you wish to contribute, you are expected to adhere to a
[code of conduct](CODE_OF_CONDUCT.md)

## How to contribute

This project is still at an early stage and open to suggestions of any kind.
Chat with us by
[opening and issue](https://github.com/HadrienG/InSilicoSeq/issues) or fork
the repository and
[open a pull request](https://github.com/HadrienG/InSilicoSeq/pulls)

## Coding guidelines

* Please adhere to [PEP8](https://www.python.org/dev/peps/pep-0008/)
* The docstrings should follow the
[Google style guide](http://www.sphinx-doc.org/en/stable/ext/napoleon.html)
* Your pull request should pass the unit tests.
New code/functionality should come with a test.
* Ideally a pull request should solve one problem or add one functionality.

## Set up your dev environment

The following steps assume you have python >= 3.5 and `pipenv` installed.

1. Fork the repository and clone your fork

2. Install the development dependencies

```
pipenv install --dev
```

3. Make your changes.

4. You can test the software with

```bash
pipenv run capture
```

and run the tests with

```bash
pipenv run test
```

5. Make your pull request 🎉
