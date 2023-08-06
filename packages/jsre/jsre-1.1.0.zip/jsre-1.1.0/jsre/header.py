'''
Common constants for jsre

@author: Howard

Copyright (c) 2018, Howard Chivers
All rights reserved.
'''


VM_MAX_STATE_SIZE = 16384    # maximum number of character states allowed in vm

''' jsre flags
 to be compatible with re's use of flags:
ASCII      = 0x100
IGNORECASE = 0x2
LOCALE     = 0x4
MULTILINE  = 0x8
DOTALL     = 0x10
VERBOSE    = 0x40
'''
I              = 0x2
IGNORECASE     = 0x2      # any individual characters are case insensitive
M              = 0x8
MULTILINE      = 0x8      # ^ and $ match line boundaries as well as start and end of buffer
S              = 0x10
DOTALL         = 0x10     # '.' matches line endings as well as all other characters
X              = 0x40
VERBOSE        = 0x40     # allow while space and comments in re
INDEXALT       = 0x200    # index highest level of alternatives
SECTOR         = 0x400    # use stride and offset to specify possible anchor positions

# Undocumented debugging flags
XTRACE         = 0x1000    # run VM with trace enabled
XTRACE_VERBOSE = 0x2000    # set verbose (readable) trace
XDUMPPROG      = 0x4000    # print compiled program
XDUMPPARSE     = 0x8000    # print parse tree
XASYNCHRONOUS  = 0x10000   # move anchor a byte at a time, not default character byte size

# node types in parse tree
TYPE_GROUP     = 0x1
TYPE_CLASS     = 0x2
TYPE_CHAR      = 0x4
TYPE_HEX       = 0x8
TYPE_PROPERTY  = 0x10
TYPE_DOT       = 0x20
TYPE_PROG      = 0x40
TYPE_ALT       = 0x80
TYPE_REPEAT    = 0x100
TYPE_RELATION  = 0x200
TYPE_RANGE     = 0x400
TYPE_CLASSREF  = 0x800   # reference to an identical class
TYPE_CHARCLASS = 0x1000  # has character class tree attached
TYPE_COMPILED  = 0x2000  # has state index
TYPE_AUXCHARS  = 0x4000  # childList contains additional characters or compiled refs
