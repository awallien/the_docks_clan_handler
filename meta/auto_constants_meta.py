"""
Developer's Note:

I realized that through out my development on this project, I have been using Python's enum 
with the wrong intention.

In Python's enum, each member has an associated value, but the variable name itself is not assigned 
to that value, but rather, it's just a symbolic identifier for the member.

For instance:

from enum import Enum
class Foo(Enum):
 ONE = 1
 TWO = 2
 THREE = 3

Foo.ONE doesn't actually equal to 1 as described in this enum class. It is a separate member:

>>> Foo.ONE
<Foo.ONE: 1>

To get the actual value '1', you have to call its value:
>>> Foo.ONE.value
1

What's really annoying about using enum is the constant calls to the member's value if I intend to use
the actual value rather than the name of the member. 
This article pretty much explains my frustration when working with Python's enum:
https://www.cosmicpython.com/blog/2020-10-27-i-hate-enums.html


What I was looking for when I wanted to group members and access their values is basically a dictionary 
but making it look like a fancy class, where members in the class actually return its assigned value.
For instance I have Ranks and I wanted to call something like Ranks.RANK_3 to get the 3rd rank, which is
simply '3'. I wanted only the '3' value, but I have to use Ranks.RANK_3.value to get the actual value.
This resulted in my project flooded with .value calls, and it began to too ugly.

To combat this, instead of Python's enum, the meta class below handles bundling all the values I'm
using in a class so I don't have to statically assign specific values to clusters, such as in my 
Rank class I bundle Ranks 1-4, 5-15, etc. All of the "constants" will be assigned under "__constants__"
for any classes that uses this metaclass.
"""
import types

class AutoConstantsMeta(type):
    def __new__(cls, name, bases, class_dict):
        values = [
            v for k,v in class_dict.items()
            if not k.startswith("__") 
            and not isinstance(v, (types.FunctionType, classmethod, staticmethod, property))
        ]
        class_dict["__constants__"] = values
        return super().__new__(cls, name, bases, class_dict)
