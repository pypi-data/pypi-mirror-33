.. _bitprim-native-python-api-versionbadge.version-travis-statusbadge.travis-appveyor-status-gitter-chatbadge.gitter:

Bitprim Native-Python-API \ |Version|\  \ |Travis status|\  |Appveyor Status| \ |Gitter Chat|\ 
===============================================================================================

    CPython extension module building block.

*Bitprim Native-Python-API* is a `CPython`_ extension module written C++
thought as a building block for the `Bitprim Python-API`_.

**This library is not intended for the end user, so we encourage to take
a look at `Bitprim Python-API`_.**


Getting started 
---------------

Stable version:

.. code-block:: bash

    $ pip install --upgrade bitprim-native

Development version:

.. code-block:: bash

    $ pip install --upgrade --index-url https://test.pypi.org/pypi/ bitprim-native


If you want a fully optimized binary for a specific microarchitecture, for example:

.. code-block:: bash

    $ pip install --upgrade --install-option="--microarch=skylake" bitprim-native

(use :code:`--index-url https://test.pypi.org/pypi/` for Dev version)


Reference documentation
-----------------------

For more detailed documentation, please refer to `<https://www.bitprim.org/>`_.

.. raw:: html

   <!-- Links -->

.. _CPython: https://en.wikipedia.org/wiki/CPython
.. _Bitprim Python-API: https://github.com/bitprim/bitprim-py

.. |Version| image:: https://badge.fury.io/gh/bitprim%2Fbitprim-py-native.svg
.. |Travis status| image:: https://travis-ci.org/bitprim/bitprim-py-native.svg?branch=master
.. |Appveyor Status| image:: https://ci.appveyor.com/api/projects/status/github/bitprim/bitprim-py-native?svg=true&branch=master
   :target: https://ci.appveyor.com/projects/bitprim/bitprim-py-native
.. |Gitter Chat| image:: https://img.shields.io/badge/gitter-join%20chat-blue.svg
