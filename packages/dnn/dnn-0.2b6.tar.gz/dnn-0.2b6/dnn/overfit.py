import sys
import numpy as np

class Overfit:
    def __init__ (self, threshold, keep_count = 100):      
        self.min_cost = sys.maxsize
        self.threshold = threshold
        self.keep_count = keep_count
        self.overfitted_count = 0
        self.cost_log = []
        self.cost_ma20 = sys.maxsize
        self.best_cost_ma20 = sys.maxsize
        self.new_record = False
        self.overfit = False
    
    @property
    def latest_cost (self):
        return  self.cost_log [-1]
        
    def is_overfit (self):
        return self.overfit
    
    def is_renewaled (self):
        return self.new_record
    
    def add_cost (self, cost):
        self.overfit, self.new_record = False, False        
        
        if cost < self.min_cost: 
            self.min_cost = cost   
            self.new_record = True
            
        self.cost_log.append (cost)
        if len (self.cost_log) < 20:
            return
        
        self.cost_ma20 = np.mean (self.cost_log)
        self.cost_log = self.cost_log [-20:] 
        
        self.best_cost_ma20 = min (self.cost_ma20, self.best_cost_ma20)
        if self.threshold and self.cost_ma20 > self.best_cost_ma20 + (self.best_cost_ma20 * self.threshold):
            self.overfitted_count += 1
            # if occured  5 times sequencially
            if self.overfitted_count > self.keep_count:
                self.overfit = True
        else:
            self.overfitted_count = 0
        