FontMeta
==========

.. image:: https://badge.fury.io/py/fontmeta.svg
    :target: https://badge.fury.io/py/fontmeta

An utility and library to get metadata from TTF/OTF fonts.


============
Installation
============
Via pip:

.. code:: bash

   pip install fontmeta


=====
Usage
=====
Simply Instantiate a ``FontMeta`` object with font's file path. call ``instance.get_full_data()`` for full data and ``instance.get_data()`` for streamlined data.

.. code:: python

   from fontmeta import FontMeta
   meta_instance = FontMeta('path_to_file')


Functions
---------

**get_full_data**
  *Arguments: None*
  Returns full Metadata.

**get_data**
  *Arguments: None*
  Returns only streamlined field name and value in a dict.
