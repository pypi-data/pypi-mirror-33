'''
Provides character classes, including file storage and recovery and set operations.

@author: Howard Chivers

Copyright (c) 2015, Howard Chivers
All rights reserved.

Version 1 = Ran 54 tests in 129.387s
After change to integer leafs: Ran 53 tests in 224.837s (long)  Ran 52 tests in 42.328s (short)

'''
import logging
import os
import sys
import struct
import traceback
from zlib import crc32
import code

from header import VM_MAX_STATE_SIZE

# character transition leaf marker (used in place of destination state for transition)
VM_CHARACTER_OK      = 0xFFFF    # character transition success

COMPILE_ROOT         = 'JSRE_Compiled'

charClassLog         = logging.getLogger(__name__)
__compilePath        = os.path.join(os.path.dirname(os.path.abspath(__file__)), COMPILE_ROOT)

FILE_FORMAT_MAGIC    = 0x7EB0 + 3
FILE_STATESIZE_LIMIT = 65521
BYTE_HASH_FIELDSIZE  = 65521
TRANSITION_MASK      = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
SEARCHMASK           = [(0XFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF, 128), (0XFFFFFFFFFFFFFFFF, 64), (0XFFFFFFFF, 32), (0XFFFF, 16), (0XFF, 8), (0XF, 4), (0X3, 2), (0X1, 1)]

__allCharacters      = {}   # dict of encoding->\p{any}


class CharClass(object):
    '''CharClass represents a character class as a byte-compiled tree

    There are two modes of representation for the state object - tree or graph, and
    this class coverts lazily between the two as required.

    Primary functions:
        Load from character, range or file
        Store to file or vm
        union, intersection, difference, inverse, equality, clone

    ISSUES:
    Does not process surrogates - from Python 3.4 surrogates are not processed
    in the utf codecs.  See https://docs.python.org/3/library/codecs.html

    The behaviour of set operations is undefined for non-deterministic
    character encodings, although Union will allow them to be loaded
    and therefore identified.
    '''
    __loadRegistry       = {}   # dict to cache loaded classes

    def __init__(self, encoding, ifirstChar=None, ilastChar=None):
        ''' build class, optionally from a single character or a range

        Params:
            ifirstChar, ilastChar    inclusive range,
                                     integers representing unicode code points
            encoding                 string with valid python codec name
        '''
        self.encoding       = encoding
        if ifirstChar is not None:
            self.newFromRange(ifirstChar, ilastChar)
        else:
            self._newState()

    def _newState(self, stateIsTree=True):
        ''' initialise character class
        '''
        self.transitions    = {}   # state -> {value->nextState}
        self.leafs          = {}   # state -> codes (256 set bitmapped to a long integer)
        self.stateSize      = 0    # number of states used
        self.stateIsTree    = stateIsTree

    def newFromRange(self, ifirstChar, ilastChar):
        ''' load character class from a range of integer code points

        Params:
            ifirstChar,ilastChar    the range is inclusive,
                                    characters are integer code points
        '''

        if ilastChar is None or ifirstChar == ilastChar:
            self.newFromCharacter(chr(ifirstChar))
        else:
            # a simplified union resuiltig in a tree,
            self._newState()
            self.stateSize = 1
            self.transitions = {0: {}}
            for cp in range(ifirstChar, ilastChar + 1):
                try:
                    bchar = chr(cp).encode(self.encoding)
                except Exception as _:
                    # empty character
                    continue
                tstate = 0
                for i in range(len(bchar) - 1):
                    code = 1 << bchar[i]
                    if code in self.transitions[tstate]:
                        # transition exists
                        tstate = self.transitions[tstate][code]
                    else:
                        # transition to a new subtree
                        self.transitions[tstate][1 << bchar[i]] = self.stateSize
                        tstate = self.stateSize
                        self.stateSize += 1
                        for j in range(i + 1, len(bchar) - 1):
                            self.transitions[tstate] = {1 << bchar[j]: self.stateSize}
                            tstate = self.stateSize
                            self.stateSize += 1
                        break
                # add to leaf
                if tstate in self.leafs:
                    self.leafs[tstate] |= 1 << bchar[-1]
                else:
                    self.leafs[tstate] = 1 << bchar[-1]

            # add in final state
            if self.transitions[0] == {}:
                del(self.transitions[0])
                if self.leafs == {}:
                    self.stateSize = 0
                    return
            self._toGraph()

    def addByteRange(self, ifirstByte, ilastByte):
        ''' load a byte range (e.g. from hex range) in ascii.

        This will load a byte range regardless of the class encoding.

        Params:
            iFirstByte,ilastByte    range is inclusive
                                    bytes are integers
        '''
        if (ifirstByte > 255) or (ilastByte > 255):
            raise ValueError("Invalid Byte Range ({:d} - {:d}".format(ifirstByte, ilastByte))

        code = _codeRange(ifirstByte, ilastByte) if ifirstByte < ilastByte else _codeRange(ilastByte, ifirstByte)
        if 0 in self.leafs:
            self.leafs[0] = self.leafs[0] | code
        else:
            self.leafs[0]  = code
            self.stateSize = 1

    def newFromCharacter(self, cString):
        '''Initialise object all characters from a string

        Note that the string is encoded as a single character.

        Normal behaviour is for characters that cannot be encoded to silently
        return an empty code set. This is (probably) OK for large character
        sets but caller should check that single characters in an RE have been
        encoded by using isEmpty().
        '''
        self._newState()
        try:
            bchar = cString.encode(self.encoding)
        except Exception as _:
            # return empty character
            return

        self.stateSize   = len(bchar)
        last             = self.stateSize - 1

        for i in range(last):
            self.transitions[i] = {1 << bchar[i]: i + 1}

        self.leafs[last] = 1 << bchar[last]

    # @coverage
    def isEmpty(self):
        ''' Returns true if the character class is empty (null)
        '''
        if self.stateSize == 0:
            return True
        return False

    def getStateSize(self):
        ''' Returns state size of character class
        '''
        return self.stateSize

    def toFile(self, fileName):
        ''' Write character class to named file.

        File format:  (int16 unless noted)
          header:            formatVersion,encodingNameSize,stateSize,
                             transitionCount,leafCount, encodingName_UTF8
          transitions:       [state, numberoftransitions [nextState, byteindicator, bytelist]]
          leafs:             [state, byteindicator, byte list]
                             checksum

        the byte indicator low 5 bits is first byte posn, upper 3 is count (7 = all) of subsequent byte list (see codes)
        '''
        self._toTree()
        self._toGraph()

        # protect from very large character classes
        if self.stateSize > FILE_STATESIZE_LIMIT:
            charClassLog.warning("State limit exceeded in character class, not written to file, state size = {}, file = {}".format(self.stateSize, fileName))
            return

        # protect from non-deterministic classes - ie where leaf and transition have same value
        for s in self.leafs:
            if s in self.transitions:
                for v in self.transitions[s]:
                    if v & self.leafs[s]:
                        charClassLog.warning("Character is internally non-deterministic (" + fileName + "), will not be written")
                        return
        try:
            # check file
            if os.path.isfile(fileName):
                charClassLog.warning("Character output file already exists (" + fileName + "), will be overwritten")

            # open new file
            if not os.path.exists(os.path.dirname(fileName)):
                os.makedirs(os.path.dirname(fileName))
            outFile = open(fileName, 'wb')
        except Exception as e:
            charClassLog.error("OS IO error when trying to open character class file ({}) for writing, error: {}".format(fileName, str(e)))
            exit(1)

        encoding = self.encoding.encode('utf-8')
        try:
            bout = bytearray(struct.pack('=HHHHH', FILE_FORMAT_MAGIC,
                                         len(encoding), self.stateSize,
                                         len(self.transitions), len(self.leafs)))
            bout.extend(encoding)

            for tk in self.transitions:
                bout.extend(struct.pack('=HH', tk, len(self.transitions[tk])))
                for valueKey in self.transitions[tk]:
                    ind, ser = _codeToSerial(valueKey)
                    bout.extend(struct.pack('=HB',
                                            self.transitions[tk][valueKey],
                                            ind))
                    for v in ser:
                        bout.extend(struct.pack('=B', v))

            for tk in self.leafs:
                ind, ser = _codeToSerial(self.leafs[tk])
                bout.extend(struct.pack('=HB', tk, ind))
                for v in ser:
                    bout.extend(struct.pack('=B', v))

            bhash = crc32(bytes(bout)) % BYTE_HASH_FIELDSIZE
            # print('out  ' + str(bytes(bout)) + '   ' + str(bhash))
            bout.extend(struct.pack('=H', bhash))
            outFile.write(bytes(bout))
            outFile.close()

        except Exception as e:
            charClassLog.error("Error when trying to write character class file ({}) for writing, error: {}".format(self.fileName, str(e)))
            exit(1)

    def loadFromFile(self, fileName):
        ''' Rebuild state of self from the named character class file.

        See toFile() for file format.
        '''
        # check file
        if not os.path.isfile(fileName):
            raise FileNotFoundError("Character file (" + fileName + ") not found")

        if fileName in CharClass.__loadRegistry:
            self._selfLoad(CharClass.__loadRegistry[fileName].clone())
            return

        try:
            inFile = open(fileName, 'rb')
            inData = inFile.read()
            inFile.close()
        except Exception as e:
            charClassLog.error("OS IO error when trying to open character class file ({}), error: {}".format(fileName, str(e)))
            exit(1)

        try:
            # checksum test
            check = crc32(bytes(inData[:-2])) % BYTE_HASH_FIELDSIZE
            test = struct.unpack('=H', inData[-2:])[0]
            if test != check:
                charClassLog.error("Checksum error when reading from character class file ({})".format(fileName))
                exit(1)

            version, encodeLen, self.stateSize, transLen, leafLen = struct.unpack_from('=HHHHH', inData, 0)
            start = struct.calcsize('=HHHHH')
            self.stateIsTree = False

            if version != FILE_FORMAT_MAGIC:
                charClassLog.error("Format Version error when reading from character class file ({})".format(fileName))
                exit(1)

            self.encoding = inData[start:start + encodeLen].decode('utf-8')
            start += encodeLen

            self.transitions = {}
            for _i in range(transLen):
                # states
                state, count = struct.unpack_from('=HH', inData, start)
                start += struct.calcsize('=HH')
                self.transitions[state] = {}

                # transitions from state
                for _j in range(count):
                    child      = struct.unpack_from('=H', inData, start)[0]
                    start     += struct.calcsize('=H')
                    start, val = _serialToCode(start, inData)
                    self.transitions[state][val] = child

            self.leafs = {}
            for _ in range(leafLen):
                state = struct.unpack_from('=H', inData, start)[0]
                start += struct.calcsize('=H')
                start, self.leafs[state] = _serialToCode(start, inData)

            # cache the character
            CharClass.__loadRegistry[fileName] = self.clone()

        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            charClassLog.error("Conversion error when trying to decode character class file ({}), error: {}".format(fileName, str(e)))
            exit(1)

    def writeGDF(self, fileName):
        ''' Write character class to .gdf graph file.

        warning - not all info is preserved
        artificial nodes corresponding to leafs are generated and
        given numbers = <source node>L
        transitions are labelled with the action value
        '''
        path = fileName + '.gdf'

        # check directory?
        try:
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(fileName))
            gdfFile = open(path, 'w')
        except Exception as e:
            charClassLog.error("OS IO error when trying to open gdf file ({}) for writing, error: {}".format(fileName, str(e)))
            exit(1)

        gdfFile.write('nodedef> name VARCHAR,label VARCHAR,Modularity Class VARCHAR\n')
        mode = 1
        for p in range(self.stateSize):
            gdfFile.write('"{0}","{0}","{1:d}"\n'.format(p, mode))
        mode = 2
        for p in self.leafs:
            gdfFile.write('"{0:d}L","{0:d}L","{1:d}"\n'.format(p, mode))

        gdfFile.write('edgedef> node1,node2,label VARCHAR,directed BOOLEAN\n')
        for s in self.transitions:
            src = self.transitions[s]
            for vk in src:
                gdfFile.write('"{:d}","{:d}","{}",true\n'.format(s, src[vk], _codeToString(vk)))
        for s in self.leafs:
            codes = self.leafs[s]
            label = []
            code  = 0
            while codes > 0:
                if 1 & codes:
                    label.append('{:02X}'.format(code))
                code += 1
                codes = codes >> 1
            gdfFile.write('"{0:d}","{0:d}L","{1}",true\n'.format(s, _codeToString(self.leafs[s])))

        gdfFile.close()

    # **************************************************************************
    #      Public Set Operations: union, difference, intersection,
    #                             equality, negate, clone
    # **************************************************************************

    def union(self, right):
        ''' Self is updated with the union with right

        right is unmodified
        '''
        _checkEncoding(self, right)

        # identity and zero checks
        if right is self:
            return self
        if self.stateSize == 0:
            self._selfLoad(right.clone())
            return self
        if right.stateSize == 0:
            return self

        # normalise & map lright - > self
        right = right.clone()
        cmap = _makeComparable(self, right)

        # make space for unmapped states from right
        oldStateSize = self.stateSize
        for s in right.transitions:
            if s not in cmap:
                cmap[s] = self.stateSize
                self.stateSize += 1
        for s in right.leafs:
            if s not in cmap:
                cmap[s] = self.stateSize
                self.stateSize += 1

        # merge right into self
        for rs in right.transitions:
            tdict = right.transitions[rs]
            if cmap[rs] < oldStateSize:
                # state is identical to existing state,
                # need to copy in any new transitions
                for vk in tdict:
                    if cmap[tdict[vk]] >= oldStateSize:

                        # transition points to a merged state,
                        # so transition be rewritten and added
                        if cmap[rs] not in self.transitions:
                            self.transitions[cmap[rs]] = {}
                        self.transitions[cmap[rs]][vk] = cmap[tdict[vk]]
            else:
                # new state to be added
                self.transitions[cmap[rs]] = {}
                for vk in tdict:
                    self.transitions[cmap[rs]][vk] = cmap[tdict[vk]]

        # merge leaf nodes
        for rl in right.leafs:
            if cmap[rl] in self.leafs:
                # existing leaf nodes must be merged
                self.leafs[cmap[rl]] |= right.leafs[rl]
            else:
                # can just copy new leaf node to state
                self.leafs[cmap[rl]] = right.leafs[rl]

        return self

    def intersect(self, right):
        ''' Intersect self with right
        '''
        _checkEncoding(self, right)

        if self.stateSize == 0 or right.stateSize == 0:
            self._newState()
            return self
        if right is self:
            return self

        right = right.clone()
        cmap = _makeComparable(self, right)

        # intersect any mapped leaf codes
        # this should be all that is necessary
        # assumes that transition model is consistent
        tleafs = {}
        for rk in right.leafs:
            if rk in cmap and cmap[rk] in self.leafs:
                newCodes = self.leafs[cmap[rk]] & right.leafs[rk]
                if newCodes > 0:
                    tleafs[cmap[rk]] = newCodes
        self.leafs = tleafs

        # throw away any states that don't terminate in a leaf
        # or result in full leaf range
        self._trimNonTerminatingStates()
        self._compactStates()
        return self

    def difference(self, right):
        ''' Remove elements from self that are present in right.
        '''
        _checkEncoding(self, right)

        if right.stateSize == 0 or self.stateSize == 0:
            return self
        if right is self:
            self._newState()
            return self

        right = right.clone()
        cmap = _makeComparable(self, right)

        # difference mapped leaf codes
        for rk in right.leafs:
            if rk in cmap and cmap[rk] in self.leafs:
                self.leafs[cmap[rk]] &= (TRANSITION_MASK ^ right.leafs[rk])
                if self.leafs[cmap[rk]] == 0:
                    del self.leafs[cmap[rk]]

        # remove states if possible
        self._trimNonTerminatingStates()
        self._compactStates()
        return self

    def inverse(self):
        '''
        This returns the inverse of a character class by set difference between
        'any' and that class.

        Note that this preserves multi-byte encoding, not just byte logic.
        '''
        cc = getAny(self.encoding)
        cc.difference(self)
        self._selfLoad(cc)
        return self

    def equals(self, test):
        ''' Test if a character class is equal to self.

        This is a deep test that maps the two classes and
        checks if they produce the same result. Returns true if equal.
        '''
        # the basics!
        if test is self:
            return True
        if test.encoding != self.encoding:
            return False

        left  = self.clone()
        right = test.clone()

        cmap = _makeComparable(left, right)

        if right.stateSize != left.stateSize:
            return False
        if len(left.leafs) != len(right.leafs):
            return False
        if len(left.transitions) != len(right.transitions):
            return False
        if right.stateSize != len(cmap):
            return False

        # check leaf nodes
        for tk in right.leafs:
            if cmap[tk] not in left.leafs:
                # cannot match leaf
                return False
            if left.leafs[cmap[tk]] != right.leafs[tk]:
                return False
        return True

    def clone(self):
        ''' Return a clone of this character class.

        This is deep enough to separate child objects.
        '''
        res = CharClass(self.encoding)

        for sk in self.transitions:
            res.transitions[sk] = self.transitions[sk].copy()
        res.leafs       = self.leafs.copy()
        res.stateSize   = self.stateSize
        res.stateIsTree = self.stateIsTree
        return res

    def addAsSequence(self, right):
        ''' Adds the given character class as a sequence from
            self.

            This renumbers right above self then modifies
            leafs in self to transitions to the root of the new states

            This first ensures that the classes are graphs, the code will
            work with tree input but would result in a non-minimal graph.
        '''

        if right is None or right.stateSize == 0:
            return self
        _checkEncoding(self, right)

        self._toGraph()
        right._toGraph()

        newcc = right.clone() if self is right else right

        base = self.stateSize
        # rewrite leafs to point at extra character base
        for sk in self.leafs:
            if sk not in self.transitions:
                self.transitions[sk] = {}
            self.transitions[sk][self.leafs[sk]] = base
        del(self.leafs)
        self.leafs = {}

        # copy extra leafs and transitions
        for sk in newcc.leafs:
            self.leafs[base + sk] = newcc.leafs[sk]
        for sk in newcc.transitions:
            self.transitions[base + sk] = {}
            for val in newcc.transitions[sk]:
                self.transitions[base + sk][val] = base + newcc.transitions[sk][val]
        self.stateSize += newcc.stateSize

        return self

    def _toGraph(self):
        ''' Compress character class tree into compact graph.

        Compresses the tree into a graph by working from the leaves toward the
        root breadth first and joining matching cases.
        '''

        if not self.stateIsTree:
            return

        if self.stateSize < 2:
            self.stateIsTree = True
            return

        # compress to unique leaf nodes
        oldtonew = {}
        valtonew = {}
        newleafs  = {}
        for l in self.leafs:
            if self.leafs[l] in valtonew:
                new         = valtonew[self.leafs[l]]
                oldtonew[l] = new
            else:
                valtonew[self.leafs[l]] = l
                newleafs[l]             = self.leafs[l]
        self.leafs = newleafs

        # build dependancy dict and rewrite transitions to new leafs
        depthMap   = [{0: set()}]     # list of [{child state -> (set of parent states)}]
        d       = 0
        while len(depthMap[d]):
            d += 1
            depthMap.append({})
            depends = depthMap[d]
            for ps in depthMap[d - 1]:
                if ps in self.transitions:
                    for val in self.transitions[ps]:
                        cs = self.transitions[ps][val]
                        if cs in oldtonew:
                            self.transitions[ps][val] = oldtonew[cs]
                            cs = oldtonew[cs]
                        if cs in depends:
                            depends[cs].add(ps)
                        else:
                            depends[cs] = {ps, }

        # merge identical states
        for depth in range(d - 1, 1, -1):
            depends     = depthMap[depth]
            dependsNext = depthMap[depth - 1]
            # index from gradnchildren to reduce comparsons for groups
            for gs in depends:
                groups = []
                # group parents of this state by transitions
                groupval = []
                for child in depends[gs]:
                    found = False
                    for i, val in enumerate(groupval):
                        if val == self.transitions[child]:
                            groups[i].append(child)
                            found = True
                            break
                    if not found:
                        groups.append([child])
                        groupval.append(self.transitions[child])

                # merge within groups if possible
                for group in groups:
                    # merge group members
                    if len(group) < 2:
                        continue
                    commonChild = group[0]
                    del[group[0]]
                    for child in group:
                        parent = dependsNext[child].pop()    # still a tree here
                        for val in self.transitions[parent]:
                            if self.transitions[parent][val] == child:
                                self.transitions[parent][val] = commonChild
                        dependsNext[commonChild].add(parent)
                        for gs in self.transitions[child].values():
                            depends[gs].discard(child)
                            depends[gs].add(commonChild)
                        del(self.transitions[child])
                        del(dependsNext[child])

        # merge/encode transitions
        for parent in self.transitions:
            # group by next state
            groups      = []
            states      = []
            lastState   = None
            for val, child in sorted(self.transitions[parent].items(), key=lambda x: x[1]):
                if child != lastState:
                    groups.append([val])
                    states.append(child)
                    lastState = child
                else:
                    groups[-1].append(val)
            # replace group of transitions with single code
            self.transitions[parent] = {}
            for i, child in enumerate(states):
                gval = 0
                for val in groups[i]:
                    gval |= val
                self.transitions[parent][gval] = child

        # compact state indexes
        self._compactStates()
        self.stateIsTree = False
        return

    def _toTree(self):
        ''' rewrite a compressed graph into a tree.
        '''
        if self.stateIsTree:
            return

        if self.stateSize < 2:
            self.stateIsTree = True
            return

        newtrans = {0: {}}
        newleafs = {}
        if 0 in self.leafs:
            newleafs[0] = self.leafs[0]
        self.stateSize   = self._expand_toTree(1, 0, 0, newtrans, newleafs)
        self.transitions = newtrans
        self.leafs       = newleafs
        self.stateIsTree = True

    def _expand_toTree(self, nextState, oldRoot, newRoot, newtrans, newleafs):
        ''' rewrite a sub-graph to a tree
        '''
        for code, oldState in self.transitions[oldRoot].items():
            newState   = nextState
            nextState += 1
            newtrans[newRoot][code] = newState
            if oldState in self.transitions:
                newtrans[newState] = {}
                nextState          = self._expand_toTree(nextState, oldState, newState, newtrans, newleafs)
            if oldState in self.leafs:
                newleafs[newState] = self.leafs[oldState]
        return nextState

    def publishToVM(self, vm):
        ''' Publish the character class to a VM

        Failure raises exception up to caller except an allocation error which
        returns None.

        If successful the vm base index of the state is returned
        setting compact=False prevents compression of tree to graph
        prior to writing to the vm (either write the tree or a
        previously published graph)

        If an empty class is written then a single sate is allocated,
        which will be empty.

        Most of the failures that this might raise are compile errors
        reported by the vm. They all indicate system errors in the
        python compiling the re!
        '''
        self._toGraph()

        if self.getStateSize() >= (VM_MAX_STATE_SIZE - vm.nextState()):
            msg = "This RE is too big for space remaining in virtual machine"
            charClassLog.error(msg)
            raise MemoryError(msg)

        baseState = vm.nextState()
        toAllocate = 1 if self.stateSize == 0 else self.stateSize

        # make space
        try:
            vm.newStates(baseState, baseState + toAllocate)
        except Exception as e:
            charClassLog.error("Error while allocating VM states: " + str(e))
            return None

        # write transitions
        for sk in self.transitions:
            tdict = self.transitions[sk]
            for tk in tdict:
                for start, end in _codeToRangelist(tk):
                    vm.newTransitionRange(baseState + sk, start, end, baseState + tdict[tk])

        for sk in self.leafs:
            for start, end in _codeToRangelist(self.leafs[sk]):
                vm.newTransitionRange(baseState + sk, start, end, VM_CHARACTER_OK)

        return baseState

    def _selfLoad(self, tcc):
        ''' Load the state into self
        '''
        self.transitions = tcc.transitions
        self.leafs       = tcc.leafs
        self.stateSize   = tcc.stateSize
        self.stateIsTree = tcc.stateIsTree
        self.encoding    = tcc.encoding

    def _inverseStateDirectory(self):
        ''' Return a dictionary which maps states to their parents.

        This builds a dictionary which shows the parent of any state.
        This requies self to be a tree,

        Returns:
            destinationState -> (sourceState,transitionValue)
        '''
        imap = {}
        for s in self.transitions:
            src = self.transitions[s]
            for vk in src:
                imap[src[vk]] = (s, vk)
        return imap

    def _compactStates(self):
        ''' Compress the character class to minimum state size.

        This takes a charClass in which some states and transitions have been
        removed and renumbers it to the minimum state size.

        returns the map between old and new states for al states that have been moved
        '''

        if self.stateSize == 0:
            return

        # find current top
        for top in range(self.stateSize - 1, -1, -1):
            if top in self.transitions or top in self.leafs:
                break

        # restore to normal python range
        top += 1

        # find spare slots
        spareStates = []
        for i in range(top):
            if i not in self.transitions and i not in self.leafs:
                spareStates.append(i)
        if len(spareStates) == 0:
            # already compressed - any missing are at the top of the range
            self.stateSize = top
            return

        # map top states into spare slots
        rmap = {}

        slot = 0
        state = top - 1
        while slot < len(spareStates) and state > spareStates[slot]:
            if state in self.transitions or state in self.leafs:
                rmap[state] = spareStates[slot]
                if state in self.transitions:
                    self.transitions[spareStates[slot]] = self.transitions[state]
                    del self.transitions[state]
                if state in self.leafs:
                    self.leafs[spareStates[slot]] = self.leafs[state]
                    del self.leafs[state]
                slot  += 1
                state -= 1
            else:
                state -= 1

        for tk in self.transitions:
            for vk in self.transitions[tk]:
                old = self.transitions[tk][vk]
                if old in rmap:
                    self.transitions[tk][vk] = rmap[old]

        self.stateSize = top - len(spareStates)

        return rmap

    def _trimNonTerminatingStates(self):
        ''' Remove states that do not support a leaf node.

        That is, a leaf node anywhere in the subtree of the state.
        '''
        # need to build inverse state directory
        imap = self._inverseStateDirectory()

        # remove redundant states
        for ts in range(self.stateSize):
            self._testOrRemoveState(ts, imap)

        return self

    def _testOrRemoveState(self, ts, imap):
        ''' If a state has no transitions or values, remove it.

        Checks if a state has any transitions or value, if remove it
        then test recursively down the chain toward root.

        Params:
            ts     test state to check
            imap   inverse state map - state->parent
        '''

        # terminate if the state is useful, otherwise remove the state
        useful = False
        if ts in self.transitions:
            if len(self.transitions[ts]) > 0:
                useful = True
            else:
                del self.transitions[ts]

        if ts in self.leafs:
            if self.leafs[ts] > 0:
                useful = True
            else:
                del self.leafs[ts]

        if useful:
            return

        # if at root, nothing below
        if ts == 0:
            return

        # state has been removed here, or perhaps earlier,
        # remove transition to state if in map
        if ts not in imap:
            return

        # if transaction to state has already gone (probably cleaned recursively)
        if imap[ts][0] not in self.transitions:
            return
        if imap[ts][1] not in self.transitions[imap[ts][0]]:
            return

        # otherwise remove transition to this state state
        del self.transitions[imap[ts][0]][imap[ts][1]]

        # then check if source needs to be removed
        self._testOrRemoveState(imap[ts][0], imap)

    # **************************************************************************
    #      Static code set Helpers
    # **************************************************************************

# codes are lists of integers (0 - 255) bit mapped onto a long integer

def _toCode(vals):
    ''' compress a list of integer values to a code '''

    prev = 0
    bit  = 1
    code = 0
    for v in sorted(vals):
        bit   = bit << (v - prev)
        code |= bit
        prev  = v
    return code


def _codeToList(code):
    ''' expand code to a list of integers '''
    vals = []
    bit  = 0
    while code > 0:
        for mask, shift in SEARCHMASK:
            if not (mask & code):
                code = code >> shift
                bit += shift
        vals.append(bit)
        code = code >> 1
        bit += 1
    return vals


def _codeToRangelist(code):
    ''' expand code into a list of ranges of set bites
        e.g 0b01000110 -> [(1,2), (6, 6)]
    '''
    res = []
    bit   = 0
    while code:
        for mask, shift in SEARCHMASK:
            if not (mask & code):
                code = code >> shift
                bit += shift
        start = bit
        for mask, shift in SEARCHMASK:
            if not (mask & ~code):
                code = code >> shift
                bit += shift
        res.append((start, bit - 1))
    return res


def _codeToSerial(code):
    ''' format code as bytes list for file output

        returns byteindicator, [list of bytes]
        the list of bytes is a section from the code,
        the bytes indicator ls 5 bits is the start address in bytes,
           the ms 3 bites is the count if bytes, unless 7 in which all bytes above the first are copied
    '''
    sout = []

    # find 1st byte with set bit
    posn = 0
    while code & 0xFF == 0:
        posn += 1
        code   = code >> 8

    # find active range
    for count in range(8):
        sout.insert(0, code & 0xFF)
        code = code >> 8
        if code == 0:
            break

    # if count == 7, copy all remaining bytes
    if count == 7:
        for _ in range(24 - posn):
            sout.insert(0, code & 0xFF)
            code = code >> 8

    return posn + (count << 5), sout


def _serialToCode(start, inData):
    ''' read file serialised value to code
        inData is a byte stream,
        start is the address of the start of the code record

        returns the next start and the code value
    '''

    ind    = struct.unpack_from('=B', inData, start)[0]
    start += struct.calcsize('=B')

    posn  = ind & 0x1F
    count = 31 - posn if (ind >> 5) == 7 else ind >> 5
    codes = 0
    for _ in range(count + 1):
        codes = (codes << 8) | struct.unpack_from('=B', inData, start)[0]
        start += struct.calcsize('=B')

    return start, codes << (posn * 8)


def _codeRange(first, last=None):
    ''' return a Codes value with members from first to last inclusive '''

    codes = 1 << first
    bit   = codes

    if last is None:
        return codes

    for _ in range(1 + last - first):
        codes |= bit
        bit = bit << 1

    return codes


def _codeToString(code):
    ''' return printable string - csv hex values '''
    return ','.join(['{:02X}'.format(x) for x in _codeToList(code)])


# ****************************************************************************
#    State and transition Helpers
# ****************************************************************************


def _makeComparable(left, right):
    ''' modify the two ccs to allow comparison as minimal compatible trees

        This results in two trees in which transition codes from
        equivalent states are either identical or non-overlapping.

        transition codes are pairwise checked for common codes, and if found then
        these codes are removed from their originals and new transitions built to
        equivalent states. a mapping between the two is developed as a side effect.

        assumes that right and left are different objects
    '''
    right._toTree()
    left._toTree()

    if right.stateSize < 2 or left.stateSize < 2:
        if right.stateSize == 0 or left.stateSize == 0:
            return {}
        else:
            return {0: 0}

    cmap = {0: 0}          # right state -> left state
    todo = [(0, 0)]        # state pairs, (l, r)
    compactL = True
    compactR = True

    while len(todo):
        rootL, rootR = todo[0]
        del(todo[0])

        for codeL, nextL in list(left.transitions[rootL].items()):
            for codeR, nextR in [(c, s) for c, s in right.transitions[rootR].items() if c & codeL]:
                if codeR == codeL:
                    # identical, can avoid most common processing
                    # comparable new states, so map and check further
                    cmap[nextR] = nextL
                    if nextL in left.transitions and nextR in right.transitions:
                        todo.append((nextL, nextR))
                    break
                else:
                    common = codeL & codeR
                    # remove common from current transitions
                    del(left.transitions[rootL][codeL])
                    codeL &= (TRANSITION_MASK ^ common)
                    left.transitions[rootL][codeL] = nextL

                    del(right.transitions[rootR][codeR])
                    codeR &= (TRANSITION_MASK ^ common)
                    right.transitions[rootR][codeR] = nextR

                    # copy in new common sub-trees
                    newL = left.stateSize
                    left.stateSize += 1
                    left.transitions[rootL][common] = newL
                    _cloneSubtree(left, nextL, newL)

                    newR = right.stateSize
                    right.stateSize += 1
                    right.transitions[rootR][common] = newR
                    _cloneSubtree(right, nextR, newR)

                    # comparable new states, so map and check further
                    cmap[newR] = newL
                    if newL in left.transitions and newR in right.transitions:
                        todo.append((newL, newR))

                    # check still code values for original transitions
                    if not codeR:
                        del(right.transitions[rootR][codeR])
                        _delSubtree(right, nextR)
                        compactR = False

                    if not codeL:
                        del(left.transitions[rootL][codeL])
                        _delSubtree(left, nextL)
                        compactL = False
                        break

    # if ccs not compact, rewrite states
    if not compactL:
        moved = left._compactStates()
        for sr in cmap:
            sl = cmap[sr]
            if sl in moved:
                cmap[sr] = moved[sl]
    if not compactR:
        moved = right._compactStates()
        for sr in moved:
            if sr in cmap:
                cmap[moved[sr]] = cmap[sr]
                del(cmap[sr])
    return cmap


def _cloneSubtree(cc, sfrom, sto):
    ''' clone a subtree from sfrom to sto
    '''
    if sfrom in cc.leafs:
        cc.leafs[sto] = cc.leafs[sfrom]
    if sfrom in cc.transitions:
        for code in cc.transitions[sfrom]:
            snew = cc.stateSize
            cc.stateSize += 1
            if sto not in cc.transitions:
                cc.transitions[sto] = {code: snew}
            else:
                cc.transitions[sto][code] = snew
            _cloneSubtree(cc, cc.transitions[sfrom][code], snew)


def _delSubtree(cc, sfrom):
    ''' delete a subtree rooted at sfrom
    '''
    if sfrom in cc.leafs:
        del(cc.leafs[sfrom])
    if sfrom in cc.transitions:
        for code, snext in list(cc.transitions[sfrom].items()):
            _delSubtree(cc, snext)
        del(cc.transitions[sfrom])


# @coverage
def _checkEncoding(class1, class2):
    if class1.encoding != class2.encoding:
        raise ValueError('CharClass: attempt to combine character classes compiled for different encodings')


# ***************************************************************************
#    Public Module methods
# ***************************************************************************


def newClassFromList(encoding, sourceList):
    ''' Build a new class as the union of the named character classes.

    Failure is silent, since some encodings will not have all listed classes.
    Up to caller to check all present if required.
    '''
    res = CharClass(encoding)
    if len(sourceList) == 0:
        return res
    for charPath in sourceList:
        cc  = CharClass(encoding)
        try:
            cc.loadFromFile(charPath)
            res.union(cc)
        except FileNotFoundError:
            pass
    return res


def newCasedCharacter(cases, encoding, character, ignoreCase):
    ''' Build a single character class from either an integer or a string.

    If the string is several code points it will be treated as a graphene
    sequence (eg CR LF) and built as a single character; case processing
    will not be used.

    Otherwise (for a single character or an integer character) if ignoreCase is
    True then the case file is used to merge alternative cases into the class.
    The case file contains circular refs which are usually 2 long, but may be 3
    '''
    cString = character
    if not isinstance(cString, str):
        cString = chr(character)

    cc = CharClass(encoding)
    cc.newFromCharacter(cString)
    if len(cString) > 1:
        return cc

    if ignoreCase and cString in cases:
        nextChar = cases[cString]
        while nextChar != cString:
            cn = CharClass(encoding)
            cn.newFromCharacter(nextChar)
            cc.union(cn)
            nextChar = cases[nextChar]
    return cc


def getAny(encoding):
    '''Return the 'any' character set: all possible encoded codepoints.
    '''

    # is the cc cached?
    if encoding in __allCharacters:
        return __allCharacters[encoding].clone()

    # is the cc compiled in the unicode database?
    try:
        cc = CharClass(encoding)
        cc.loadFromFile(os.path.join(__compilePath, encoding, 'any'))
        if cc.stateSize:
            __allCharacters[encoding] = cc
            return cc.clone()
    except Exception as _:
        pass

    # otherwise need to build the class from scratch
    cc = CharClass(encoding)
    cc.newFromRange(0, 0x10FFFF)
    __allCharacters[encoding] = cc
    return cc.clone()
