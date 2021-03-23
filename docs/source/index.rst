.. COMSAR documentation master file, created by
   sphinx-quickstart on Fri Feb 19 07:54:14 2021.

Computational Music and Sound Archiving
=======================================
The Computational Music and Sound Archiving system provides high-level audio
feature extraction facilities for multi-viewpoint music similarity analysis.

Music similarity is hard to analyse. A viewpoint highlights certain aspects of
musical perception. Asking for similarity regarding pitch requires another
viewpoint than asking for rhythm similarity.

COMSAR combines pre-selected low-level audio features to *Track*
objects, which represent a viewpoint.


comsar Trask System
---------------------------------------
* :doc:`tracks/pitch_track`
* :doc:`tracks/rhythm_track`
* :doc:`tracks/timbre_track`


Source code
---------------------------------------
The source code is available at the GitHub Repository.

It is published under the permisive `BSD 3-Clause License`_. You may change and
republish the code for any personal or commercial project.

.. _BSD 3-Clause License: https://opensource.org/licenses/BSD-3-Clause


.. toctree::
   :hidden:
   :maxdepth: 2
  
   install
   basics
   tracks/pitch_track
   tracks/rhythm_track
   tracks/timbre_track
   api/modules


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
