import tensorflow as tf
import numpy as np
from . import predutil

class Result:
    def __init__ (self, x, y, is_training, accfunc, train_dir, labels, logit, cost, acc, epoch):
        self.__x = x
        self.__y = y
        self.__is_training = is_training
        self.__accfunc = accfunc
        
        self.epoch = epoch
        self.train_dir = train_dir        
        self.logit = logit
        self.y = y
        self.labels = labels
        self.cost = cost
        self.accuracy = acc
    
    def update (self, *args, **karg): 
        self.accuracy = self.__accfunc (self.logit, self.y, *args, **karg)
                
    def make_summary (self):
        d = {"cost": self.cost}
        for i, label in enumerate (self.labels):
            try:
                d ["acc:" + label.name] = self.accuracy [i]
            except IndexError:
                break    
        return d
    
    def confidence_level (self, label_index = 0):
        label = self.labels [label_index]
        stat = {}        
        for idx in range (len (self.y)):
            logit = self.logit [idx][:len (label)]
            y = self.y [idx][:len (label)]
            probs = predutil.softmax (logit)
            prob = "{:.5f}".format (probs [np.argmax (probs)])
            if prob not in stat:
                stat [prob] = [0, 0]
            if np.argmax (probs) == np.argmax (y):    
                stat [prob][0] += 1
            stat [prob][1] += 1
            
        ordered = [] 
        accum = 0        
        accum_t = 0
        total = len (self.y)
        for lev, (c, t) in sorted (stat.items (), reverse = True):            
            accum += c            
            accum_t += t
            accuracy = accum / accum_t * 100
            ordered.append ((
                lev, 
                accum, accum_t, accuracy, 
                accum / total * 100 
            ))
            if len (ordered) >= 10 and accuracy < 100.:
                break
        return ordered    
                     
    def logit_range (self):
        output_range = [self.logit.min (), self.logit.max (), np.mean (self.logit), np.std (self.logit)]
        quant_range = {}
        for idx, m in enumerate (self.logit [:,:29].argsort (1)[:,-2]):
            sec = int (self.logit [idx, m])
            try: quant_range [sec] += 1
            except KeyError: quant_range [sec] = 1
        quant_range = quant_range
        if quant_range:           
            stats = sorted (quant_range.items ())
            # output range for top1: {} ~ {}, logit range: {:.3f} ~ {:.3f}, mean: {:.3f} std: {:.3f}
            return stats [0][0] - 1, stats [-1][0] + 1, output_range [0], output_range [1], output_range [2], output_range [3]                                
        