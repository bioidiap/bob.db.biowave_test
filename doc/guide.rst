.. vim: set fileencoding=utf-8 :
.. @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
.. @date:   Thu Dec  6 12:28:25 CET 2012

==============
 User's Guide
==============

This package contains the access API and descriptions for the BIOWAVE_ database.
It only contains the Bob_ accessor methods to use the DB directly from python, with our certified protocols.
The actual raw data for the BIOWAVE_ database should be downloaded from the original URL.


The Database Interface
----------------------

The :py:class:`bob.db.biowave.Database` complies with the standard biometric verification database as described in :ref:`commons`, implementing the interface :py:class:`bob.db.verification.utils.SQLiteDatabase`.

.. todo::
   Explain the particularities of the :py:class:`bob.db.biowave.Database`.


.. _bob: https://www.idiap.ch/software/bob
