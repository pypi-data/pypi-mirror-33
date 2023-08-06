# Lo4container

The simplest IoC in python

## Install

```
pip install lo4container
```

## Usage

Creating a container is matter of creating a `Container` instance

```
from lo4container import Container
container = Container()
```

### Assign value

We can use `container` as a dictionary, it means you can assign/get value by key, check existing, ...

```
container['name'] = 'lo4container'
print(container['name'])
# output: 'lo4container'

'name' in container
# return True
```

If we use lambda function for value, it would execute with `container` as argument

```
import datetime
container['timer'] = lambda c: return datetime.datetime.now()

print(container['time'])
# output: 2018-07-07 14:05:59.941780
```

Each time you get a value by key, lo4container returns a differences instance. If you want the same instance to be returned for all calls, use `share` method

```
import datetime
container['timer'] = lambda c: return datetime.datetime.now()
container.share('timer')

print(container['time'])
# output: 2018-07-07 14:05:59.941780

print(container['time'])
# output: 2018-07-07 14:05:59.941780

print(container['time'])
# output: 2018-07-07 14:05:59.941780
# same results for n calls
```