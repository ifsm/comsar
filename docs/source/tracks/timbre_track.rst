=================
Timbre Track
=================

All timbre features use a Fourier to analyze the sound in adjacent, non-overlapping frames of 80 ms. The analyzed discrete spectrum $A_i$ with amplitude A and N frequency entries $f_i$ is then further processed in the the four features. Here i is used as the vector bins, which map into frequency values through the sample frequency s and the analysis window length l in samples like $f_i$ = i / (l / s).

1. Spectral Centroid

The spectral centroid C is the center of a spectrum, where the sum of amplitudes of frequencies above and below this center are equal, and is calculated as

.. math::
  C = \frac{\sum_{i=0}^N f_i A_i}{\sum_{i=0}^N A_i} \ .


This corresponds to psychoacoustic brightness perception.

2. Roughness

Roughness calculations have been suggested in several ways (for a review see (Schneider2009), ({Bader2013).). Basically two algorithms exist, calculating beating of two sinusoidals close to each other (Helmholtz ({Helmholtz1863), Helmholtz/Bader (Schneider2009), Sethares (Sethares1993), or integrating energy in critical bands on the cochlear (Fastl (Zwicker1999), Sothek (Sothek1994). The former has been found to work very well with musical sounds, the latter with industrial noise. 

In the paper a modified Helmholt/Bader algorithm is used. Like Helmholtz it assumes a maximum roughness of two sinusoidals at 33 Hz frequency difference. As Helmholtz did not give a mathematical formula how he did calculate roughness, according to his verbal descriptions a curve of the amount of roughness $R_n$ is assumed between two frequencies with distance $df_n$ which have amplitudes $A_1$ and $A_2$ like

.. math::
  R_n = A_1 A_2 \frac{|df_n|}{f_r e^{-1}} e^{- |df_n|/f_r} \ .


with a maximum roughness at $f_r$ = 33 Hz. The roughness R is then calculated as the sum of all possible sinusoidal combinatins like

.. math::
  R = \sum_{i=1}^N R_i \ .


The only difference between the algorithm used in apollon and that described in (Schneider2009) is the precision with which the frequencies are calculated. To arrive at very precise values in (Schneider2009) a wavelet analysis is performed, allowing for an arbitrary precision of frequency estimation. As this is very expensive in terms of computational time, in the present study the above described Fourier analysis precision is used. In ({Schneider2009} the research aim was to tell the perceptual differences between tuning systems like Pure Tone, Werkmeister, Kirnberger, etc. in a Baroque piece of J.S. Bach which succeeded. The present analysis is not aiming for such subtle differences, but for the overall estimation of roughness.

4. Sharpness

Perceptual sharpness is related to the work of Bismarck (Bismarck1974) and followers (Aures1985b, Fastl2007). It corresponds to small frequency-band energy. According to (Fastl2007) it is measured in acum, where 1 acum is a small-band noise within one critical band around 1 kHz at 60 dB loudness level. Sharpness increases with frequency in a nonlinear way. If a small-band noise increases its center frequency from about 200 Hz to 3 kHz sharpness increases slightly, but above 3 kHz strongly, according to perception that very high small-band sounds have strong sharpness. Still sharpness is mostly independent of overall loudness, spectral centroid, or roughness, and therefore qualifies as a parameter on its own.

To calculate sharpness the spectrum A is integrated with respect to 24 critical or Bark bands, as we are considering small-band noise. With loudness $L_B$ at each Bark band B sharpness is

.. math::
  S = 0.11 \frac{\sum_{B=0}^{24 Bark} L_B g_B B}{\sum_{B=0}^{24 Bark} L_B} \ \text{acum} ,  


where a weighting function $g_B$ is used strengthening sharpness above 3 kHz like({Peeters2004}

.. math::
  g_B = \left\{\begin{array}{ll} 1 \text{ if} B < 15 \\ 0.066 e^{0.171 B} \text{ if} z \geq 15 \end{array} \right.


5. Loudness

Although several algorithms of sound loudness have been proposed (Fastl2007), for music still no satisfying results have been obtained (Rusckowski2013). Most loudness algorithms aim for industrial noise and it appears that musical content considerably contributes to perceived loudness. Also loudness is found to statistically significantly differ between male and female subjects due to the different constructions of the outer ears between the sexes. Therefore a very simple estimation of loudness is used, and further investigations in the subject are needed. The algorithm used is

.. math::
 L = 20 \log_{10} \frac{1}{N}\sqrt{\sum_{i=0}^N \frac{A_i^2}{A_{ref}^2}} \ .


This corresponds to the definition of decibel, using a rough logarithm-of-ten compression according to perception, and a multiplication with 20 to arrive at 120 dB for a sound pressure level of about 1 Pa. Of course the digital audio data are not physical sound pressure levels (SPL), still the algorithm is used to obtain dB-values most readers are used to. As all psychoacoustic parameters are normalized before inputting them into the SOM, the absolute value is not relevant.

6. Spectral Flux

7. Fractal Correlation Dimension

8. Correlogram

9. Spread

10. Kurtosis


Lit.: 

Aures, W.: Der sensorische Wohlklang als Funktion psychoakustischer Empfindungsgroessen, [Sensory pleasing sounds as function of psychoacoustic perception parameters], Acustica 58, 282-290, 1985.

Bader, R.: *Nonlinearities and Synchronization in Musical Acoustics and Music Psychology,* Springer-Verlag, Berlin, Heidelberg, Current Research in Systematic Musicology, vol. 2,  2013.

Fastl H. & Zwicker, E.: *Psychoacoustics. Facts and Models.* 3rd edition, Springer 2007.

von Helmholtz, H.: *Die Lehre von den Tonempfindungen als physiologische Grundlage fuer die Theorie der Musik [On the Sensations of tone as a physiological basis for the theory of music]*. Vieweg, Braunschweig 1863.

Ruschkowski, A. v.:  *Lautheit von Musik: eine empirische Untersuchung zum Einfluss von Organismusvariablen auf die Lautstaerkewahrnehmung von Musik. [Loudness of music: an empirical investigation on the impact of Organism variables on loudness perception of music.]* https://katalogplus.sub.uni-hamburg.de/vufind/Record/78110422X?rank=1 Hamburg 2013.

Schneider, A., von Ruschkowski, A., & Bader, R.: Klangliche Rauhigkeit, ihre Wahrnehmung und Messung. In: Bader, R. (ed. / Hrsg.).: Musical Acoustics, Neurocognition and Psychology of Music / Musikalische Akustik, Neurokognition und Musikpsychologie. Hamburger Jahrbuch fuer Musikwissenschaft 25, 101-144, 2009.

Sethares, W.: Local consonance and the relationship between timbre and scale, J. of the Acoust. Soc. of America 94, 1218-1228, 1993.

Sottek, R.: Gehoergerechte Rauhigkeitsberechnung [Roughness calculation fitting perception], Tagungsbericht DAGA 94, Dresden, 1197-1200, 1994.

Zwicker, E. & Fastl, H.: *Psychoacoustics. Facts and models. 2nd ed. Berlin*, New York, Springer, 1999.
