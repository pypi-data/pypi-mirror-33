Introduction
============

dgsamples is a package of sample image chips and vector files that can
be used for unit testing without having to maintain test data in each
code base that needs to be tested.

Quick Start
===========

.. code:: python

  import dgsamples
  
  # The code automatically discovers the data available and puts it on a 
  # bunch object called samples which can be accessed directly:
  dgsamples.allsamples   # This will pretty print the contents of the bunch
  
  # Finer grained access to the samples can be achieved by:
  dgsamples.wv2_longmont_1k.files
  # The above will produce a path similar to: 
  # /path/to/dgsampledata/wv2_longmont_1k/...M2AS-053792616010_01_P001.TIL'
  # /path/to/dgsampledata/wv2_longmont_1k/...P2AS-053792616010_01_P001.TIL'
  
  # If the samples have a filename_map.PVL file provided, there will also be
  # sensor specific shotcuts available in an OrderedBunch object:
  dgsamples.wv2_longmont_1k.ms
  # The above will produce a path to the sensor .TIL file:
  # /path/to/dgsampledata/wv2_longmont_1k/...M2AS-053792616010_01_P001.TIL'
  
  # The .TIL file can be ingested with geoio as:
  import geoio
  img = geoio.DGImage(dgsamples.wv2_longmont_1k.ms)

  # However, these links are to real files on disk and can be read with
  # an appropriate application.
  from osgeo import gdal
  obj = gdal.Open(dgsamples.bayou_chip.extract_test)

  # or
  import fiona
  s = fiona.open(dgsamples.bayou_vectors.poly)
  
  # The sample data can also be retrieved through the "file" bunch key:
  dgsamples.bayou_vectors.files
  # The above will produce something similar to:
  # ['/path/to/dgsampledata/.../extract_test_point.shp',
  #  '/path/to/dgsampledata/.../extract_test_poly.shp']

Adding Data Sets
================

New data can be added directly into the "dgsamples" package and will be
dynamically discovered on import.  The dynamic discovery code uses the
following logic when determining what type of data exists in a directory:

.. code:: python

    if ".TIL found":
        "return all .TILs and stop"
    elif ".TIF found" :
        "return all .TIFs and stop"
    elif ".shp or .json found" :
        "return all .shp and .json then stop"

If a file named "filename_map.PVL" is added to a sample directory, the key/
value pairs in the file will be used to map files to an key entry on the
returned OrderedBunch object.

If a file named "notes.txt" is present in the sample directory, the content
will be added to a "notes" entry on the OrderedBunch object.
