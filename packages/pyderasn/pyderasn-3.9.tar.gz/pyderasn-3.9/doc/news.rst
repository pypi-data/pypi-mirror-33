News
====

.. _release3.9:

3.9
---
* SEQUENCE's values are printed with field's name. Previously there was
  the following output::

    AlgorithmIdentifier SEQUENCE[OBJECT IDENTIFIER 1.3.14.3.2.26, [UNIV 5] ANY 0500 OPTIONAL]

  now it is::

    AlgorithmIdentifier SEQUENCE[algorithm: OBJECT IDENTIFIER 1.3.14.3.2.26; parameters: [UNIV 5] ANY 0500 OPTIONAL]
* Fixed EOC (Unicode character) repr printing issues under Python2

.. _release3.8:

3.8
---
BER's EOC is explicitly shown during pprinting. Following notation::

      15-2 [0,0,1576]-4  . content: [0] EXPLICIT [UNIV 16] ANY

is replaced with::

      15-2∞ [0,0,1576]∞  . content: [0] EXPLICIT [UNIV 16] ANY
    [...]
    1587    [1,1,   0]   . content:  BER EOC
    1589    [1,1,   0]   . content: EXPLICIT BER EOC

.. _release3.7:

3.7
---
* BER decoding support
* BitString's ''H notation support
* ``termcolor`` package is included in the tarball

.. _release3.6:

3.6
---
* Ability to set values during Sequence initialization

.. _release3.5:

3.5
---
* Fix TagMismatch exception completeness during Choice and Set decoding
  Previously we will loose offset and decode_path information about
  concrete TagMismatched entity

.. _release3.4:

3.4
---
* Strict NumericString's value sanitation
* Invalid encoding in string types will raise ``DecodeError`` exception,
  instead of ``Unicode*Error``
* Fixed DecodePathDefBy workability with Python 2.x

.. _release3.3:

3.3
---
* Fix nasty BitString decoding bug: it could fail when data follows
  encoded BitString value. There weren't any problems when BitString is
  at the end of Sequence

.. _release3.2:

3.2
---
* Slightly corrected colours, now visible on white background

.. _release3.1:

3.1
---
* Fix bug related to DecodeError showing with DecodePathDefBy entities
* Respect ``NO_COLOR`` environment variable

.. _release3.0:

3.0
---
* :py:func:`pyderasn.decode_path_defby` is replaced with
  :py:class:`pyderasn.DecodePathDefBy`
* Ability to turn colourized terminal output by calling
  ``pprint(..., with_colours=True)``. You will need
  `termcolor package <https://pypi.org/project/termcolor/>`__

.. _release2.1:

2.1
---
* Fixed invalid offset calculation when dealing with DEFINED BY objects
  having explicit tags

.. _release2.0:

2.0
---
* BIT STRINGs can also be :ref:`DEFINED BY <definedby>`
* Decoding process can be governed with optional :ref:`ctx <ctx>`
  keyword argument to ``decode()`` method
* :ref:`defines_by_path <defines_by_path_ctx>` option is now
  :ref:`decode context <ctx>` option, not a keyword argument
* Ability to do :ref:`strict validation <strict_default_existence_ctx>`
  of defaulted values met in sequence, raising an exception

.. _release1.6:

1.6
---
Ability to skip specified number of bytes (``--skip``) in command line
utility.

.. _release1.5:

1.5
---
* Generic decoder's scheme and pretty printer
  (:py:func:`pyderasn.generic_decoder`) can be used in libraries
* Ability to specify :ref:`defines_by_path <defines_by_path_ctx>`
  during command line invocation

.. _release1.4:

1.4
---
Ability to automatically decode :ref:`DEFINED BY <definedby>` fields
inside SEQUENCEs.

.. _release1.3:

1.3
---
Removed ``__lt__``/``__eq__`` from base class, as pylint likes it.

.. _release1.2:

1.2
---
Full rich comparison operators added.


.. _release1.1:

1.1
---
Trivial README addition.

.. _release1.0:

1.0
---
Initial release.
