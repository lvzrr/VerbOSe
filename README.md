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
+ [High pass filter](https://en.wikipedia.org/wiki/High-pass_filter#:~:text=A%20high-pass%20filter%20(HPF,depends%20on%20the%20filter%20design.) (at 550hz)
+ High pass shelf (at 16k Hz with a +4 gain)
+ Loudness module to set the integrated [LUFS](https://www.izotope.com/en/learn/what-are-lufs.html) at -14 [(spotify's standard)](https://support.spotify.com/es/artists/article/loudness-normalization/)
+ A [limiter](https://www.masteringbox.com/es/learn/audio-limiter) to make sure there is no [clipping](https://es.wikipedia.org/wiki/Clipping_(audio)) in the audio (threshold at [-1bBFS](https://es.wikipedia.org/wiki/DBFS))

This is the chain that feeds the signal to the louder:
```bash
Chain=Pedalboard([Gain(9),HighpassFilter(cutoff_frequency_hz=550),HighShelfFilter(cutoff_frequency_hz=16000,gain_db=+4),Compressor(threshold_db=-15,ratio=4,attack_ms=1,release_ms=10)])
```
You can change the settings in [here](https://github.com/lvzrr/VerbOSe/blob/main/processing_chain.py)
## Audio segmentation
You can find the audio segmentation function [here](https://github.com/lvzrr/VerbOSe/blob/main/stt_methods.py) at the segment() method, this splits the signal based on fixed parameters when the module detects there is a silence big enough
![v2-Diagram (1)](https://github.com/lvzrr/VerbOSe/assets/161524890/a964d873-e9ff-43fe-8a8d-354445902a53)
