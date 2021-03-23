***************************************
Pitch Track
***************************************
The pitch track of the COMSAR framework extracts pitch from a soundfile,
accumulates pitches into an octave, detects notes, vibrato, slurs, or melisma,
determines most likely tonal systems, extracts the melody, and calculates
n-gram histograms.

The pitch track instance should contain the frame size and hop ratio. In the
example notebook 100 pitches per second are analyzed (see jupyter example
notebook **COMSAR_Melody_Example.jpynb**)


Melody, n-grams
=======================================
An example of a Lisu solo flute piece for pitch and melody extraction is shown
in the figure below (ESRA index 626,
https://vimeo.com/showcase/5259277/video/278497941).

.. figure:: ../fig/PitchMelody_Lisu_626.png
   :scale: 50 %
   :alt: Melody Lisu flute solo

   Example of pitch and melody extraction using Lisu flute solo, ESRA index
   626. The analysis has five stages of abstraction. 1) pitches are calculated
   over the whole piece. From pitch values to melodies: 2) top left:
   Pitch contours of detected notes, 3) top right) pitch contour of
   notes allowed for n-grams (melodies), 4) bottom left: mean pitches
   of allowed notes from plot 2) still showing grace-notes, 5) bottom
   right: mean pitches of notes allowed for n-grams.

**In a first analysis stage'**, the original sound files are analyzed with
respect to **pitch**, where n pitch values are calculated per second,
determined by the args used in the instantiation of the pitch track. Pitch
analysis is performed using the autocorrelation method, where the first peak of
the autocorrelation function determines the periodicity of the pitch. 

For frequencies below about 50 Hz the result of the autocorrelation is not
precise. In nearly all cases, the amount of period cycles the autocorrelation
integrates over is not an integer, but a fraction of one period is integrated
over at the end of the sound. With higher frequencies, this is not
considerable. Still, with low frequencies, due to the few sound period cycles
the autocorrelation integrates over, this leads to incorrect results. Here an
algorithm is used to compensate for overintegration. For frequencies above 1.7
kHz, results again are not correct due to the limited sample frequency,
allowing only certain periods. Here, oversampling is performed to compensate
for incorrectness. Still, in most cases, melody falls into the human singing
range, and, therefore, the algorithm does not need these corrections. 

The pitches are transferred into cent, using a fundamental frequency of f0 to
be determined in the args (f0 = 27.5 Hz is recommended for sub contra A) in
noctaves above f0 (noctaves = 8 is recommended), and a cent precision dcent
(dcent = 1 cent is recommended).

**The second abstraction stage** uses an agent-based approach, where **musical
events, notes, grace-notes, slurs, melismas, etc.** are detected. The agent
follows the cent values from the start of each musical piece and concatenates
adjacent cent values according to two constraints, a minimum length (minlen) a
pitch event needs to have and a maximum allowed cent deviation (mindev). So,
e.g., with pitch track instantiated using 100 pitch values per second, a minlen
= 3 is 30 ms minimum note length, and mindev = 60 his allows for including
vibrato and pitch glides within about one semitone, often found in vocal and
some instrumental music. Lowering the allowed deviation often leads to the
exclusion of pitches, which often have quite strong deviations. As an example,
an excerpt of 23 seconds of a Lisu solo flute piece is shown in the figure
below on the top left. Some pitches show a quite regular periodicity, some are
slurs or grace-notes.

**The third abstraction stage** determines **single pitches** for each detected
event by taking the strongest value of a pitch histogram. As can be seen in the
top left figure, often pitches are stable, only to end in some slur in the end.
Therefore, taking the mean of these pitches would not represent the main pitch.
Using the maximum of a histogram, on the other side, detects the pitch most
frequency occurring during the event. On the bottom left, this is performed and
can be compared to the top left plot. When listening to the piece, this
representation seem to contain still too many pitch events. So,. e.g., the
events around 6000 cent are clearly perceived as notes. Still, those small
events preceding around 6200 cent are heard as grace-notes. Therefore, to
obtain a melody without grace-notes, a fourth stage needs to be performed.

**In a fourth stage**, pitch events are selected using three constraints to
allow for **n-gram construction**.  n-grams have shown to represent melodies
stable and robust in terms of melody identification, like e.g., in
query-by-humming tasks. Here, n adjacent notes are clustered in an n-gram. A
musical piece, therefore, has N-n n-grams, where N is the amount of notes in
the piece. The n-grams are not constructed from the notes themselves, but from
the intervals between the notes. Therefore, a 3-gram has two intervals. Also,
the n-grams are sorted in 12-tone just intonation. Therefore, each interval is
sorted into its nearest pitch-class. Further implementations might include
using tonal systems as pitch classes. Usuall,y 2-grams or 3-grams are used,
sometimes up to 5-grams. All n-grams present in a piece are collected in a
histogram, where, in the present study, the nngram most frequent n-grams (ten
in this case) are collected into a feature vector to be fed into the machine
learning algorithm.

So adjacent notes qualifying for n-gram inclusion need to be such to exclude
grace-notes, slurs, etc. This is obtained by demanding the notes to have a
certain length (minnotelength in amount of analysis frames), in the example
below 100 ms is used (minnotelength = 10 as pitch track instantiation with 100
pitches per second was performed). Additionally, a lower (ngcentmin) and upper
(ngcentmax) limit for adjacent note intervals is applied. The lower limit is 0
cent in the example to allow for tone repetition. The upper limit is set to
+-1200 cent here, so two octaves, most often enough for traditional music. This
does not mean that traditional pieces do not have larger intervals, as e.g.,
expected in jodeling. Still, such techniques are not used in the present music
corpus, and even when present, they are not expected to be more frequent than
smaller intervals. In the top right figure, we see the pitch contours for all
allowed notes used in n-gram calculation. Indeed, all grace-notes are gone.

**In a last step**, shown in the bottom right plot, the pitches of each event
are again taken as the maximum of the histogram of each event. Now following
the musical piece aurally, the events represent the **melody**. These notes are
used for the n-gram vector.

An example of a trained SOM using musical pieces of Kachin ethnic group,
northern Myanmar with Uyghur musical pieces from Xinjiang, western China is
shown below. The map is trained with 5-grams. Most Uyghur pieces are located at
the lower blue region, mainly because of the frequent tone repetitions of
Uyghur music compared to Kachin songs.

.. figure:: ../fig/ngram_5_noteminlen_10_BaderUyghur.png
   :scale: 50 %
   :alt: 5-gram SOM

   Trained 5-gram SOM, comparing Kachin and Uyghur musical pieces. Most Uyghur
   pieces are located in the lower blue region due to enhanced note repetition
   found in Uyghur music.

Tonal System
=======================================
Tonal systems are normally understood as a small set of cent values. So a
7-tone scale has seven-pitch values. Still, depending on musical performance,
determining a tonal system is more or less complex. Articulation in singing
often leads to a large variation in pitch. The same might hold for lutes,
guitars, violins, or wind instruments. Percussion instruments have a much more
straight pitch. till, they often are inharmonic, and, therefore, a pitch might
not even be perceived.

Therefore the MIR tool for investigating tonal systems takes tonal systems as
an accumulation of pitch values over mainly single-voiced musical pieces
compressed within one octave with a precision of one cent. An autocorrelation
algorithm determines the pitch for n time frames per second, the one already
shown in the melody section above.

In a second stage, pitch events are detected, again as discussed above. All
pitches of the detected musical events are then accumulated in dcent values
(dcent = 1 is recommended), starting again from f0 in noctaves. To also include
melismas and slurs in the calculation, the tonal system is derived from all
pitch values in the musical event (top left plot of above figure). If the tonal
system should only be constructed from pitch events with a very constant pitch,
the mindev parameter needs to be small. 

The strongest frequency maxf is then taken as the fundamental of the tonal
system. In the tonal system plots shown below, this lowest cent is not shown,
as it often overwhelms the other accumulated cent values.

In a last step, using the largest accumulated pitch as fundamental of the tonal
system, all accumulated cents in noctaves are mirrored into one octave. When a
precision of one cent was used, the input feature vector to the SOM has a
length of 1200, reflecting 1200 cent in one octave.

.. figure:: ../fig/TonalSystem_Examples.png
   :scale: 50 %
   :alt: Tonal System Examples

   Three examples of tonal systems as calculated from a sound file (left
   column) and as a vector on the neural map on the location the musical pieces
   fits best (right column). Top: Uygur Rock/Pop piece by Qetik, Middel: Kachin
   flute solo piece, Bottom: Lisu flute solo piece.

The outputs are

   - accumulated cent values over noctaves
   - accumulated cent values within one octave
   - Names of the ten best-matchin tonal systems
   - Cent values of the best-matching tonal systems
   - Correlation of each cent value in all best-matching scale to estimate the salience of each note to the overall large correlation between theoretical scale and calculated values
   - Overall correlation of the best-matching scales

The tonal systems used for comparison are taken from a set of scales:
https://www.flutopedia.com/scales.htm. The list contains over 900 scales.
Therefore, matches might not meet expectations. Reduced lists fitting special
intrests will be developed in the future.

Below, a trained SOM with tonal systems of the Kachin vs. Uyghur music case is
shown below. Both ethnic groups are clustered, where Uyghur pieces on the lower
left are nearer to just intonation, while Kachin shows more deviating pitches.

.. figure:: ../fig/TonalSystem_UyghurLisu_RawangShanBama.png
   :scale: 50 %
   :alt: 5-gram SOM
