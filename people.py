#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import codecs

#Flat template for python projects

class People(object):
    """A simple class of people"""
    def __init__(self, name, age, friend = None):
        """Initialize  name and age"""
        self._name = name
        self._age = age
        if friend:
            self._friend.append(friend)
        else:
            self._friend = []

    def list_me(self):
        """This will print the object person"""
        print(self._name + " is awesome")
    
    def __str__(self):
        """This will format the print for you."""
        print_self = self._name.title()
        return print_self
    
    def add_friend(self, friend):
        self._friend.append(friend)
        return "Success"

def main():
    UTF8Writer = codecs.getwriter('utf8')
    sys.stdout = UTF8Writer(sys.stdout)

    return 

if __name__ == '__main__':
    main()
