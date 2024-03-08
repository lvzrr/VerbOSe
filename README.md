# VerbOSe
Simple audio transcription module for python
This program is designed to take a video ```(.mp4)``` and output 2 files:
+ A ```.csv``` file that contains a transcription for the video audio
+ A new video, with the audio processed and enhanced
## About
Some of the most important modules that are used to run this program are:
+ [Spotify Pedalboard](https://engineering.atspotify.com/2021/09/introducing-pedalboard-spotifys-audio-effects-library-for-python/) for audio data augmentation
+ [Numpy](https://numpy.org/) for feeding data into other modules
+ [Pyloudnorm](https://github.com/csteinmetz1/pyloudnorm) for normalising audio to streaming-ready standards
+ [Pydub](https://github.com/jiaaro/pydub) for audio segmentation and encoding
+ [Assembyai's api](https://www.assemblyai.com/) for audio transcription
+ [Ffmpeg](https://kkroening.github.io/ffmpeg-python/) for audio encoding
## Volume level checkpint
Checks both the integrated loudness of the audio file imput and the maximum dBFS value at any point then decides if the paugmentation chain needs input gain and normalization.
## Audio chain
The audio chain is provided by spotify's pedalboard module, that runs (when the algorythm decides that the input needs the full-chain processing):
+ Input gain
+ Compression (fast attack,slow release,ratio=4,threshold=-15)
+ High pass filter (at 550hz)
+ High pass shelf (at 16k Hz with a +4 gain)
+ Loudness module to set the integrated LUFS at -14 (spotify's standard)
+ A limiter to make sure there is no clipping in the audio (threshold at -1bBFS)

![v2-Diagram (1)](https://github.com/lvzrr/VerbOSe/assets/161524890/a964d873-e9ff-43fe-8a8d-354445902a53)
