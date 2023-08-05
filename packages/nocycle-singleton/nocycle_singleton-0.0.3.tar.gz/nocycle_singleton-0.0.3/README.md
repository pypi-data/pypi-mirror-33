# my_singleton Package

This is a simple singleton.
Borg pattern can achieve this aim by share state,
however it can't solve this problem in which 2 objects refer circularly.

```
e.g. 
obj = object
Class A(obj):
    def __init__(self):
        self.b_obj = B()

Class B(obj):
    def __init__(self):
        self.a_obj = A()

when we define c = A(),
there must be a err.

but,
if obj = my_singleton,
from nocycle_singleton.singleton import Singleton as my_singleton,

we can solve this. 
```