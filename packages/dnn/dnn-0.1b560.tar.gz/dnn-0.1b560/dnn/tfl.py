from tensorflow.contrib.lite.python import interpreter
import tensorflow as tf
from .dnn import _normalize 

class Interpreter (interpreter.Interpreter):    
    def __init__ (self, path):
        self.path = path
        self.interp = interpreter.Interpreter (path)
        self.interp.allocate_tensors()
    
    def details (self): 
        print ("* TFL Inputs")
        for each in self.interp.get_input_details ():
            print ("  - #{}. {}: {}".format (each ["index"], each ["name"], each ["shape"]))        
        print ("* TFL Outputs")
        for each in self.interp.get_output_details ():
            print ("  - #{}. {}: {}".format (each ["index"], each ["name"], each ["shape"]))        
        
    def run (self, x,  min = -50, max = 50): 
        self.interp.set_tensor (self.interp.get_input_details()[0]["index"], x.astype ("uint8"))        
        return self.interp.get_tensor(self.interp.get_output_details()[0]["index"])


if __name__ == "__main__":
    import numpy as np
    
    f = Interpreter ("/home/ubuntu/sns/aimdv/engine2/resources/exported/lge7/71/model.tfl")
    f.details ()
    x = np.load ("/home/ubuntu/sns/aimdv/engine2/resources/features/Ghost/Ghost_scene025.wav.npy")
    with open ("/home/ubuntu/sns/aimdv/engine2/resources/exported/lge7/70/normfactors") as f:
        norm_factor = pickle.load (f)
    x = _normalize (x, *norm_factor) * 2.0
    print (f.run (x.reshape (1, 12, 449)))
    
    
    