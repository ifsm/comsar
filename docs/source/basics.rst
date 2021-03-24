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
