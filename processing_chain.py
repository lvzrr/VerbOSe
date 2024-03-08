import os

import pyloudnorm as norm
import soundfile as sf
from pedalboard import (Compressor, Gain, HighpassFilter, HighShelfFilter,
                        Limiter, Pedalboard)
from pedalboard.io import AudioFile


def chain(input,output,analysis):
    match(analysis):
        case "1":
            Chain=Pedalboard([Gain(9),HighpassFilter(cutoff_frequency_hz=550),HighShelfFilter(cutoff_frequency_hz=16000,gain_db=+4),Compressor(threshold_db=-15,ratio=4,attack_ms=1,release_ms=10)])
        case "0":
            Chain=Pedalboard([HighpassFilter(cutoff_frequency_hz=550),HighShelfFilter(cutoff_frequency_hz=16000,gain_db=+4),Compressor(threshold_db=-15,ratio=4,attack_ms=1,release_ms=10)])
    with AudioFile(input) as f:
        with AudioFile(output, 'w', f.samplerate, f.num_channels) as o:
            while f.tell() < f.frames:
                chunk= f.read(f.samplerate)
                affected=Chain(chunk,f.samplerate,reset=False)
                o.write(affected)
    return None
def unclip(input,output):
    Chain=Pedalboard([Limiter(threshold_db=-1,release_ms=30)])
    with AudioFile(input) as f:
        with AudioFile(output, 'w', f.samplerate, f.num_channels) as o:
            while f.tell() < f.frames:
                chunk= f.read(f.samplerate)
                affected=Chain(chunk,f.samplerate,reset=False)
                o.write(affected)
    return None

