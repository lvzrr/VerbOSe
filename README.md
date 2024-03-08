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
## Installation and Execution
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
## DeepFilterNet
This program runs an instance of [deepfilternet's](https://github.com/Rikorose/DeepFilterNet) noise supression module, it may be hard on your ram, it will denoise the audio before the compression and processing is applied.
![pic](https://user-images.githubusercontent.com/16517898/225623209-a54fea75-ca00-404c-a394-c91d2d1146d2.svg)
## Audio chain
The audio chain is provided by spotify's pedalboard module, that runs (when the algorythm decides that the input needs the full-chain processing):
+ Input gain
+ Compression (fast attack,slow release,ratio=4,threshold=-15)
+ [High pass filter](https://en.wikipedia.org/wiki/High-pass_filter) (at 550hz) for removing unnecessary low frequencies 
+ [High shelf](https://www.recordingblogs.com/wiki/shelving-filter) (at 16k Hz with a +4 gain) for making the vocal stand out
+ Loudness module to set the integrated [LUFS](https://www.izotope.com/en/learn/what-are-lufs.html) at -14 [(spotify's standard)](https://support.spotify.com/es/artists/article/loudness-normalization/)
+ A [limiter](https://www.masteringbox.com/es/learn/audio-limiter) to make sure there is no [clipping](https://es.wikipedia.org/wiki/Clipping_(audio)) in the audio (threshold at [-1bBFS](https://es.wikipedia.org/wiki/DBFS))

This is the chain that feeds the signal to the louder:
```
Chain=Pedalboard([Gain(9),HighpassFilter(cutoff_frequency_hz=550),HighShelfFilter(cutoff_frequency_hz=16000,gain_db=+4),Compressor(threshold_db=-15,ratio=4,attack_ms=1,release_ms=10)])
```
You can change the settings [here](https://github.com/lvzrr/VerbOSe/blob/main/processing_chain.py)
## Audio segmentation
You can find the audio segmentation function [here](https://github.com/lvzrr/VerbOSe/blob/main/stt_methods.py) at the segment() method, this splits the signal based on fixed parameters `(can be modified)` when the module detects there is a big enough silence.

This chunks of audio are written to memory in the `./temp/chunks` folder (will be gnerated automatically at the start of the program, they will delete themselves)
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
This build uses Assemblyai's base spanish model for speech transcription. Every .wav chunk of audio that got written at the segmentation module is passed as an argument for the recogniser_threads() method as a list, the method will send 5 transcription petitions at a time and wait for the responses (in order to not get flagged as an attack, and because the free api key only supports processing of 5 files at a time).

This method uses the default python module [threads](https://docs.python.org/3/library/threading.html), in order to speed up the process

The threads used in this method return a duple to the array `out` consisting of: `[ [integer,"transcriped test"], ...]` this integer is used to index each entry and sort the array by order of what text was transcribed first.

These are the methods involved in the interaction with the API:
```bash
def transcribe_chunk(transcriber, chunk,out,cont):
    try:
        result = transcriber.transcribe(chunk).text.encode("utf-8")
        out.append([cont,result])
    except Exception as e:
        print(f"Error occurred while transcribing {chunk}: {e}")

def recogniser_threads(chunk_paths):
    threads = []
    out = []
    try:
        print(f"{processing} Initializing transcription module...\r",end="",flush=True)
        config = aai.TranscriptionConfig(language_code="es")
        transcriber = aai.Transcriber(config=config)
        cont=1
        cont2=1
        for i in range(0,len(chunk_paths),5):
            batch=chunk_paths[i:i+5]
            for chunk in batch:
                print(f"{processing} Sending chunk: {chunk} [{cont}/{len(chunk_paths)}]\r",end="",flush=True)
                cont+=1
                thread = threading.Thread(target=transcribe_chunk, args=(transcriber, chunk,out,cont))
                threads.append(thread)
                thread.start()

            for thread in threads:
                print(f"{processing} Waiting for thread: {thread} [{cont2}/{len(chunk_paths)}]\r",end="",flush=True)
                cont2+=1
              thread.join()
            threads.clear()
```
## Diagram/Concept map
![v2-Diagram (1)](https://github.com/lvzrr/VerbOSe/assets/161524890/a964d873-e9ff-43fe-8a8d-354445902a53)
