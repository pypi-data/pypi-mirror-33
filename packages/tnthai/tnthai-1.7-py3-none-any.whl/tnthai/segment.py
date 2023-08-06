from tnthai.swathclone.SC import SwathC
from tnthai.swathclone.SC import SwathDicTrie 
from tnthai.swathclone.SC import SwathSegmentAlgorithm 

segmenter = SwathC(SwathDicTrie, SwathSegmentAlgorithm)

def SafeSegment(text):
    return segmenter.Segment(text,"Safe")

def UnsafeSegment(text):
    return segmenter.Segment(text,"Unsafe")

def SmartSegment(text):
    return segmenter.Segment(text,"Smart")

def SafeSegmentBounding(text):
    return segmenter.Segment(text,"SafeBounding")