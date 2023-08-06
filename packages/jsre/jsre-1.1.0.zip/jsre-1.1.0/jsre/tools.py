#!python
'''
Runs tests and compilation for jsre.

@author: Howard Chivers

Copyright (c) 2015, Howard Chivers
All rights reserved.

'''
import logging

from codecs import lookup
from sys import argv
from os import path

import test

from ucd import compileEncoding, normaliseName, isEncodingInstalled, DEFAULT_ENCODINGS
from charclass import CharClass

usage = '''
usage:
test                    runs jsre unit tests
compile [encoding]      installs default encodings, or the specified encoding


Encodings must be installed before use, the default encodings include the normal unicode
encodings (utf_8, utf_16_be, utf_16_le, utf_32_be, utf_32_le), ascii and a range of code pages.
'''

'''
undocumented:
test_new encoding int,int...  builds char class from a list of codepoints (either decimal or hex), writes test file and graph
'''


DEBUG = False
if DEBUG:
    DEBUG_OUTPUT   = 'JSRE_DEBUG_OUTPUT'
    __debugOutput  = path.join(path.dirname(path.abspath(__file__)), DEBUG_OUTPUT)


# set tools logger
LOGGING_LEVEL = logging.INFO
toolLog = logging.getLogger()
toolLog.setLevel(LOGGING_LEVEL)


def abort(msg):
    print('Error: ' + msg)
    print(usage)
    exit(1)


def getCharacterClass(fileName):
    ''' get char `class from cmd args
        arg2 encoding
        arg3 csv list of code poins in decmal or hex
    '''
    encoding = argv[2]
    first = True
    for c in argv[3].split(','):
        if first:
            cc = CharClass(encoding, int(c, 0))
            first = False
        else:
            tc = CharClass(encoding, int(c, 0))
            cc.union(tc)
    cc.writeGDF(fileName)
    return cc


if __name__ == '__main__':
    if DEBUG:
        debugFileName = path.join(__debugOutput, 'test_codes')
    if len(argv) < 2:
        abort('Invalid command line, no command given.')
    if argv[1] == 'test':
        print("Running jsre tests")
        test.runTest()
        exit(0)
    elif argv[1] == 'compile':
        if len(argv) == 2:
            print("Compiling default encodings")
            for encoding in DEFAULT_ENCODINGS:
                compileEncoding(encoding)
        else:
            encoding = normaliseName(argv[2])
            if isEncodingInstalled(encoding):
                abort("Encoding {} is already installed".format(encoding))
            try:
                lookup(encoding)
            except Exception as e:
                abort("Encoding {} is not known - not a valid Python codec".format(encoding))
            if encoding in ('utf_32', 'utf_32_le', 'utf_16', 'utf_16_le'):
                abort("Error - encoding {} not valid, must specify -be".format(encoding))
            print('Compiling Unicode properties for encoding: {}'.format(encoding))
            compileEncoding(encoding)
        print("Compile Complete")
        exit(0)
    elif not DEBUG:
        abort('Command not recognised: {}'.format(argv[1]))

    if argv[1] == 'test_new':     # <encoding> <cs list of code points in hex or decimal>
        cc       = getCharacterClass(debugFileName + '_args')
        cc.toFile(debugFileName)
        cr = CharClass(argv[1])
        cr.loadFromFile(debugFileName)
        cr.writeGDF(debugFileName + '_new')

    elif argv[1] == 'test_intersect':      # <encoding> <cs list of code points in hex or decimal>
        cc = CharClass(argv[1])
        cc.loadFromFile(debugFileName)
        cr = getCharacterClass(debugFileName + '_args')
        cc.intersect(cr)
        cc.toFile(debugFileName)
        cc.writeGDF(debugFileName + '_intersect')

    elif argv[1] == 'test_diff':
        cc = CharClass(argv[1])
        cc.loadFromFile(debugFileName)
        cr = getCharacterClass(debugFileName + '_args')
        cc.difference(cr)
        # cc.toFile(debugFileName)
        cc.writeGDF(debugFileName + '_difference')

    elif argv[1] == 'load':
        cc = CharClass(argv[1])
        cc.loadFromFile(argv[2])
        cc.writeGDF(debugFileName + '_load')

    elif argv[1] == 'test_pub':
        cc = CharClass(argv[1])
        cc.loadFromFile(argv[2])
        ref = cc.clone()
        cc._toGraph()
        cc.writeGDF(debugFileName + '_published')
        print('graph size =', cc.getStateSize())
        cc._toTree()
        if cc.equals(ref):
            print('rountrip tree ok')
        else:
            print('roundtrip not equal')
    else:
       abort('Command not recognised: {}'.format(argv[1])) 
