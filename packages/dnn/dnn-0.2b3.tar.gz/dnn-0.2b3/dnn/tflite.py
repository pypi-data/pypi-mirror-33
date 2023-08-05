# required tensorflow >= 1.9 

try:
    from tensorflow.contrib.lite import interpreter
except ImportError:
    from tensorflow.contrib.lite.python import interpreter        
import tensorflow as tf
import numpy as np
import threading
from tensorflow.contrib.lite.python.convert import tensor_name
from . import saved_model
import os

def convert (path, saved_model_dir, quantized_input = None, quantized_input_stats = (128, 128), default_ranges_stats = (0, 1)): 
    converter = tf.contrib.lite.TocoConverter.from_saved_model (saved_model_dir)
    if quantized_input is not None:
        converter.inference_type = tf.contrib.lite.constants.QUANTIZED_UINT8            
        converter.quantized_input_stats = {tensor_name (quantized_input): quantized_input_stats}
    converter.default_ranges_stats =  default_ranges_stats
    tflite_model = converter.convert()
    open(path, "wb").write(tflite_model)

def load (path, quantized = None):
    return Interpreter (path, quantized)

class Interpreter (saved_model.Interpreter):    
    def __init__ (self, path, quantized = None):
        self.path = path
        self._quantized = quantized
        
        self.interp = interpreter.Interpreter (path)
        self.model_dir = os.path.dirname (self.path)
        self.lock = threading.RLock ()
        if self._quantized:
            assert len (self._quantized) == 2, "quantized should be 2 integer tuple like (128, 128)"            
        self._allocated = False
        self.norm_factor = self.load_norm_factor ()
        
    def get_info (self): 
        inputs = {}
        outputs = {}
        for each in self.interp.get_input_details ():
            inputs [each ["name"]] = (each ["index"], each ["shape"])
        for each in self.interp.get_output_details ():
            outputs [each ["name"]] = (each ["index"], each ["shape"])     
        return inputs, outputs      
        
    def run (self, x):
        if not self._allocated:
            if  self._quantized:
                self.interp.resize_tensor_input(self.interp.get_input_details()[0]["index"], np.array(x.shape, dtype=np.int32))
            self.interp.allocate_tensors ()
            self._allocated = True
        
        x =  self.normalize (x)
        if self._quantized:
            x = x * self._quantized [0] + self._quantized [1]
            x = np.clip (x, 0, 255).astype ("uint8")
            #x = (x.astype (np.float32) - 128) / 128
        else:
            x = x.astype ("float32")    
        
        with self.lock:
            self.interp.set_tensor (self.interp.get_input_details()[0]["index"], x)
            self.interp.invoke ()
            y = self.interp.get_tensor (self.interp.get_output_details()[0]["index"])
        return y.astype (np.float32)
