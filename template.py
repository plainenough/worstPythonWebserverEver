#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import codecs

#Flat template for python projects

def main(error):
    UTF8Writer = codecs.getwriter('utf8')
    sys.stdout = UTF8Writer(sys.stdout)
    #Do something here.
    return 

if __name__ == '__main__':
    main()
