##TO DO: id_naming_video
import os
import platform
import sys
import threading
import warnings

warnings.filterwarnings("ignore")

import assemblyai as aai
from audio_analysis import analysis, decision
from stt_methods import (audio_extract, check_quiet, createtables,
                         deletechunks, denoise, gen_id, limit, mergevideo,
                         recogniser_threads, segment)

aai.settings.api_key ="633d8b7b72e744948733ee6c86566d9d"

arguments=sys.argv
arguments=arguments[1:]

working_dir=os. getcwd()
id=gen_id()

if platform.system()=="Windows":
    video_path= working_dir+"\\"+arguments[0]
    working_dir+="\\temp"
    os.system("mkdir "+working_dir)
    audio_path = working_dir+"\\audio.mp3"
    temporal_file=working_dir+"\\temp.wav"
    output_path = working_dir+"\\audio.wav"
    video_out= working_dir+"\\"+id+".mp4"
    
elif platform.system=="Linux":
    video_path= working_dir+"/"+arguments[0]
    video_out= working_dir+"/"+id+".mp4"
    working_dir+="/temp"
    os.system("mkdir "+working_dir)
    audio_path = working_dir+"/audio.mp3"
    temporal_file=working_dir+"/temp.wav"
    output_path = working_dir+"/audio.wav"

processed = "\u001b[1;32m[+]\u001b[0m"

if __name__=="__main__":
    print("""\n+---------------------------------------------------+
+ Lvxw's audio normalization and transcription tool +
+ https://github.com/lvzrr/video-transcription      +
+---------------------------------------------------+\n""")
    warnings.filterwarnings("ignore")
    
    audio_extract(video_path, audio_path)
    print(f"{processed} Successfully unliked audio from video    \r",end="\n\n",flush=True)
    
    check_quiet(audio_path)
    print(f"{processed} Checked if the file was too quiet    \r",end="\n\n",flush=True)
    
    denoise(audio_path,temporal_file,working_dir)
    
    print(f"{processed} Enhanced vocal presence and reduced noise                            \r",end="\n\n",flush=True)
    
    result=decision(analysis(temporal_file))

    print(f"{processed} Audio has been successfully analysed            \r",end="\n\n",flush=True)
        
    limit(temporal_file,audio_path,output_path,result)
        
    print(f"{processed} Audio has been processed       \r",end="\n\n",flush=True)

    mergevideo(audio_path,video_path,id)
    
    print(f"{processed} Normalized video successfully created     \r",end="\n\n",flush=True)

    if "Windows" == platform.system():
        os.system("del /q "+video_path)
        os.system("del /q "+audio_path)
    elif "Linux" == platform.system():
        os.system("rm "+audio_path)
        os.system("rm "+video_path)
        
    chunks=segment(output_path,working_dir)
    chunk_path=working_dir+"\\chunks"
    print(f"{processed} Successfully segmented audio                                                                                    \r",end="\n\n",flush=True)

    transcrip=recogniser_threads(chunks[1])
    print(f"{processed} Successfully transcribed audio                                                                      \r",end="\n\n",flush=True)
    
    createtables(transcrip,chunks[0])
    
    print(f"{processed} Database has been correctly created                         \r",end="\n\n",flush=True)
    
    deletechunks(chunk_path,id)
    print(f"\n{processed} Files rearranged                           \r",end="\n\n",flush=True)
    
    print(f"{processed} +--------Finished all tasks-------+                        \r",end="",flush=True)
    print("""\u001b[1;31m\n _   __        __   ____  ____
| | / /__ ____/ /  / __ \/ __/__
| |/ / -_) __/ _ \/ /_/ /\ \/ -_)
|___/\__/_/ /_.__/\____/___/\__/\n\u001b[0m""")
    print("This tool was developed by lvxw for the Public University of Navarra\n")