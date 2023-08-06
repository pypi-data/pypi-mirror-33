# klab-autotime
Time everything in IPython

## Installation:

use pip

## Examples

```python
Installed autotime.py. To use it, type:
  %load_ext klab-autotime

In [2]: %load_ext klab-autotime
time: 1433692.87 s

In [3]: x = 1
time: 730.99 us

In [4]: x + 2
Out[4]: 3
time: 2.50 ms

In [5]: x + ''
---------------------------------------------------------------------------
TypeError                                 Traceback (most recent call last)
<ipython-input-5-bde712cacec5> in <module>()
----> 1 x + ''

TypeError: unsupported operand type(s) for +: 'int' and 'str'
time: 156.05 ms
```

## Want to turn it off?

```python
In [5]: %unload_ext klab-autotime
```
# klab-autotime
