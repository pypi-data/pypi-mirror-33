py-cpp-demangle: Demangles C++ linker symbols
============================================================

A package for demangling C++ linker symbol strings

This package provides python bindings for the rust crate
`cpp_demangle <http://github.com/gimli-rs/cpp_demangle>`_ by building
a native Python extension using `PyO3 <https://github.com/pyO3/pyO3>`_.

This is mainly an experiment in creating python extensions in Rust.
More info (and possibly a blog post) coming soon maybe.

Usage
-------------------

To install

.. code-block:: python

    pip install cpp-demangle


Building from source requires the nightly version of the rust compiler.

This module exposes a single function that transforms C++ linker symbols to a human readable
representation.

.. code-block:: python

    from cpp_demangle import demangle

    print(demangle('_ZN7mangled3fooEd'))
    # prints 'mangled::foo(double)'

Released under the MIT License
