"""
Fynd: A super simple string searching library
    for complex list/dict structures
Version: 1.3.0
GitHub: https://github.com/ahmednooor/fynd
License: MIT
Author: Ahmed Noor (https://github.com/ahmednooor)
"""


class Fynd:
    """ Fynd: A super simple string searching library
        for complex list/dict structures """

    def __init__(self, search_string):
        """ pass search string """
        self._search_string = search_string
        self._case_sensitive = False
        self._paths = []
        self._target = None

    def case_sensitive(self):
        """ set case_sensitive to True """
        self._case_sensitive = True
        return self

    def inside(self, target):
        """ pass the list/dict to search from """
        self._target = target
        if self._search_string == '':
            return []
        self._search(self._search_string, self._target)
        return self._paths

    def _search(self, search_string, target, path=None):
        """ search for passed string inside target list/dict
            - determine the type, list or dict?
            - iterate accordingly
            - if current item is a str? then compare
            - else call the function again for next iteration """

        if path is None:
            path = []

        if isinstance(target, str):
            if self._case_sensitive is True \
                    and search_string in target:
                self._paths.append(path + [])
                return

            elif self._case_sensitive is False \
                    and search_string.lower() in target.lower():
                self._paths.append(path + [])
                return

        elif isinstance(target, (list, tuple, dict)):
            for key, val in enumerate(target):
                if isinstance(target, dict):
                    key = val
                path.append(key)
                self._search(search_string, target[key], path)
                path.pop()
