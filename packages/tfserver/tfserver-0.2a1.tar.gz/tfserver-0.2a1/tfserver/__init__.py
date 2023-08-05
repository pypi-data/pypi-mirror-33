import os
import tensorflow as tf
import time
import pickle
from dnn.dnn import _normalize

__version__ = "0.2a1"

class Session:
    def __init__ (self, model_dir, tfconfig = None):
        self.model_dir = model_dir
        try:
            self.version = int (os.path.basename (model_dir))
        except:
            self.version = 0    
        self.tfconfig = tfconfig
        self.graph = tf.Graph ()
        self.tfsess = tf.Session (config = tfconfig, graph = self.graph)
        with self.graph.as_default ():
            meta = tf.saved_model.loader.load (
                self.tfsess, 
                [tf.saved_model.tag_constants.SERVING], 
                model_dir
            )
        
        self.norm_factor = self.load_norm_factor ()
        self.input_map = {}
        self.outputs = {}
        self.activation = {}
            
        for signature_def_name, signature_def in meta.signature_def.items ():
            self.input_map [signature_def_name] = {}
            self.outputs [signature_def_name] = []
            self.activation [signature_def_name] = []
            
            for k, v in signature_def.inputs.items ():
                self.input_map [signature_def_name][k] = (v.name, self.graph.get_tensor_by_name (v.name), v.dtype, [dim.size for dim in v.tensor_shape.dim])                    
            for k, v in signature_def.outputs.items ():
                self.outputs[signature_def_name].append ((k, v.name, self.graph.get_tensor_by_name (v.name), v.dtype, [dim.size for dim in v.tensor_shape.dim]))                
                self.activation [signature_def_name] .append (v.name)        
    
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
                                        
    def get_version (self):
        return self.version
            
    def run (self, feed_dict, signature_def_name = tf.saved_model.signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY):
        return self.tfsess.run (self.activation [signature_def_name], feed_dict = feed_dict)
        
    def close (self):
        self.tfsess.close ()

tfsess = {}
            
def load_model (alias, model_dir, tfconfig = None):
    global tfsess
    tfsess [alias] = Session (model_dir, tfconfig)
    
def close ():
    global tfsess
    for sess in tfsess.values ():
        sess.close ()
    tfsess = {}
        
