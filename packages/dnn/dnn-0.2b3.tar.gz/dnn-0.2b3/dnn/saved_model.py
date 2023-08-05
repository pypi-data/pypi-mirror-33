import tensorflow as tf
from .dnn import _normalize
import os
import pickle

def check_or_create (sess, graph):
    if sess is None:
        sess = tf.Session ()
    if graph is None:
        graph = sess.graph
    return sess, graph    
        
def convert (model_dir, predict_def, inputs, outputs, sess = None, graph = None):
    sess, graph = check_or_create (sess, graph)
    
    with graph.as_default ():            
        builder = tf.saved_model.builder.SavedModelBuilder(model_dir)
        classification_inputs = tf.saved_model.utils.build_tensor_info(inputs ["x"])
        classification_outputs_classes = tf.saved_model.utils.build_tensor_info(outputs ["y"])
        
        classification_signature = ( 
            tf.saved_model.signature_def_utils.build_signature_def(
            inputs={tf.saved_model.signature_constants.CLASSIFY_INPUTS: classification_inputs},
            outputs={
                tf.saved_model.signature_constants.CLASSIFY_OUTPUT_CLASSES: classification_outputs_classes,
                tf.saved_model.signature_constants.CLASSIFY_OUTPUT_SCORES: classification_outputs_classes
            },
            method_name=tf.saved_model.signature_constants.CLASSIFY_METHOD_NAME)
        )
        
        inputs=dict ([(k, tf.saved_model.utils.build_tensor_info (v)) for k, v in inputs.items ()])
        outputs=dict ([(k, tf.saved_model.utils.build_tensor_info (v)) for k,v in outputs.items ()])
        
        prediction_signature = (
          tf.saved_model.signature_def_utils.build_signature_def(
              inputs=inputs,
              outputs=outputs,
              method_name=tf.saved_model.signature_constants.PREDICT_METHOD_NAME)
          )
        
        builder.add_meta_graph_and_variables(
          sess, [tf.saved_model.tag_constants.SERVING],
          signature_def_map = {
              predict_def: prediction_signature,
              tf.saved_model.signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY: classification_signature
          }
        )
        
        builder.save ()
    return inputs, outputs
 
def load (model_dir, sess = None, graph = None):
    sess, graph = check_or_create (sess, graph)
        
    with graph.as_default ():            
        meta = tf.saved_model.loader.load (
            sess, 
            [tf.saved_model.tag_constants.SERVING], 
            model_dir
        )
    
    input_map = {}
    outputs = {}
    activation = {}
        
    for signature_def_name, signature_def in meta.signature_def.items ():
        input_map [signature_def_name] = {}
        outputs [signature_def_name] = []
        activation [signature_def_name] = []
        
        for k, v in signature_def.inputs.items ():
            input_map [signature_def_name][k] = (v.name, sess.graph.get_tensor_by_name (v.name), v.dtype, [dim.size for dim in v.tensor_shape.dim])                    
        for k, v in signature_def.outputs.items ():
            outputs[signature_def_name].append ((k, v.name, sess.graph.get_tensor_by_name (v.name), v.dtype, [dim.size for dim in v.tensor_shape.dim]))                
            activation [signature_def_name] .append (v.name)
    
    return Interpreter (model_dir, meta, input_map, outputs, activation, sess, graph)


class Interpreter:
    def __init__ (self, model_dir, meta, input_map, outputs, activation, sess, graph):
        self.model_dir = model_dir
        self.meta = meta
        self.input_map = input_map
        self.outputs = outputs
        self.activation = activation     
        self.sess = sess
        self.graph = graph
        self.norm_factor = self.load_norm_factor ()
        
    def load_norm_factor (self):
        norm_file = os.path.join (self.model_dir, "normfactors")
        if os.path.isfile (norm_file):
            with open (norm_file, "rb") as f:
                return pickle.load (f)
    
    def normalize (self, x):
        # SHOLUD BE SYMC with dnn,DNN.normalize ()
        if not self.norm_factor:
            return x
        return _normalize (x, *self.norm_factor)
            
    def run (self, feed_dict, signature_def_name = tf.saved_model.signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY):
        return self.sess.run (self.activation [signature_def_name], feed_dict = feed_dict)
        


