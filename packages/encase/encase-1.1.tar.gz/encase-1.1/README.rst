######
Encase
######


.. image:: https://travis-ci.org/RyanMillerC/encase.svg?branch=master
    :target: https://travis-ci.org/RyanMillerC/encase

An extension of the Python built-in Dictionary class for working with large
datasets.


Features
========

The Encase class is used to create dictionary objects with:

* Attribute access via dot (.) notation
* Nested instances
* Recursive conversion for existing dictionaries, including nested lists of
  dictionaries

This allows key/value pairs to be accessed like instance attributes, which
makes code dealing with APIs that return large amounts of JSON easier to read
and write. Instead of writing,

``relevant_data = api_result['data']['subset']['subsubset']``

you can accomplish the same with,

``relevant_data = api_result.data.subset.subsubset``.


Installation
============

Install this package using pip:

``pip install encase``


Documentation
=============

Encase is an extension of the Python dictionary class and therefore inherits
all attributes and methods of regular dictionary objects. This also means that
an Encase instance can be used as a drop in replacement for a dict object.

Usage
-----

Basic Usage
::

    >>> from encase import Encase
    >>> d = Encase()
    >>> d.hello_world = "Hello World!"
    >>> print(d.hello_world)
    Hello World!

Instances can also be nested
::
    >>> d.child = Encase()
    >>> d.child.message = "Encase Instances can be nested"
    >>> print(d.child.message)
    Encase Instances can be nested

Methods
-------

get(key)
""""""""
Return value of attribute at 'key'. This is the method form of using,
``encase.child``. This can be used when you won't know a key name prior and
need to use a variable for 'key'.

``param str key``
    Name of attribute whose value will be returned

set(key, value)
"""""""""""""""
Set value of attribute at 'key'. This is the method form of using,
``encase.child = 'Value'``. This can be used when you won't know key name prior
and need to use a variable for 'key'.

``param str key``
    Name of attribute to set
``param str value``
    Value to set for attribute

    
Examples
========

Create a JSON File from Encase instance:
::

    >>> import json
    >>> j = Encase()
    >>> j.data = Encase()
    >>> j.data.info = "JSON can be converted into nested Encases"
    >>> j.data.features = []
    >>> j.data.features.append('Recursively transform dictionaries')
    >>> j.data.features.append('Supports recursion through lists as well')
    >>> j.data.features.append(Encase())
    >>> j.data.features[2].example = "Example of a Encase in a list"

    >>> print(j)
    {
      'data': {
        'info': 'JSON can be converted into nested Encases',
        'features': [
          'Resursively transform dictionaries into Encases',
          'Supports recursion through lists as well',
          {
            'example': 'Example of a Encase in a list'
          }
        ]
      }
    }

    >>> with open('example.json', 'w') as stream:
    ...   json.dump(j, stream)

Read a JSON File into Encase instance:
::

    >>> with open('example.json', 'r') as stream:
    ...     j_data = json.load(stream)

    >>> j_stack = Encase(j_data)
    >>> print(j_stack.data.info)
    JSON can be converted into nested Encases

    >>> for item in j_stack.data.features:
    ...     print(item)
    ...
    Resursively transform dictionaries into Encases
    Supports recursion through lists as well
    {'example': 'Example of a Encase in a list'}

    >>> print(j_stack.data.features[2].example)
    Example of a Encase in a list


Author
======

Ryan Miller - ryan@devopsmachine.com
