#!/usr/bin/env python
#  -*- coding: UTF-8 -*-

from tnthai.swathclone import AbstractWordSegment as AWS
import os, sys
import datrie
import string
# import cProfile
# import Timecount
import json

sys.setrecursionlimit(1000000)

class SwathDicTrie(AWS.PrototypeGramTrie):
    def __init__(self, ):
        # Initialize GramTrie
        self.Trie = datrie.Trie.load(os.path.dirname(os.path.abspath(__file__))+'/dict/my.trie')

# SegmentAlgorithm class
class SwathSegmentAlgorithm(AWS.PrototypeSegmentAlgorithm):
    def __init__(self, ):
        self.globalResult = list()
        self.segmentResult = list()
        self.failSegmentRemainText = []
        self.positive_backtrack = {}
        self.negative_backtrack = {}
        self.setResult = set()
        
    def Segmenting(self, InputString, GramTrie, Mode):
        # check python version 
        if (sys.version_info > (3, 0)):
            self.inputWord = InputString
            # Check mode 
            if (Mode == "Safe"):
                # clear variables                 
                self.segmentResult = list()
                # call recursive Segment_safe to find only first result
                self.Segment_safe(self.inputWord, GramTrie)
                # clone result from temp
                result = list(self.globalResult)
                # clear variables 
                self.globalResult = list()
                self.segmentResult = list()
                return Mode,result

            elif (Mode == "SafeBounding"):
                # clear variables 
                # do safe bounding segment
                self.Segment_safe_with_bounding(0,'',self.inputWord, GramTrie)
                # clone result from temp
                result = self.setResult
                # clear variables 
                self.positive_backtrack = {}
                self.negative_backtrack = {}
                self.setResult = set()
                return  Mode,result

            elif (Mode == "Unsafe"):
                # do unsafe segment
                self.Segment_unsafe(self.inputWord, GramTrie)
                # clone result from temp
                result = list(self.globalResult)
                # clear global Temp result
                self.globalResult = list() 
                return Mode,result

            elif (Mode == "Smart"):
                Mode = "Safe"
                # call recursive Segment_safe to find only first result
                self.Segment_safe(self.inputWord, GramTrie)
                # clone result from temp
                result = list(self.globalResult)
                # empty blacklist
                self.failSegmentRemainText = []
                #  if no result in safe
                if len(result) == 0:
                    Mode = "Unsafe"
                    # do unsafe segment
                    self.Segment_unsafe(self.inputWord, GramTrie)
                    # clone result from temp
                    result = list(self.globalResult)
                
                # clear global Temp result
                self.globalResult = list()
                
                return Mode,result
        else:
            # This is where python2 going to work
            
            # python2 have to decode thai word before use
            self.inputWord = InputString.decode('utf-8')
            # Check mode 
            if (Mode == "Safe"):
                # clear variables                 
                self.segmentResult = list()
                # call recursive Segment_safe to find only first result
                self.Segment_safe(self.inputWord, GramTrie)
                # clone result from temp
                result = list(self.globalResult)
                # clear variables 
                self.globalResult = list()
                self.segmentResult = list()
                return Mode,result

            elif (Mode == "SafeBounding"):
                # clear variables 
                # do safe bounding segment
                self.Segment_safe_with_bounding(0,'',self.inputWord, GramTrie)
                # clone result from temp
                result = self.setResult
                # clear variables 
                self.positive_backtrack = {}
                self.negative_backtrack = {}
                self.setResult = set()
                return  Mode,result

            elif (Mode == "Unsafe"):
                # do unsafe segment
                self.Segment_unsafe(self.inputWord, GramTrie)
                # clone result from temp
                result = list(self.globalResult)
                # clear global Temp result
                self.globalResult = list() 
                return Mode,result

            elif (Mode == "Smart"):
                Mode = "Safe"
                # call recursive Segment_safe to find only first result
                self.Segment_safe(self.inputWord, GramTrie)
                # clone result from temp
                result = list(self.globalResult)
                # empty blacklist
                self.failSegmentRemainText = []
                #  if no result in safe
                if len(result) == 0:
                    Mode = "Unsafe"
                    # do unsafe segment
                    self.Segment_unsafe(self.inputWord, GramTrie)
                    # clone result from temp
                    result = list(self.globalResult)
                
                # clear global Temp result
                self.globalResult = list()
                
                return Mode,result
    
    def Segment_safe(self, remainText, trie):
        
        # Bug Check Accurate Found by Army 27 June 
        # if remainText in cache fail so not trying segment
        # if remainText in self.failSegmentRemainText:
        #    return False
        
        # this always be true
        assert ("".join(self.segmentResult) + remainText) == self.inputWord
        
        if len(remainText) > 0:
            FirstChar = remainText[0]
            if self.isLeadingChar(FirstChar):
                Prefixes = trie.prefixes(remainText)
                resultOrCount = False
                
                for i in range(len(Prefixes)-1,-1,-1):
                    selectedPrefix = Prefixes[i]
                    self.segmentResult.append(selectedPrefix)
                    suffixRemainText = remainText[len(selectedPrefix):]
                    prefixResult = self.Segment_safe(suffixRemainText, trie)
                    self.segmentResult.pop()
                    resultOrCount = resultOrCount or prefixResult
                
                if resultOrCount == False:
                    #self.failSegmentRemainText.append(remainText)
                    pass
                
            else:
                if FirstChar in string.ascii_letters+string.digits+string.printable:

                    for i in string.punctuation,string.whitespace,string.ascii_letters,string.digits:
                        if FirstChar in i:
                            remain,othersCharResult = self.isOtherChar(FirstChar,remainText,i)

                    self.segmentResult.append(othersCharResult)
                    self.Segment_safe(remain, trie)
                    self.segmentResult.pop()

        else:
            # all remainText consume so. get the segmenting result
            self.globalResult.append(list(self.segmentResult))

    def Segment_safe_with_bounding(self, curID, select, remainText, trie):
        
        # same bug as Segment_safe
        # if remainText in self.failSegmentRemainText:
        #     return False

        # this always be true
        assert ("".join(self.segmentResult) + remainText) == self.inputWord
        
        if self.checkPBI(curID):
            return

        if self.checkNBI(curID):
            return  

        if len(remainText) > 0:
            FirstChar = remainText[0]
            if self.isLeadingChar(FirstChar):
                Prefixes = trie.prefixes(remainText)
                resultOrCount = False               

                for i in range(len(Prefixes)-1,-1,-1):
                    selectedPrefix = Prefixes[i]
                    curID += len(selectedPrefix)
                    self.segmentResult.append(selectedPrefix)
                    suffixRemainText = remainText[len(selectedPrefix):]
                    prefixResult = self.Segment_safe_with_bounding(curID,selectedPrefix, suffixRemainText, trie)
                    self.segmentResult.pop()
                    curID -= len(selectedPrefix)
                    resultOrCount = resultOrCount or prefixResult
                
                if resultOrCount == False:
                    self.negative_backtrack[curID-len(select)] = True   
                
            else:
                if FirstChar in string.ascii_letters+string.digits+string.printable:

                    for i in string.punctuation,string.whitespace,string.ascii_letters,string.digits:
                        if FirstChar in i:
                            remain,othersCharResult = self.isOtherChar(FirstChar,remainText,i)

                    self.segmentResult.append(othersCharResult)
                    self.Segment_safe_with_bounding(curID+len(othersCharResult),'',remain, trie)
                    self.segmentResult.pop()
                        
                else:
                    # in case other langauge , skip letter by letter
                    self.segmentResult.append(remainText[0])
                    self.Segment_safe_with_bounding(curID+1,select,remainText[1:], trie)
                    self.segmentResult.pop()
                    
        else:
            # all remainText consume so. get the segmenting result
            self.PBI()

    def Segment_unsafe(self, remainText, trie):
        # To get only first result
        if len(self.globalResult) > 0:
            return
    
        # this always be true
        assert ("".join(self.segmentResult) + remainText) == self.inputWord
        
        if len(remainText) > 0:
            FirstChar = remainText[0]
            if self.isLeadingChar(FirstChar):
                Prefixes = trie.prefixes(remainText)
                for i in range(len(Prefixes)-1,-1,-1):
                    self.segmentResult.append(Prefixes[i])
                    self.Segment_unsafe(remainText[len(Prefixes[i]):], trie)
                    self.segmentResult.pop()
                j=0
                unsafePrefixes=""
                while j<len(remainText):
                    Prefixes = trie.prefixes(remainText[j:])
                    j=j+1
                    if len(Prefixes)>0 :
                        unsafePrefixes=remainText[:j-1]
                        break
                    else:
                        unsafePrefixes=remainText[:j]
                    if j==len(remainText):
                        unsafePrefixes = remainText
                        break
                    if not self.isLeadingChar(remainText[j]):
                        unsafePrefixes = remainText[:j]
                        break
                self.segmentResult.append(unsafePrefixes)
                self.Segment_unsafe(remainText[len(unsafePrefixes):], trie)
                self.segmentResult.pop()
            else:
                if FirstChar in string.ascii_letters+string.digits+string.printable:
                    
                    for i in string.punctuation,string.whitespace,string.ascii_letters,string.digits:
                        if FirstChar in i:
                            remain,othersCharResult = self.isOtherChar(FirstChar,remainText,i)

                    self.segmentResult.append(othersCharResult)
                    self.Segment_safe(remain, trie)
                    self.segmentResult.pop()
                
                else:
                    self.segmentResult.append(remainText[0])
                    self.Segment_unsafe(remainText[1:], trie)
                    self.segmentResult.pop()
        else :
            self.globalResult.append(list(self.segmentResult))
                    
    def isLeadingChar(self, ch):
        # 0E4E 0e4F 0e5a 0e5b
        thai_unicode_char = u'กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรฤลฦวศษสหฬอฮฯะ ัาำ ิ ี ึ ื ุ ู ฺ ฿เแโใไๅๆ ็ ่ ้ ๊ ๋ ์ ํ ๐๑๒๓๔๕๖๗๘๙' + u"\u0e4e\u0e4f\u0e5a\u0e5b"
        return ch in thai_unicode_char.replace(" ","")
        # return ch in u'กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรลวศศษสหฬอฮะึาิูแุีเัโไใ ่ ้ ๊ ๋ ำ็ฤ์ฦํฯืๆ ฺ '.replace(" ","")
        # return ord(ch) >= ord('ก'.decode('utf-8')) and  ord(ch) <= ord('ฮ'.decode('utf-8'))
   
    def isOtherChar(self,first,remain,ch):
        if first in ch:
            j = 0
            while remain[j] in ch:
                j+=1
                if len(remain) == j:
                    break
            return remain[j:], remain[:j]
   
    def PBI(self):
        prv = 0
        for i in range(0,len(self.segmentResult)):
            if prv == 0:
                self.setResult.add((prv,self.segmentResult[i]))
                prv += len(self.segmentResult[i])
            else:
                self.positive_backtrack[prv] = True
                self.setResult.add((prv,self.segmentResult[i]))
                prv += len(self.segmentResult[i])
   
    def checkPBI(self,curID):
        if (curID in self.positive_backtrack):
            self.PBI()
            return True
    
    def checkNBI(self,curID):
        if curID in self.negative_backtrack:
            return True


# Putting altogether GramTrie and SegmentAlgorithm to function as Segmentation
class SwathC(AWS.PrototypeGramSegment):
    def __init__(self, GramTrieClass, SegmentAlgorithmClass):
        self.GramTrie = GramTrieClass()
        self.SegmentAlgorithm = SegmentAlgorithmClass()
        # also assert if trying to create other type of class
        assert isinstance(self.GramTrie, AWS.AbstractGramTrie)
        assert isinstance(self.SegmentAlgorithm, AWS.AbstractSegmentAlgorithm)
    
    def Segment(self, toBeSegmentInput, Mode):
        # Call SegmentAlgorithm to segment by passing GramTrie
        Output, Mode = self.SegmentAlgorithm.Segmenting(toBeSegmentInput, self.GramTrie.Trie, Mode)
        return Output,Mode

if __name__ == '__main__':
    # example of calling WordSegment
    WordSegment = SwathC(SwathDicTrie,SwathSegmentAlgorithm)
   
    text = sys.argv[1]
    result = WordSegment.Segment(text,"SafeBounding")

    if (len(sys.argv)-1) != 2:       
        result = WordSegment.Segment(text,"Smart") 
    elif sys.argv[2]:
        mode = sys.argv[2]
        result = WordSegment.Segment(text,mode) 

    jsonResult = {}
    jsonResult["Mode"] = result[0]
    Solutions = []
    for segs in result[1]:
        res = []
        for seg in segs:
            res.append(seg)
        Solutions.append(res)
    jsonResult["Solutions"]=Solutions
    
    print (json.dumps(jsonResult,ensure_ascii=False))
