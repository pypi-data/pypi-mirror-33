import sys
import numpy as np

class Overfit:
    def __init__ (self, keep_count = 0):      
        self.keep_count = keep_count or 100
        self.overfitted_count = 0
        self.cost_log = [[], []]        
        self.new_record = False
        self.min_cost = sys.maxsize
        self.overfit = False
    
    @property
    def latest_cost (self):
        return  self.cost_log [1][-1]
        
    def is_overfit (self):
        return self.overfit
    
    def is_renewaled (self):
        return self.new_record
    
    def add_cost (self, cost, is_validating):
        self.overfit, self.new_record = False, False        
        
        if is_validating:
            if cost < self.min_cost: 
                self.min_cost = cost   
                self.new_record = True
        
        index = int (is_validating)
        if self.cost_log [index]:
            latest = np.mean (self.cost_log [index])
        self.cost_log [index].append (cost)
        if len (self.cost_log  [index]) < 20:
            return
        self.cost_log [index] = self.cost_log [index] [-20:]
        current = np.mean (self.cost_log [index])
        if current >= latest:
            self.overfitted_count += 1            
            if self.overfitted_count > self.keep_count:
                self.overfit = True
        else:
            self.overfitted_count = 0
        