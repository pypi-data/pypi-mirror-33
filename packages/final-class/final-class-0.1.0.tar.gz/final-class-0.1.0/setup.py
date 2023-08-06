# -*- coding: utf-8 -*-
from distutils.core import setup

modules = \
['final_class']
setup_kwargs = {
    'name': 'final-class',
    'version': '0.1.0',
    'description': 'Final classes for Python 3',
    'long_description': "# final_class\n\n[![wemake.services](https://img.shields.io/badge/style-wemake.services-green.svg?label=&logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAABGdBTUEAALGPC%2FxhBQAAAAFzUkdCAK7OHOkAAAAbUExURQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP%2F%2F%2F5TvxDIAAAAIdFJOUwAjRA8xXANAL%2Bv0SAAAADNJREFUGNNjYCAIOJjRBdBFWMkVQeGzcHAwksJnAPPZGOGAASzPzAEHEGVsLExQwE7YswCb7AFZSF3bbAAAAABJRU5ErkJggg%3D%3D)](http://wemake.services) [![Build Status](https://travis-ci.org/wemake-services/final_class.svg?branch=master)](https://travis-ci.org/wemake-services/final_class)\n\nFinal classes for `python3.6+`.\n\n\n## Features\n\n- No metaclass conflicts\n- No runtime overhead\n- No dependencies\n- Type hints included\n- Designed to be as simple as possible\n\n\n## Why?\n\nIn languages like `java` we have a nice way\nto restrict subclassing any class by making it `final`:\n\n```java\npublic final class SomeClass {\n  // ...\n}\n```\n\nIn `python` we don't have such feature out of the box.\nThat's where `final_class` library comes in!\n\n\n## Installation\n\n```bash\npip install final_class\n```\n\n\n## Usage\n\n```python\nfrom final_class import final\n\n\n@final\nclass Example(object):  # You won't be able to subclass it!\n    ...\n\n\nclass Error(Example):  # Raises `TypeError`\n    ...\n```\n\n\n## License\n\nMIT.\n",
    'author': 'sobolevn',
    'author_email': 'mail@sobolevn.me',
    'url': 'https://github.com/wemake-services/final-class',
    'py_modules': modules,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
