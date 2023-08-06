# nr.types

A collection of useful Python datatypes, including enumerations, generics,
enhanced mappings, meta-programming tools and sumtypes.

## Changes

### 1.0.6 (2018-07-14)

* Default values in annotated fields specified in subclasses of the
  `nr.types.named.Named` class can now be functions in which case they
  behave the same as passing that function to a `Named.Initializer`
* Add `HashDict` class to `nr.types.map`

### 1.0.5 (2018-07-05)

* Add missing requirement `six` to `setup.py` and `requirements.txt`

### 1.0.4 (2018-06-29)

* Add `nr.types.function` module
* Add `nr.types.generic` module
* Make `nr.types.named` module Python 2.6 compatible
* Fix `ObjectAsMap.__new__` and `MapAsObject.__new__`

### 1.0.3 (2018-06-03)

* Hotfix for the `__version__` member in the `nr.types` module

### 1.0.2 (2018-06-03)

* Setup script Python 2 compatibility
