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
### Waveform Before and After
Before            |  After
:-------------------------:|:-------------------------:
![low_mic_unnormalised](https://github.com/lvzrr/VerbOSe/assets/161524890/a6852ebe-9b01-4fef-b16c-02485c8fa606) | ![low_noise_fixed](https://github.com/lvzrr/VerbOSe/assets/161524890/9347efe7-1d30-4325-997e-be6e00120861)

Before            |  After
:-------------------------:|:-------------------------:
[![a](https://img.youtube.com/vi/<VIDEO ID>/maxresdefault.jpg)](https://github.com/lvzrr/VerbOSe/assets/161524890/ea4e05c3-cd27-4283-bd45-5bd688c0c63d) | [![a](https://img.youtube.com/vi/<VIDEO ID>/maxresdefault.jpg)](https://github.com/lvzrr/VerbOSe/assets/161524890/a35940a9-9d40-4e17-aa4f-84773f715baa)
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
## Csv output format:
```
Longitud (ms),Texto
9.022,b'En este ejercicio os dejo una trama de Cernet para que identifiqu\xc3\xa9is los campos.'

17.996,"b'una trama Ethernet completa que yo he recibido por un interfaz Ethernet, los bits lo he puesto en hexadecimal, con lo cual cada dos d\xc3\xadgitos o letras es un byte y lo que tenemos que hacer aqu\xc3\xad es identificar los campos de la trama.'"

3.914,"b'Entonces fijaros, ah\xc3\xad abajo os he puesto la trama de Cernet.'"

63.937,"b'con la cabecera del subnivel MAC y el c\xc3\xb3digo de redundancia c\xc3\xadclica al final y en la cabecera del subnivel MAC ten\xc3\xadamos MAC destino, MAC origen y un tercer campo que pod\xc3\xada ser tipo o longitud seg\xc3\xban la trama fuera el formato DIX, formato CERNEC2 o el formato 802 entonces vendr\xc3\xa1 a continuaci\xc3\xb3n la cabecera LLC. Entonces los primeros 6 bytes son la direcci\xc3\xb3n MAC destino. En concreto Fijaros que es ese valor que coment\xc3\xa1bamos que estaba reservado para hacer referencia a todos los interfaces de la red de esta LAN. Lo que llamamos la direcci\xc3\xb3n MAC de Broadcast. Pero es un valor de direcci\xc3\xb3n MAC como otro cualquiera, solo que tiene ese significado especial. El siguiente campo es la direcci\xc3\xb3n MAC origen. Esos 6 bytes de ah\xc3\xad es la direcci\xc3\xb3n MAC origen. Es decir, la direcci\xc3\xb3n MAC del interfaz Ethernet que ha construido, que ha enviado esta trama Ethernet. Entonces, las direcciones MAC, si record\xc3\xa1is, ten\xc3\xadan dos partes. Los primeros tres bytes es lo que llamamos el OUI.'"

34.124,"b'que es un identificador b\xc3\xa1sicamente del fabricante y los \xc3\xbaltimos tres bytes es como quien dice el n\xc3\xbamero de serie pr\xc3\xa1cticamente de la tarjeta, un identificador de la tarjeta fabricada por ese fabricante. Entonces pod\xc3\xa9is ir a tablas que tiene el iecubo y os dice a quien ha asignado los OUI y en concreto si busc\xc3\xa1is este 0077D est\xc3\xa1 asignado a Cisco Systems, \xc2\xbfvale? No lo s\xc3\xa9, conozca. Cisco Systems es un fabricante de equipos de comunicaciones originalmente de routers IP pero hoy en d\xc3\xada hay muchas m\xc3\xa1s cosas, \xc2\xbfvale? Muy conocido.'"

31.237,"b'y muchos de los equipos que ten\xc3\xa9is en el laboratorio son de este tipo. Bien, el tercer campo es el Ethertype o la longitud. \xc2\xbfDe qu\xc3\xa9 depend\xc3\xada que fuera un campo de tipo o un campo de longitud? De si su valor era mayor que 1500 o menor o igual que 1500. Si es un campo longitud, me dice cu\xc3\xa1l es la longitud de los datos que vienen a continuaci\xc3\xb3n. Y dec\xc3\xadamos que la m\xc3\xa1xima cantidad de datos, lo que llamamos la MTU, Era de 1500 bytes, por lo cual nunca ten\xc3\xada sentido que la longitud fuera de m\xc3\xa1s de 1500.'"

19.332,"b'No se emplea ning\xc3\xban Ethertype menor que 1.500 y as\xc3\xad tenemos hecha la compatibilidad. Si ah\xc3\xad pone m\xc3\xa1s de 1.500 es un Ethertype, si pone 1.500 o menos es una longitud y entonces estamos en formato 802 y a continuaci\xc3\xb3n deber\xc3\xada venir la cabecera LLC, \xc2\xbfvale? O digo el deber\xc3\xada y pongo la cabecera LLC porque va a todo ponerle Asterix.'"

43.829,"b'Entonces, ese valor 0806, el primer byte es el m\xc3\xa1s significativo, el segundo byte es el menos significativo, esto es lo que se suele llamar el orden de la red, o Bigendian. Si lo pas\xc3\xa1is a decimales, 2054, y hay otra tabla de IANA, las organismos de estandarizaci\xc3\xb3n de registro de n\xc3\xbameros en internet, que pod\xc3\xa9is consultar y os dir\xc3\xa1 que 2054 es el valor reservado para decir que los datos que vienen son un paquete de un protocolo que se llama ARP o Address Resolution Protocol. Este es un protocolo muy com\xc3\xban en LAN, Ethernet en las cuales yo estoy empleando en los hosts el protocolo IPv4. Y como tal lo veremos en detalle en la asignatura de redes dom\xc3\xa9sticas.'"

3.621,"b'Y bueno, los \xc3\xbaltimos cuatro bytes son el c\xc3\xb3digo de reputaci\xc3\xb3n.'"

0.406,b'\xc2\xbfBien?'
```
## Diagram/Concept map
![v2-Diagram (1)](https://github.com/lvzrr/VerbOSe/assets/161524890/a964d873-e9ff-43fe-8a8d-354445902a53)
