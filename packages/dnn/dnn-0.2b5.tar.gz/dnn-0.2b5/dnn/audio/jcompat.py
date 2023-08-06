import numpy as np
import math

def mfcc (melspec, n_mfccs):    
  # mfcc for android
  nmel, frames = melspec.shape        
  mfccs = np.zeros ((frames, n_mfccs))

  m = math.sqrt(2.0 / nmel)
  DCTcoeffs = np.zeros((nmel, n_mfccs))
  
  for i in range (nmel):
    for j in range (n_mfccs):
      DCTcoeffs [i, j] = m * math.cos (math.pi * (j + 1) * (i + .5) / nmel)
  for frm in range (frames):      
    melSpec = melspec [:,frm]
    for x in range (len (melSpec)):
      for y in range (n_mfccs):        
        mfccs [frm, y] = mfccs [frm, y] + DCTcoeffs [x, y] * melSpec [x] / frames    
  return mfccs.swapaxes(1, 0);
