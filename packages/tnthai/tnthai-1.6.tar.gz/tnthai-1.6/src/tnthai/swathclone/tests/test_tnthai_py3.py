#!/usr/bin/env python
#  -*- coding: UTF-8 -*-

import unittest

try:
    import tnthai.segment as tn
except ImportError:
    raise ImportError("Can't import package please check site-packages in your python directory") 

# result,mode = segmenter.Segment("ทดสอบการทำงานของระบบ") 
class TestPostInstall(unittest.TestCase):
    def test_is_work_case_one(self):
        safe_one = tn.SafeSegment("ทดสอบการทำงานของระบบ")
        safe_two = tn.SafeSegment("ทดสอบกฮารทำงานของระบบ")
        unsafe = tn.UnsafeSegment("ทดสอบการทำงานของระบบ")
        smart_one = tn.SmartSegment("ทดสอบการทำงานของระบบ")
        smart_two = tn.SmartSegment("ทดสอบกฮารทำงานของระบบ")

        self.assertEqual(safe_one[1][1][0],"ทดสอบ")
        self.assertEqual(safe_one[0],"Safe")
        print ("\nCase 1: \nSuccess in SafeSegment with spellings")
        self.assertEqual(safe_two[1],[])
        self.assertEqual(safe_two[0],"Safe")
        print ("Success in SafeSegment with misspellings")
        self.assertEqual(unsafe[1][0][4],"ระบบ")
        self.assertEqual(unsafe[0],"Unsafe")
        print ("Success in UnsafeSegment")     
        self.assertEqual(smart_one[1][1][0],"ทดสอบ")
        self.assertEqual(smart_one[0],"Safe") 
        print ("Success in SmartSegment with spellings")   
        self.assertEqual(smart_two[1][0][2],"ฮา")
        self.assertEqual(smart_two[0],"Unsafe") 
        print ("Success in SmartSegment with missspellings")

    def test_is_work_case_two(self):
        safe_one = tn.SafeSegment("คนแก่ขนของ")
        safe_two = tn.SafeSegment("คนแก่สขนของ")
        unsafe = tn.UnsafeSegment("คนแก่ขนของ")
        smart_one = tn.SmartSegment("คนแก่ขนของ")
        smart_two = tn.SmartSegment("คนแก่สขนของ")

        self.assertEqual(safe_one[1][0][1],"ขนของ")
        self.assertEqual(safe_one[0],"Safe")
        print ("\nCase 2: \nSuccess in SafeSegment with spellings")
        self.assertEqual(safe_two[1],[])
        self.assertEqual(safe_two[0],"Safe")
        print ("Success in SafeSegment with misspellings")
        self.assertEqual(unsafe[1][0][1],"ขนของ")
        self.assertEqual(unsafe[0],"Unsafe")
        print ("Success in UnsafeSegment")     
        self.assertEqual(smart_one[1][3][3],"ของ")
        self.assertEqual(smart_one[0],"Safe") 
        print ("Success in SmartSegment with spellings")   
        self.assertEqual(smart_two[1][0][1],"ส")
        self.assertEqual(smart_two[0],"Unsafe") 
        print ("Success in SmartSegment with missspellings") 

if __name__ == '__main__':
    unittest.main()