Spectral AEAD
=============

Spectral is algorithm for authenticated encryption with associated data;
it uses
`Speck <https://csrc.nist.gov/csrc/media/events/lightweight-cryptography-workshop-2015/documents/papers/session1-shors-paper.pdf>`__
in `CTR
mode <https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38a.pdf>`__
as the underlying cipher (with a 128-bit block size and a 128-bit key
size) along with
`HMAC <https://nvlpubs.nist.gov/nistpubs/fips/nist.fips.198-1.pdf>`__-`SHA256 <https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf>`__
in an `Encrypt-then-MAC <https://www.iso.org/standard/46345.html>`__
construction.

This package provides tested, performant **Python 3** CFFI bindings to
an implementation of Spectral, including abstractions for simplified
encryption and decryption.

Installation
============

You can install this package using ``pip`` or the included ``setup.py``
script:

::

   # Using pip
   pip install spectral-aead

   # Using setup.py
   python setup.py install

Usage
=====

.. code:: python

   from spectral import *

   # Demonstration key, nonce, plaintext and associated data
   key = b"\0" * spectral.KEY_SIZE
   nonce = b"\0" * spectral.NONCE_SIZE
   plaintext = b"\0" * 16
   associated = b"\0" * 16

   # Spectral simplified encryption
   encrypted = encrypt(key, plaintext, associated)  # Associated data is optional

   # Spectral simplified decryption
   computed_plaintext = decrypt(key, encrypted, associated)  # Raises RuntimeError if any parameter has been tampered with
   assert plaintext == computed_plaintext

   # Spectral disjoint encryption
   ciphertext, mac = encrypt_disjoint(key, nonce, plaintext, associated)  # Associated data is optional

   # Spectral disjoint decryption
   computed_plaintext = decrypt_disjoint(key, nonce, ciphertext, mac, associated)  # Raises RuntimeError if any parameter has been tampered with
   assert plaintext == computed_plaintext

License
=======

.. code:: text

   Copyright (c) 2018 Phil Demetriou

   Permission is hereby granted, free of charge, to any person obtaining a copy
   of this software and associated documentation files (the "Software"), to deal
   in the Software without restriction, including without limitation the rights
   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
   copies of the Software, and to permit persons to whom the Software is
   furnished to do so, subject to the following conditions:

   The above copyright notice and this permission notice shall be included in all
   copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
   SOFTWARE.
