# fynd

[![PyPI](https://img.shields.io/badge/pypi-v1.3.0-blue.svg)](https://pypi.org/project/fynd/)
[![Build Status](https://travis-ci.org/ahmednooor/fynd.svg?branch=master)](https://travis-ci.org/ahmednooor/fynd)

> `fynd` makes it super simple to search for strings in complex list/dict (JSON like) data structures. It returns a list of paths from root of the data structure to the found strings.

## Installation
```sh
pip install fynd
```

## Usage
```python
from fynd import Fynd as fynd

COLLECTION = {
    'blogposts': [
        {
            'title': 'Lorem Ipsum',
            'text': 'Dolor Sit Amet Blah Blah Blah'
        },
        {
            'title': 'Brown Fox',
            'text': 'The quick brown fox jumps over blah'
        }
    ]
}

# default usage:
RESULT = fynd('blah').inside(COLLECTION)
# ^ will return,
# [
#    ['blogposts', 0, 'text'], 
#    ^ COLLECTION['blogposts'][0]['text'] == 'Dolor Sit ... Blah'
#    ['blogposts', 1, 'text']
#    ^ COLLECTION['blogposts'][1]['text'] == 'The quick ... blah'
# ]

# case sensitive usage:
RESULT = fynd('blah').case_sensitive().inside(COLLECTION)
# ^ will return,
# [
#    ['blogposts', 1, 'text']
#    ^ COLLECTION['blogposts'][1]['text'] == 'The quick ... blah'
# ]

# not found case:
RESULT = fynd('hulalala').inside(COLLECTION)
# ^ will return,
# [] an empty list
```

## Meta
- License: MIT
- Author: Ahmed Noor
- Source: https://github.com/ahmednooor/fynd
