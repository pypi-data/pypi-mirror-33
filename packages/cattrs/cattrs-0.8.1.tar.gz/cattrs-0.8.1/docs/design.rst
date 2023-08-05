==============================
Design decisions and internals
==============================

The core of ``cattrs`` (both structuring and unstructuring) is organized around
Python's singledispatch_.
Singledispatch links classes to their handling functions; on a high level, this
is what ``cattrs`` fundamentally is: a collection of handler functions mapped
to types.

Using only ``singledispatch`` creates several problems, though.

* At times, we need to use different criteria than types and subtypes. For example,
``attrs`` classes don't have a common ancester, but they do have a special ``__attrs_attrs__`` attribute.
* Depending on the versions of Python and the ``typing`` module,

.. _singledispatch: https://docs.python.org/3/library/functools.html#functools.singledispatch