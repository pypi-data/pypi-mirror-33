try:
    from tensorflow.contrib.lite import interpreter
except ImportError:
    from tensorflow.contrib.lite.python import interpreter
import tensorflow as tf
from .dnn import _normalize
from . import predutil
import pickle
import numpy as np

class Interpreter (interpreter.Interpreter):    
    def __init__ (self, path, normfactor = None, quantized = None):
        self.path = path
        self.interp = interpreter.Interpreter (path)
        self._quantized = quantized
        if self._quantized:
            assert len (self._quantized) == 2, "quantized should be 2 integer tuple like (128, 128)"            
        self._allocated = False            
        if isinstance (normfactor, str):
            with open (normfactor, "rb") as f:
                self.normfactor = pickle.load (f)
        else:
            self.normfactor = normfactor                                
        
    def details (self): 
        print ("* TFL Inputs")
        for each in self.interp.get_input_details ():
            print ("  - #{}. {}: {}".format (each ["index"], each ["name"], each ["shape"]))        
        print ("* TFL Outputs")
        for each in self.interp.get_output_details ():
            print ("  - #{}. {}: {}".format (each ["index"], each ["name"], each ["shape"]))        
        
    def run (self, x):
        if not self._allocated:
            if  self._quantized:
                self.interp.resize_tensor_input(self.interp.get_input_details()[0]["index"], np.array(x.shape, dtype=np.int32))
            self.interp.allocate_tensors ()
            self._allocated = True
        
        x =  _normalize (x, *self.normfactor)
        if self._quantized:
            x = x * self._quantized [0] + self._quantized [1]
            x = np.clip (x, 0, 255).astype ("uint8")
            #x = (x.astype (np.float32) - 128) / 128
        else:
            x = x.astype ("float32")    
        
        self.interp.set_tensor (self.interp.get_input_details()[0]["index"], x)
        self.interp.invoke ()
        y = self.interp.get_tensor (self.interp.get_output_details()[0]["index"])
        return y.astype (np.float32)
