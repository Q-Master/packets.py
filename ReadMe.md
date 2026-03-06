packets - pure python declarative packes system for serializing/deserializing
===

`packets` is my own view of declarative description of serializable/deserializable objects.

The main idea of this project is to give easiness of managing serializable objects in declarative way
without any need to implement type checking, defaults, serializing and deserializing of objects.

Installation

---
You can use `pip` package manager to install `packets`. The most recent
version of the library can be installed directly from Git repo:

```bash
pip install git+https://github.com/Q-Master/packets.py.git
```

Usage

---
Mostly usage examples could be seen in tests directory.
The `packets` requires `ujson`, but it is not a strict requirement.

```python
from typing import Optional
from packets import Packet, makeField, 
from packets.typedef.int_t import int_t
from packets.typedef.string_t import string_t

class Parent(Packet):
    field1: int = makeField(int_t, 'a', required=True)


class Child(Parent):
    field1: int = makeField(int_t, default=3, override=True)

class Show(Packet):
    field1: int = makeField(int_t, required=True)
    field2: Optional[str] = makeField(string_t)

parent = Parent(field1=2)
packet = Child()

show = Show.load({'field1': 1})
show2 = Show.load({'field1': 1, 'field2': 'show must go on'})

print('Parent:')
print(parent)
print(parent.dump())
print('Child:')
print(packet)
print(packet.dump())
print('Show:')
print(show)
print(show.dump())
print(show2)
print(show2.dump())
```
