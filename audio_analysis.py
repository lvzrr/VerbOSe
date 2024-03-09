import os

from pydub import AudioSegment

wdir=os.getcwd()
input=wdir+"\\test.mp3"

processing = "\u001b[1;33m[-]\u001b[0m"

def analysis(input):
    print(f"{processing} Analysing audio...  \r",end="",flush=True)
    file=AudioSegment.from_mp3(input)
    max_dBFS=file.max_dBFS
    loudness=file.dBFS
    out=[max_dBFS,loudness]
    return out
def decision(analysis):
    print(f"{processing} Making decisions based on analysis...  \r",end="",flush=True)
    out=["",""]
    if analysis[0]==0 or analysis[0]>=-5:
        out[0]="0"
    else:
        out[0]="1"
    if analysis[1] >= -16:
        out[1]="0"
    else:
        out[1]="1"
    return "".join(out)
