# VerbOSe
Simple audio transcription module for python.

This program is designed to take a video ```(.mp4)``` and output 2 files:
+ A ```.csv``` file that contains a transcription for the audio and the length of each phrase
+ A new video, with the audio processed and enhanced
## About
Some of the most important modules that are used to run this program are:
+ [Spotify Pedalboard](https://engineering.atspotify.com/2021/09/introducing-pedalboard-spotifys-audio-effects-library-for-python/) for audio data augmentation
+ [Numpy](https://numpy.org/) for feeding data into other modules
+ [Pyloudnorm](https://github.com/csteinmetz1/pyloudnorm) for normalising audio to streaming-ready standards
+ [Pydub](https://github.com/jiaaro/pydub) for audio segmentation and encoding
+ [Assembyai's api](https://www.assemblyai.com/) for audio transcription
+ [Ffmpeg](https://kkroening.github.io/ffmpeg-python/) for audio encoding
+ [Pandas](https://pandas.pydata.org/) for building the dataframe that will be exported as a .csv
## Run
First, you will need to get all the dependencies for python, you can get them through pip (make sure you are inside a virtual environment):
```
pip install -r requirements.txt
```
For running this program you will need a `python3.10` or higher version of python, here is the formatting of the arguments:
```
python verbose.py <file.mp4>
```
## Volume level checkpint
Checks both the integrated loudness of the audio file imput and the maximum dBFS value at any point then decides if the paugmentation chain needs input gain and normalization.
## Audio chain
The audio chain is provided by spotify's pedalboard module, that runs (when the algorythm decides that the input needs the full-chain processing):
+ Input gain
+ Compression (fast attack,slow release,ratio=4,threshold=-15)
+ [High pass filter](https://en.wikipedia.org/wiki/High-pass_filter) (at 550hz)
+ [High shelf](https://www.recordingblogs.com/wiki/shelving-filter) (at 16k Hz with a +4 gain)
+ Loudness module to set the integrated [LUFS](https://www.izotope.com/en/learn/what-are-lufs.html) at -14 [(spotify's standard)](https://support.spotify.com/es/artists/article/loudness-normalization/)
+ A [limiter](https://www.masteringbox.com/es/learn/audio-limiter) to make sure there is no [clipping](https://es.wikipedia.org/wiki/Clipping_(audio)) in the audio (threshold at [-1bBFS](https://es.wikipedia.org/wiki/DBFS))

This is the chain that feeds the signal to the louder:
```
Chain=Pedalboard([Gain(9),HighpassFilter(cutoff_frequency_hz=550),HighShelfFilter(cutoff_frequency_hz=16000,gain_db=+4),Compressor(threshold_db=-15,ratio=4,attack_ms=1,release_ms=10)])
```
You can change the settings [here](https://github.com/lvzrr/VerbOSe/blob/main/processing_chain.py)
## Audio segmentation
You can find the audio segmentation function [here](https://github.com/lvzrr/VerbOSe/blob/main/stt_methods.py) at the segment() method, this splits the signal based on fixed parameters when the module detects there is a big enough silence.

This chunks of audio are written to memory in the ./temp/chunks folder (both folders will be gnerated automatically at the start of the program, they will delete themselves)
```bash
[SNIP]
def segment(output_path,working_dir):
    out1=[]
    out2=[]

    w=AudioSegment.from_wav(output_path)
    
    print(f"{processing} Looking for silences and splitting...\r",end="",flush=True)
    try:
        chunks=split_on_silence(w,min_silence_len=1300,keep_silence=100,silence_thresh=-40,seek_step=1)
    except Exception as e:
        Raise(2,f"\n{e}")
    print(f"{processing} Creating directory for chunks...\r",end="",flush=True)
[SNIP]
```
## API usage
This build uses Assemblyai's base spanish model for speech transcription. Every .wav chunk of audio that got written at the segmentation module is passed as an argument for the recogniser_threads() method as a list, the method will send 5 transcription petitions at a time and wait for the responses (in order to not get flagged as an attack, and because the free api key only supports 5 files at a time). The threads used in this method return a duple to the array `out` consisting of: `[ [integer,transcriped test], ...]` this integer is used to index each entry and sort the array by order of what text was transcribed first.
## Diagram/Concept map
![v2-Diagram (1)](https://github.com/lvzrr/VerbOSe/assets/161524890/a964d873-e9ff-43fe-8a8d-354445902a53)
