import os  # for file management
import platform  # for os detection
import random
import threading  # for api requests
import warnings

import assemblyai as aai  # api
import ffmpeg  # Compression-encoding-audio_separation
import pandas as pd  # csv dataframe generator
import pyloudnorm as pyln  # Normalise audio to streaming standards
import soundfile as sf  # Make audio readable for pynorm
from df.enhance import (enhance, init_df, load_audio,  # Noise reduction module
                        save_audio)
from errorhandling import Raise
from processing_chain import chain, unclip
from pydub import AudioSegment  # Segmenting and encoding audio
from pydub.silence import split_on_silence  # Segmenting and encoding audio

warnings.filterwarnings("ignore")
processing = "\u001b[1;33m[-]\u001b[0m"

def audio_extract(video_path, audio_path):
    print(f"{processing} Creating audio file...  \r",end="",flush=True)
    try:
        ffmpeg.input(video_path).output(audio_path, acodec='mp3', loglevel='quiet').run(overwrite_output=True)
    except Exception as e:
        Raise(1,f"\n{e}")
    return None
def check_quiet(audio_path):
    archivo= AudioSegment.from_mp3(audio_path)
    print(f"{processing} Converting to mono...                         \r",end="",flush=True)
    archivo.set_channels(1)
    if int(archivo.max_dBFS) < -20:
        print(f"{processing} Applying gain...                         \r",end="",flush=True)
        archivo=archivo+30
    archivo.export(audio_path,"mp3")
    return None

def limit(temporal,audio_path,output_path,analysis):
    print(f"{processing} Processing audio signal through chain...                      \r",end="",flush=True)
    chain(temporal,output_path,analysis[0])
    if analysis[1]=="1":
        print(f"{processing} Loading .wav file...                      \r",end="",flush=True)
        try:
            data, rate = sf.read(output_path)
        except Exception as e:
            Raise(1,f"\n{e}")
        try:
            meter = pyln.Meter(rate)
            print(f"{processing} Monitoring Lufs units in the audio file...\r",end="",flush=True)
            loudness = meter.integrated_loudness(data)
            print(f"{processing} Normalising...                            \r",end="",flush=True)
            loudness_normalized_audio = pyln.normalize.loudness(data, loudness, target_loudness=-14.0)
            print(f"{processing} Encoding audio to .wav...                      \r",end="",flush=True)
            sf.write(output_path, loudness_normalized_audio,rate)
            print(f"{processing} Encoding audio to .mp3...                      \r",end="",flush=True)
            sf.write(audio_path, loudness_normalized_audio,rate)
            print(f"{processing} Checking for clipped audio...                      \r",end="",flush=True)
            unclip(output_path,temporal)
            uno=AudioSegment.from_wav(temporal)
            print(f"{processing} Encoding...                         \r",end="",flush=True)
            uno.export(audio_path,"mp3")
            uno.export(output_path,"wav")
        except Exception as e:
            Raise(5,f"\n{e}")
    else:
        print(f"{processing} Checking for clipped audio...                      \r",end="",flush=True)
        unclip(output_path,temporal)
        print(f"{processing} Encoding...                         \r",end="",flush=True)
        temp=AudioSegment.from_wav(temporal)
        temp.export(audio_path,"mp3")
        temp.export(output_path,"wav")
    if "/" in temporal:
        os.system("rm "+temporal)
    else:
        os.system("del /q "+temporal)
    return None

def segment(output_path,working_dir):
    out1=[]
    out2=[]

    w=AudioSegment.from_wav(output_path)
    
    print(f"{processing} Looking for silences and splitting...                      \r",end="",flush=True)
    try:
        chunks=split_on_silence(w,min_silence_len=1300,keep_silence=100,silence_thresh=-40,seek_step=1)
    except Exception as e:
        Raise(2,f"\n{e}")
    print(f"{processing} Creating directory for chunks...                      \r",end="",flush=True)
    
    cont=0
    try:
        if "Windows" == platform.system():
            os.system("mkdir {}\\chunks".format(working_dir))
            temp_dir=working_dir+"\\chunks"
            total_duration=0
        elif "Linux" == platform.system():
            os.system("mkdir {}/chunks".format(working_dir))
            temp_dir=working_dir+"/chunks"
            total_duration=0
        
        for chunk in chunks:
            name="chunk_{}.wav".format(cont)
            if "Windows" == platform.system():
                file_path=temp_dir+"\\"+name
            elif "Linux" == platform.system():
                file_path=temp_dir+"/"+name
            
            os.system("echo > {}".format(file_path))
            
            total_duration+=chunk.duration_seconds
            
            print(f"{processing} Building chunk: {chunk} in {name}                                       \r",end="",flush=True)
            
            chunk.export(file_path,format='wav')
            
            out1.append(chunk.duration_seconds)
            out2.append(file_path)
            cont+=1
    except Exception as e:
        Raise(6,f"\n{e}")
    return out1,out2

def createtables(text,time,):
    print(f"{processing} Creating tables...                            \r",end="",flush=True)
    df=pd.DataFrame({"Longitud (ms)":time,"Texto":text})
    df.to_csv('output.csv', index=False)
    return None

def mergevideo(audio_path,video,video_out):
    print(f"{processing} Merging video and normalised audio...                            \r",end="",flush=True)
    try:
        input_video = ffmpeg.input(video)

        input_audio = ffmpeg.input(audio_path)

        ffmpeg.concat(input_video, input_audio, v=1, a=1).output(video_out+".mp4",loglevel='quiet').run()
    except Exception as e:
        Raise(3,f"\n{e}")
    return None

def deletechunks(chunk_path,id):
    print(f"{processing} Deleting chunks from working directory...                            \r",end="",flush=True)
    try:
        if "Windows" == platform.system():
            os.system("del /q "+chunk_path)
            os.system("rmdir /q "+chunk_path)
            os.system("del /q .\\temp")
            os.system("rmdir /q .\\temp")
            os.system("mkdir results")
            print(f"{processing} Arranging output files....                        \r",end="",flush=True)
            os.system("copy output.csv .\\results\\output.csv")
            os.system("copy {}.mp4 .\\results\\{}.mp4".format(id,id))
            os.system("del /q output.csv")
            os.system("del /q {}.mp4".format(id))
        elif "Linux" == platform.system():
            os.system("rm -rf "+chunk_path)
            os.system("rm audio.wav")
            os.system("rm -rf /temp")
            os.system("mkdir results")
            print(f"{processing} Arranging output files....                        \r",end="",flush=True)
            os.system("cp output.csv /results/output.csv")
            os.system("cp {}.mp4 .\\results\\{}.mp4".format(id,id))
            os.system("rm output.csv")
            os.system("rm {}.mp4".format(id))
    except Exception as e:
        Raise(4,f"\n{e}")
def denoise(audio_path,output_path,wdir):
    print(f"{processing} Encoding mp3 to wav...                            \r",end="",flush=True)
    
    audio = AudioSegment.from_file(audio_path,"mp3")
    
    audio.export(output_path, format="wav")
    if audio.duration_seconds < 1800:
        print(f"{processing} Enhancing vocal presence and reducing noise...                            \r",end="",flush=True)
        try:
            model,df_state,_=init_df(log_level="none")
            audio,_=load_audio(output_path, sr=df_state.sr(),verbose="none")
            enhanced = enhance(model, df_state, audio)
            save_audio(output_path, enhanced, df_state.sr(),log=False)
        except Exception as e:
            Raise(7,f"\n{e}")
    elif audio.duration_seconds > 1800 and audio.duration_seconds<3600:
        print(f"{processing} File is too big, processing in segments...                            \r",end="",flush=True)
        chunk1=audio[0:len(audio)/2]
        chunk2=audio[len(audio)/2:len(audio)]
        cont=0
        chunks=[chunk1,chunk2]
        for chunk in chunks:
            chunk.export(wdir+"\\preprocessed{}.wav".format(cont),"wav") ## add option for linux
            cont+=1
        for i in range(2):
            print(f"{processing} Enhancing vocal presence and reducing noise... [{i+1}/2]                         \r",end="",flush=True)
            try:
                model,df_state,_=init_df(log_level="none")
                audio,_=load_audio(wdir+"\\preprocessed{}.wav".format(i), sr=df_state.sr(),verbose="none")
                enhanced = enhance(model, df_state, audio)
                save_audio(wdir+"\\preprocessed{}.wav".format(i), enhanced, df_state.sr(),log=False)
            except Exception as e:
                Raise(7,f"\n{e}")
        primeramitad=AudioSegment.from_wav(wdir+"\\preprocessed0.wav")
        segundamitad=AudioSegment.from_wav(wdir+"\\preprocessed1.wav")
        audiofinal=primeramitad+segundamitad
        audiofinal.export(output_path,"wav")
    else:
        print(f"{processing} File too big for AI enhancements!                           \r",end="",flush=True)
        audio.export(output_path,"wav")
    return None
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
        print(f"{processing} Initializing transcription module...                        \r",end="",flush=True)
        config = aai.TranscriptionConfig(language_code="es")
        transcriber = aai.Transcriber(config=config)
        cont=1
        cont2=1
        for i in range(0,len(chunk_paths),5):
            batch=chunk_paths[i:i+5]
            for chunk in batch:
                print(f"{processing} Sending chunk: {chunk} [{cont}/{len(chunk_paths)}]                                                                      \r",end="",flush=True)
                cont+=1
                thread = threading.Thread(target=transcribe_chunk, args=(transcriber, chunk,out,cont))
                threads.append(thread)
                thread.start()

            for thread in threads:
                print(f"{processing} Waiting for thread: {thread} [{cont2}/{len(chunk_paths)}]                                                               \r",end="",flush=True)
                cont2+=1
                thread.join()
            threads.clear()
    except Exception as e:
        Raise(3, f"\n{e}")
    temp=sorted(out, key=lambda x: x[0])
    ret=[]
    for str in temp:
        ret.append(str[1])
    return ret
def gen_id():
    cadena = "abcdefghijklmñopqrstuvwxyz" + "abcdefghijklmñopqrstuvwxyz".upper() + "1234567890"
    generated = ""
    for i in range(0, random.randint(15, 30)):
        caracter = cadena[random.randint(0, len(cadena) - 1)]
        generated += caracter
    return generated
