Basic usage
----------------------------------------
In order to compute audio features regarding a certain track, you just have to
create an instance of your desired track object and then call its
:code:`extract()` method with the path to an audio file. Considre the following
example:

.. code-block:: python

   from comsar.tracks import TimbreTrack

   tt = TimbreTrack()
   res = tt.extract('path/to/my_audio.wav')
   res.to_pickle('my_features.pkl')

The first line imports the desired Track object, in this case a
:code:`TimbreTrack`. The third line creates a :code:`TimbreTrack` instance
with the name :code:`tt`. The fourth line calls the :code:`extract` method of
:code:`tt` and passes it the path to an actual audio file. comsar then
processes the audio file and makes the results available under the name
:code:`res`. The fifths line eventually saves the results to disc.
