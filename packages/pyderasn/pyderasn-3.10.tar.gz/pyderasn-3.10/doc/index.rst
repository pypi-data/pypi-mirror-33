============================================
PyDERASN -- ASN.1 DER/BER library for Python
============================================

..

    I'm going to build my own ASN.1 library with slots and blobs!
    (C) PyDERASN's author

`ASN.1 <https://en.wikipedia.org/wiki/ASN.1>`__ (Abstract Syntax
Notation One) is a standard for abstract data serialization. PyDERASN is
yet another library for dealing with ASN.1 structures, decoding them in
`BER/CER/DER <https://en.wikipedia.org/wiki/X.690>`__ formats and
encoding to DER (Distinguished Encoding Rules). Although ASN.1 is
written more than 30 years ago by wise Ancients (taken from ``pyasn1``'s
README), it is still often can be seen anywhere in our life.

PyDERASN is `free software <https://www.gnu.org/philosophy/free-sw.html>`__,
licenced under `GNU LGPLv3+ <https://www.gnu.org/licenses/lgpl-3.0.html>`__.

.. figure:: pprinting.png
   :alt: Pretty printing example output

   An example of pretty printed X.509 certificate with automatically
   parsed DEFINED BY fields.

.. toctree::
   :maxdepth: 1

   features
   examples
   reference
   news
   install
   download
   thanks
   feedback
