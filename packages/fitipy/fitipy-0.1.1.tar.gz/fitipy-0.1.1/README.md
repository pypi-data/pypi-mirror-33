# Fitipy

This small python module is used to eliminate checks if a file exists and casts
to and from a string. It applies a [redis](https://redis.io)-style interface 
to the filesystem.

## Installation

```bash
pip3 install fitipy
```

## Example

```python
from fitipy import Fitipy

fi = Fitipy('data')
users = fi.read('users.txt').set()  # Returns Python set object
users.add('sue')
fi.write('users.txt').set(users)

```

Compared to the raw Python:

```python
from os import makedirs
from os.path import isfile, join

if isfile(join('data', 'users.txt')):
    with open(join('data', 'users.txt')) as f:
        users = set(f.read().split('\n'))
else:
    users = set()
users.add('sue')
makedirs('data', exist_ok=True)
with open(join('data', 'users.txt'), 'w') as f:
    f.write('\n'.join(users))

```
