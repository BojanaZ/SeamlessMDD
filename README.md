# SeamlessMDD

## Project setup

To be able to run the project, You should have installed python and :

1. [Python3](https://www.python.org/) (tested on Python 3.5)
2. [Virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

Dependancies for these project are listed in venv/requirements.txt. To install them, move to SeamlessMDD directory, activate the Virtual environment, and use pip.

On macOS and Linux:
```
$ source venv/bin/activate
$ pip install -r venv/requirements.txt
```

On Windows:
```
.\venv\Scripts\activate
pip install -r venv\requirements.txt
```

To configure virtual envrionment in PyCharm, follow [these instructions](https://www.jetbrains.com/help/pycharm/creating-virtual-environment.html).

## Testing

This project uses [pytest](https://docs.pytest.org/en/latest/) library for testing. It relies on its conventions for discovery, and because of that, You should check it's [conventions](https://docs.pytest.org/en/latest/goodpractices.html#test-discovery).

The library has been added to requirements.txt, so You should first move to SeamlessMDD folder, activate the virtual environment, and install the requirements using the pip.

After that, You can invoke the pytest to run tests:
```
$ pytest
```

