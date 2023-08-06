# css-class-names [![Build Status](https://travis-ci.org/arturfsousa/css-class-names.svg?branch=master)](https://travis-ci.org/arturfsousa/css-class-names)

A python script for css class names conditional generation. Inspered by the node package [classnames](https://github.com/JedWatson/classnames).

## Why?

The node `classnames` package has been helping me a lot with `React/JSX` and general javascript front-end development. I really missed something similar to use when working with `django` and `jinja2` templates, so, I decided to create this package.

## Usage

You can add css class names by calling the function with arguments as:

* Strings
* Numbers: Floats or Integers (0 is allowed)
* Sequences: Lists or Tuples
* Dictionaries

```python
from css_class_names import class_names

class_names('header', 'is-visible') # 'header is-visible'
class_names(['is-visible', 'text-uppercase']) # 'is-visible text-uppercase'
class_names((100001000, 'clear')) # '100001000 clear'

class_names('header', { 
    'header--is-fixed': True, 
    'header--is-blue': False 
}) 
# 'header header--is-fixed'
```

### Conditional dicts

Dictionaries can be used to concat class names conditionally using expressions:

```python
from css_class_names import class_names

errors = ['Some error']
class_names('alert', { 
    'alert-danger': errors, 
    'alert-success': not errors,
    'small': True
}) 
# 'alert alert-danger'

class_names('client', { 
    'client-{}'.format(client.id): client, 
    'disable': not client.active()
}) 
# 'client client-989'
```

### Excludes falsy values

Falsy values (except 0) and not supported types will be ignored:

```python
from css_class_names import class_names

class_names([], '', False, {}, 0, object(), lambda x: x, None)
# '0'
```

### Strip and flatten

Strings are striped and sequences are recursively flattened:

```python
from css_class_names import class_names

class_names([' header   ', ['  green ', ' small ']])
# 'header green small'
```

### Dedupe

You can dedupe names with the `dedupe` argument:

```python
from css_class_names import class_names

class_names('cart', 'is-open', 'is-logged', {'is-logged': True}, dedupe=True)
# 'cart is-open is-logged'
```

### Prefix

You can add class name prefixes with the `prefix` argument. This is really usefull when you need a class namespace or using the [BEM](http://getbem.com/) methodology:

```python
from css_class_names import class_names

class_names('head', 'head--is-empty', {'head--is-large': True}, prefix='mysite-')
# 'mysite-head mysite-head--is-empty mysite-head--is-large'
```

## Development

After cloning the repository, create a virtualenv and use the `Makefile` commands to `setup` development requirements and run tests:

```bash
make setup
make lint 
make test 
make watch # run tests when code changes
make coverage
```
