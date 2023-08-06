import librosa
import soundfile
import os
from aquests.lib import pathtool

def resampling (audioFilePath, targetFilePath):
    y, sr = librosa.load (audioFilePath, sr = 22050, mono = True)
    with open (targetFilePath, "wb") as f:
       soundfile.write (f, y, 22050)
       
def resample_dir (directory, target = None, recusive = False):
    if taget is None:
        target  = os.path.join (directory, "AIMDV")
    pathtool.mkdir (target)
        
    for each in os.listdir (directory):
        if each == "AIMDV":
            continue
        
        path = os.path.join (directory, each)
        if os.path.isdir (path):
            if recusive:
                resample_dir (path, target, True)
            else:
                continue    
        
        try:
            resampling (path, target)
        except:
            raise


