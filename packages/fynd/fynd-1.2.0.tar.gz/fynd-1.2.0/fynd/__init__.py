"""
Fynd: A super simple string searching library
    for complex list/dict structures
Version: 1.2.0
GitHub: https://github.com/ahmednooor/fynd
License: MIT
Author: Ahmed Noor (https://github.com/ahmednooor)
"""

from copy import deepcopy


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

        if isinstance(target, (list, tuple, dict)):
            for key, val in enumerate(target):
                if isinstance(target, dict):
                    key = val

                if isinstance(target[key], str):
                    target_string = target[key] + ""
                    if self._case_sensitive is True \
                            and search_string in target_string:
                        path.append(key)
                        self._paths.append(deepcopy(path))
                        path.pop()

                    elif self._case_sensitive is False \
                            and search_string.lower() in target_string.lower():
                        path.append(key)
                        self._paths.append(deepcopy(path))
                        path.pop()

                elif isinstance(target[key], (list, tuple, dict)):
                    path.append(key)
                    self._search(search_string, target[key], deepcopy(path))
                    path.pop()
