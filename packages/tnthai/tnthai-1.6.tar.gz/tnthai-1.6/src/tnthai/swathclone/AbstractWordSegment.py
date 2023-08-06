#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import abc

class AbstractGramTrie:
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def __init__(self,):
        pass

class AbstractSegmentAlgorithm:
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def Segmenting(self, ):
        pass

class AbstractGramSegment:
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def __init__(self, ):
        pass
    
    @abc.abstractmethod
    def Segment(toBeSegmentInput):
        pass
    
class PrototypeGramTrie(AbstractGramTrie):
    def __init__(self,):
        pass

class PrototypeSegmentAlgorithm(AbstractSegmentAlgorithm):
    def Segmenting(self, InputString, GramTrie):
        pass

class PrototypeGramSegment(AbstractGramSegment):
    def __init__(self, GramTrieClass, SegmentAlgorithmClass):
        self.GramTrie = GramTrieClass()
        self.SegmentAlgorithm = SegmentAlgorithmClass()
        assert isinstance(self.GramTrie, AbstractGramTrie)
        assert isinstance(self.SegmentAlgorithm, AbstractSegmentAlgorithm)
    
    def Segment(toBeSegmentInput):
        result = self.GramAlgorithm.Segmenting(toBeSegmentInput, self.GramTrie)
        return result

if __name__ == '__main__':
    c = PrototypeGramSegment(PrototypeGramTrie,PrototypeSegmentAlgorithm)

    

    
    