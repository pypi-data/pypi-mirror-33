import numpy as np
from sklearn.model_selection import train_test_split
import random
import os

def _flatten (xs, ys, origin_index = None):
    assert  len (xs) == len (ys)
    _xs = []
    _ys = []
    for i, x_list in enumerate (xs):
        if origin_index is not None:
            x_list = [x_list [origin_index]] # use original only
        for x in x_list:           
            _xs.append (x)
            _ys.append (ys [i])
    return np.array (_xs), np.array (_ys)

def split (total_xs, total_ys, test_size = 500):
    train_xs, test_xs, train_ys, test_ys = train_test_split (total_xs, total_ys, test_size = test_size, random_state = random.randrange (100))
    return train_xs, test_xs, train_ys, test_ys

def split_augset (total_xs, total_ys, test_size = 500, origin_index = 0):
    train_xs_0, test_xs, train_ys_0, test_ys = split (total_xs, total_ys, test_size)
    train_xs, train_ys = _flatten (train_xs_0, train_ys_0)
    valid_xs, valid_ys = _flatten (train_xs_0, train_ys_0, origin_index)
    test_xs, test_ys = _flatten (test_xs, test_ys, origin_index)
    return train_xs, valid_xs, test_xs, train_ys, valid_ys, test_ys

def resample (batch_xs, batch_ys, sample_size = 500):
    sample_xs, sample_ys = [], []     
    for idx in np.random.permutation(len(batch_ys))[:sample_size]:
        sample_xs.append (batch_xs [idx])
        sample_ys.append (batch_ys [idx])        
    return np.array (sample_xs), np.array (sample_ys)

def shuffled (train_xs, count):
    norm_xs = []
    for num, idx in enumerate (np.random.permutation(len(train_xs))):
        if num > count:
            break
        norm_xs.append (train_xs [idx])
    return norm_xs    

def minibatch (train_xs, train_ys, batch_size = 0):
    while 1:
        if not batch_size:
            yield train_xs, train_ys
        else:  
            pos = 0
            batch_indexes = np.random.permutation(len(train_xs))
            while 1:
                batch_xs = []
                batch_ys = []
                while 1:
                    try:
                        idx = batch_indexes [pos]
                    except IndexError:
                        pos = 0
                        batch_indexes = np.random.permutation(len(train_xs))
                        idx = batch_indexes [0]
                    batch_xs.append (train_xs [idx])
                    batch_ys.append (train_ys [idx])
                    pos += 1                    
                    if len (batch_xs) == batch_size:
                        break
                yield np.array (batch_xs), np.array (batch_ys)

CACHE = {}
def cached_glob (path):
    global CACHE
    dirname = os.path.dirname (path)
    if dirname not in CACHE:
        CACHE [dirname] = {}
        for each in sorted (os.listdir (dirname)):
            if each [:4] not in CACHE [dirname]:
                CACHE [dirname][each [:4]] = []
            CACHE [dirname][each [:4]].append (each)
             
    basename = os.path.basename (path)[:-1]
    files = []
    for c4 in CACHE [dirname]:
        if basename [:4] != c4:
            continue
        for each in CACHE [dirname][c4]:
            if not each.startswith (basename):
                if files:
                    return files
                continue        
            files.append (os.path.join (dirname, each))
    return files      
    