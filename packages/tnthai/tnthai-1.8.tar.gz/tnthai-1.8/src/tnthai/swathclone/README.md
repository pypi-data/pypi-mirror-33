Prerequisite : python 2.x,3.x

# Installation

```
pip install tnthai
```
# How to Use

In ```tnthai``` package have 3 features ```Safe Mode```, ```Unsafe Mode```, ```Smart Mode```

You can run package in command line by following this command:
```
$ tnthai-run ทดสอบการทำงาน
```
If you want to choose the features you can do by following this command:

```
$ tnthai-run ทดสอบการทำงาน Safe
```
```
$ tnthai-run ทดสอบการทำงาน Unsafe
```
```
$ tnthai-run ทดสอบการทำงาน Smart
```
## Example:
Without mode will automatically use ```Smart Mode```:
```
$ tnthai-run ทดสอบการทำงาน
```
Result:
```
  {"Mode": "Safe", "Solutions": [["ทดสอบ", "การ", "ทำงาน"], ["ทดสอบ", "การ", "ทำ", "งาน"], ["ทด", "สอบ", "การ", "ทำงาน"], ["ทด", "สอบ", "การ", "ทำ", "งาน"]]}
```
```Safe Mode```:
```
$ tnthai-run ทดสอบการทำงาน Safe
```
Result:
```
  {"Mode": "Safe", "Solutions": [["ทดสอบ", "การ", "ทำงาน"], ["ทดสอบ", "การ", "ทำ", "งาน"], ["ทด", "สอบ", "การ", "ทำงาน"], ["ทด", "สอบ", "การ", "ทำ", "งาน"]]}
```
```Unsafe Mode```:
```
$ tnthai-run ทดสอบการทำงาน Unsafe
```
Result:
```
{"Mode": "Unsafe", "Solutions": [["ทดสอบ", "การ", "ทำงาน"]]}
```

## Simple Demo


```
import tnthai.segment as tn


safe = tn.SafeSegment("คนแก่ขนของ")

unsafe = tn.UnsafeSegment("คนแก่ขนของ")

smart = tn.SmartSegment("คนแก่ขนของ")
```
But if you use python2 you need to add ```# -*- coding: utf-8 -*-``` like this:
```
# -*- coding: utf-8 -*-

import tnthai.segment as tnthai

  * code *
    ...
    ...
    ...
```


Result of ```Safe Mode```  will be like this:
```
('Safe', [['คนแก่', 'ขนของ'], ['คนแก่', 'ขน', 'ของ'], ['คน', 'แก่', 'ขนของ'], ['คน', 'แก่', 'ขน', 'ของ']])
```
Result of ```Unsafe Mode```  will be like this:
```
('Unsafe', [['คนแก่', 'ขนของ']])
```
To show you how its work we will show you an example:
```
import tnthai.segment as tn


misspellings_safe = tn.SafeSegment("คนแก่สขนของ")

spellings_smartmode = tn.SmartSegment("คนแก่ขนของ")

misspellings_smartmode = tn.SmartSegment("คนแก่สขนของ")
```
```Safe Mode``` doesn't work with misspellings text so the 
result will be empty list ( ```Smart Mode``` can solve this problem )

The result of ```misspellings_safe``` is:
```
('Safe', [])
```

```Smart Mode```  will automatically use ```Safe Mode```  but if its doesn't work (which mean text have misspellings) its going to use ```Unsafe Mode```  instead


The result of ```spellings_smartmode``` is:
```
('Safe', [['คนแก่', 'ขนของ'], ['คนแก่', 'ขน', 'ของ'], ['คน', 'แก่', 'ขนของ'], ['คน', 'แก่', 'ขน', 'ของ']])
```
The result of ```misspellings_smartmode``` is:
```
('Unsafe', [['คนแก่', 'ส', 'ขนของ']])
```

If you want to test package you can run ```tnthai-test``` by following this command:
```
$ tnthai-test
```
