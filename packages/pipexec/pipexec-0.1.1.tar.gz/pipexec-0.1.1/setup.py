# -*- coding: utf-8 -*-
from distutils.core import setup

modules = \
['pipexec']
install_requires = \
['cleo>=0.6.8,<0.7.0']

entry_points = \
{'console_scripts': ['poetry = pipexec.pipexec']}

setup_kwargs = {
    'name': 'pipexec',
    'version': '0.1.1',
    'description': 'Test pip packages quickly',
    'long_description': '# pipexec\nTry out pip packages quickly\n',
    'author': 'Amos Omondi',
    'author_email': None,
    'url': 'https://github.com/amos-o/pipexec',
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
}


setup(**setup_kwargs)
