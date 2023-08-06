
from tnthai.swathclone.SCDict import SwathDicTrie 
from tnthai.swathclone.SCDict import SwathSegmentAlgorithm 
from tnthai.swathclone.SCDict import SwathC 

segmenter = SwathC(SwathDicTrie, SwathSegmentAlgorithm)

def SafeSegment(text):
    return segmenter.Segment(text,"Safe")

def UnsafeSegment(text):
    return segmenter.Segment(text,"Unsafe")

def SmartSegment(text):
    return segmenter.Segment(text,"Smart")

def SafeSegmentBounding(text):
    return segmenter.Segment(text,"SafeBounding")
