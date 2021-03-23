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


Basic usage
----------------------------------------
 In order to compute timbre features, for example, you just have to create an
 TimbrTrack instance and then call its `extract()` method with the path to an
 audio file.

.. code-block:: python

   from comsar.tracks import TimbreTrack

   tt = TimbreTrack()
   res = tt.extract('path/to/my_audio.wav')
   res.to_pickle('my_features.pkl')

Each track implements the same interface.

Source code
----------------------------------------
The source code is available at the GitHub Repository.

It is published under the permisive `BSD 3-Clause License`_. You may change and
republish the code for any personal or commercial project.

.. _BSD 3-Clause License: https://opensource.org/licenses/BSD-3-Clause


.. toctree::
   :hidden:
   :maxdepth: 2
  
   install
   tracks
