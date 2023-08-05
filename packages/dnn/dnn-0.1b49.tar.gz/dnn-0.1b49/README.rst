
==============================
Deep Neural Network Library
==============================

It is for eliminating repeat jobs of machine learning. Also it can makes your code more beautifully and Pythonic.

.. contents:: Table of Contents

Building Deep Neural Network 
==============================

mydnn.py,

.. code-block:: python

  import dnn
  import tensorflow as tf
  
  class MyDNN (dnn.DNN):
    n_seq_len = 24    
    n_channels = 1024    
    n_output = 8
        
    def make_place_holders (self):
        # should be defined as self.x and self.y
        self.x = tf.placeholder ("float", [None, self.n_seq_len, self.n_channels])
        self.y = tf.placeholder ("float", [None, self.n_output])
        
    def make_logit (self):
        # building neural network with convolution 1d, rnn and dense layers
        
        layer = self.conv1d (self.x, 2048, activation = tf.nn.relu)
        layer = self.avg_pool1d (layer)
        
        outputs = self.lstm_with_dropout (
          layer, 2048, lstm_layers = 2, activation = tf.tanh
        )
        
        # hidden dense layers
        layer = self.dense (outputs [-1], 1024)
        layer = self.batch_norm_with_dropout (layer, self.nn.relu)
        layer = self.dense (layer, 256)
        layer = self.batch_norm_with_dropout (layer, self.nn.relu)
        
        # finally, my logit        
        return self.dense (layer, self.n_output)
    
    def make_label (self):
        # prediction method 
        return tf.argmax (self.logit, 1)
    	
    def make_cost (self):
        return tf.reduce_mean (tf.nn.softmax_cross_entropy_with_logits (
            logits = self.logit, labels = self.y
        ))
    
    def make_optimizer (self):
        return tf.train.AdamOptimizer (self.learning_rate).minimize (
          self.cost, global_step = self.global_step
        )
    
    def calculate_accuracy (self):
        correct_prediction = tf.equal (tf.argmax(self.y, 1), tf.argmax(self.logit, 1))
        return tf.reduce_mean (tf.cast (correct_prediction, "float"))


Sometimes it is very annoying to calculate complex accuracy with tensors, then can replace with calculate_complex_accuracy for calculating with numpy, python math and loop statement. 

.. code-block:: python

  import dnn
  import numpy as np
  
  class MyDNN (dnn.DNN):    
    # can get additional arguments for calculating accuracy as you need
    def calculate_accuracy (self, logit, y, *args, **karg):
        return np.mean ((np.argmax (logit, 1) == np.argmax (y, 1)))


Training 
=============

Import mydnn.py,

.. code-block:: python

  import mydnn, mydataset
  from tqdm import tqdm
  from dnn import split
    
  net = mydnn.MyDNN (gpu_usage = 0.4)
  net.set_train_dir ('./checkpoint')
  
  xs, ys = mydataset.load ()
  train_xs, test_xs, train_ys, test_ys = split.split (xs, ys, test_size = 10000)
      
  net.trainable (
    start_learning_rate=0.0001, 
    decay_step=500, decay_rate=0.99, 
    overfit_threshold = 0.1, # stop learining if cost moving average is over threshold and keep 100 epoches continously 
    accuracy_thres_hold = 0.5 # save checkpoint only if accuracy is over 0.5
  )  
  # should be behind trainable ()  
  net.net.set_tensorboard_dir (cf.TFBOARD_DIR) ("./logs")
  net.make_writers ('Param', 'Train', 'Valid')
    
  minibatches = split.minibatch (train_xs, train_ys, 128)

Now, we can start learning.

.. code-block:: python

  for epoch in tqdm (range (1000)): # 1000 epoch
    # training ---------------------------------
    batch_xs, batch_ys = next (minibatches)
    _, lr = net.run (
      net.train_op, net.learning_rate, 
      x = batch_xs, y = batch_ys, 
      dropout_rate = 0.5,
      is_training = True
    )
    net.write_summary ('Param', {"Learning Rate": lr})
    
    # train loss ------------------------------     
    logit, cost, accuracy = net.run (
      net.logit, net.cost, net.accuracy, 
      x = train_xs, y = train_ys, 
      dropout_rate = 0.0, 
      is_training = True
    )
    net.write_summary ('Train', {"Accuracy": accuracy, "Cost": cost})
    
    # valid loss -------------------------------
    logit, cost, accuracy = net.run (
      net.logit, net.cost, net.accuracy, 
      x = test_xs, y = test_ys, 
      dropout_rate = 0.0, 
      is_training = False
    )
    net.write_summary ('Valid', {"Accuracy": accuracy, "Cost": cost})
    
    # check overfit if cost movement average is over overfit_threshold
    if net.is_overfit ():
        break
        
But dnn give some shortcut methods for more simpler way:

.. code-block:: python

  for epoch in tqdm (range (1000)): # 1000 epoch
    # training ---------------------------------
    batch_xs, batch_ys = next (minibatches)
    lr = net.fit (batch_xs, batch_ys, dropout_rate = 0.5)
    net.write_summary ('Param', {"Learning Rate": lr})
    
    # train loss ------------------------------
    r = net.train (train_xs, train_ys)
    net.write_summary ('Train', {"Accuracy": r.accuracy, "Cost": r.cost})
    
    # valid loss -------------------------------
    r = net.valid (test_xs, test_ys)
    net.write_summary ('Valid', {"Accuracy": r.accuracy, "Cost": r.cost})
    
    if net.is_overfit ():
        break
        
If you use custom accuracy calculating like this,

.. code-block:: python

  def calculate_accuracy (self, logit, y, debug = False):
    return np.mean ((np.argmax (logit, 1) == np.argmax (y, 1)))

Then you call just update ()
 
.. code-block:: python
  
  # evaluate first
  r = net.train (batch_xs, batch_ys)
  # update r.accuracy with your accuracy function
  r.update (debug = True)
  net.write_summary ('Valid', {"Accuracy": r.accuracy, "Cost": r.cost})


Data Normalization
=====================

Data normalization and standardization,

.. code-block:: python

  train_xs = net.normalize (train_xs, normalize = True, standardize = True)

To show cumulative sum of explained_variance_ratio\_ of sklearn PCA. 

.. code-block:: python

  train_xs = net.normalize (train_xs, normalize = True, standardize = True, pca_k = -1)

Then you can decide n_components for PCA.

.. code-block:: python
  
  train_xs = net.normalize (train_xs, normalize = True, standardize = True, axis = 0, pca_k = 500)

Test dataset will be nomalized by factors of train dataset.

.. code-block:: python  
  
  test_xs = net.normalize (test_xs)

This parameters will be pickled at your train directory named as *normfactors*. You can use this pickled file for serving your model.

   
Multi Model Training
=======================

You can train complete seperated models at same time. 

Not like `Multi Task Training`_ in this case models share the part of training data and there're no shared layers between models - for example, model A is a logistic regression and B is a calssification problem.

Anyway, it provides some benefits for model, dataset and code management rather than handles as two complete seperated models. 

First of all, you give name to each models for saving checkpoint or tensorboard logging. 

.. code-block:: python
  
  import mydnn
  import dnn
  
  net1 = mydnn.ModelA (0.3, name = 'my_model_A')
  net2 = mydnn.ModelB (0.2, name = 'my_model_B')

Your checkpoint, tensorflow log and export pathes will remaped seperately to each model names like this:

.. code-block:: bash

  checkpoint/my_model_A
  checkpoint/my_model_B
  
  logs/my_model_A
  logs/my_model_B
  
  export/my_model_A
  export/my_model_B

Next, y should be concated. Assume ModelA use first 4, and ModelB use last 3. 
  
.. code-block:: python
  
  # y length is 7
  y = [0.5, 4.3, 5.6, 9.4, 0, 1, 0]  

Then combine models into MultiDNN.

.. code-block:: python
  
  net = dnn.MultiDNN (net1, 4, net2, 3)

And rest of code is very same as a single DNN case.

If you need exclude data from specific model, you can use exclusion filter function.

.. code-block:: python

  def exclude (ys, xs = None):
    nxs, nys = [], []
    for i, y in enumerate (ys):
        if np.sum (y) > 0:            
            nys.append (y)
            if xs is not None:
                nxs.append (xs [i])
    return np.array (nys), np.array (nxs)
  net1.set_filter (exclude)

.. _`Multi Task Training`: https://jg8610.github.io/Multi-Task/


Export Model
===============

For serving model,

.. code-block:: python

  import mydnn
  
  net = mydnn.MyDNN ()
  net.restore ('./checkpoint')
  version = net.export ( 
    './export', 
    'predict_something', 
    inputs = {'x': net.x},
    outputs={'label': net.label, 'logit': net.logit}
  )
  print ("version {} has been exported".format (version))
 
 
You can serve the expoted model with `TensorFlow Serving`_ or tfserver_.

Note: If you use net.normalize (train_xs), normalizing factors (mean, std, max and etc) willl be pickled and saved to model directory with tensorflow model. 
If you can use this file for normalizing new x data at real service.

.. code-block:: python

  def normalize (x):    
    norm_file = os.path.join (model_dir, "normfactors")
    with open (norm_file, "rb") as f:
      mean, std, min_, gap, normalize, standardize = pickle.load (f)
    if normalize: # -1 to 1
        x = -1 + 2 * ((x - min_) / gap) # gap = (max - min)
    if standardize:
        x = (x - mean) / std
    return x

.. _`TensorFlow Serving`: https://github.com/tensorflow/serving 
.. _tfserver: https://pypi.python.org/pypi/tfserver


Helpers
============

There're several helper modules.

Generic DNN Model Helper
------------------------------

.. code-block:: python

  from dnn import costs, predutil


Data Processing Helper
------------------------------

.. code-block:: python
  
  from dnn import split, vector
  import dnn.video
  import dnn.audio
  import dnn.image
  import dnn.text


dnn Class  Methods & Properties
====================================

You can override or add anything. If it looks good, contribute to this project please.

Predefined Operations & Creating
---------------------------------------------------

You should or could create these operations by overriding methods,
 
- train_op: create with 'make_optimizer'
- logit: create with 'DNN.make_logit'
- cost: create with 'DNN.make_cost'
- accuracy: create with 'DNN.calculate_accuracy'
- label (optional): create with 'DNN.make_label', determine your label index(es) or something from your logit

Predefined Place Holders
--------------------------------

- x
- y
- dropout_rate: if negative value, dropout rate will be selected randomly. 
- is_training
- n_sample: Numner of x (or y) set. This value will be fed automatically, do not feed.

Layering
----------------------------

- dense
- batch_norm
- batch_norm_with_dropout
- lstm
- lstm_with_dropout
- dropout
- full_connect
- conv1d
- conv2d
- conv3d
- max_pool1d
- max_pool2d
- max_pool3d
- avg_pool1d
- avg_pool2d
- avg_pool3d
- sequencial_connect

Optimizers
-----------------

You can use predefined optimizers.

.. code-block:: python

  def make_optimizer (self):
    return self.optimizer ("adam")
    # Or
    return self.optimizer ("rmsprob", mometum = 0.01)
    
Available optimizer names are,

- "adam"    
- "rmsprob"
- "momentum"
- "clip"
- "grad"
- "adagrad"
- "adagradDA"
- "adadelta"
- "ftrl"
- "proxadagrad"
- "proxgrad"

see dnn/optimizers.py

Training 
--------------

- fit
- train
- valid
- trainable
- run
- get_epoch: equivalant with DNN.eval (self.global_step)
- is_overfit
- normalize
- l1
- l2

Model 
------------

- save
- restore
- export
- reset_dir
- set_train_dir
- eval


Tensor Board
-----------------------

- set_tensorboard_dir
- make_writers
- write_summary


History
=========

- 0.1: project initialized
