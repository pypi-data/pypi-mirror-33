import tensorflow as tf


def grad (cost, learning_rate, global_step):
    return tf.train.GradientDescentOptimizer (learning_rate).minimize (cost, global_step = global_step)

def adam (cost, learning_rate, global_step):
    return tf.train.AdamOptimizer (learning_rate).minimize (cost, global_step = global_step)

def momentum (cost, learning_rate, global_step, mometum = 0.99):
    return tf.train.MomentumOptimizer (learning_rate, mometum).minimize (cost, global_step = global_step)

def rmsprob (cost, learning_rate, global_step, decay = 0.9, mometum = 0.0, epsilon = 1e-10):
    return tf.train.RMSPropOptimizer (learning_rate, decay, momentum, epsilon).minimize(cost, global_step = global_step)

def adagrad (cost, learning_rate, global_step, initial_accumulator_value=0.1):
    return tf.train.AdagradOptimizer (learning_rate, initial_accumulator_value).minimize(cost, global_step = global_step)

def adagradDA (cost, learning_rate, global_step, initial_gradient_squared_accumulator_value=0.1, l1_regularization_strength=0.0, l2_regularization_strength=0.0):
    return tf.train.AdagradDAOptimizer (learning_rate, global_step, initial_gradient_squared_accumulator_value, l1_regularization_strength, l2_regularization_strength).minimize(cost, global_step = global_step)

def adadelta (cost, learning_rate, global_step, rho=0.95, epsilon=1e-08,):
    return tf.train.AdadeltaOptimizer (learning_rate, rho, epsilon).minimize(cost, global_step = global_step)

def ftrl (cost, learning_rate, global_step, initial_accumulator_value=0.1, l1_regularization_strength=0.0, l2_regularization_strength=0.0):
    return tf.train.FtrlOptimizer (learning_rate, global_step, initial_accumulator_value, l1_regularization_strength, l2_regularization_strength).minimize(cost, global_step = global_step)

def proxadagrad (cost, learning_rate, global_step, initial_accumulator_value=0.1, l1_regularization_strength=0.0, l2_regularization_strength=0.0):
    return tf.train.ProximalAdagradOptimizer (learning_rate, global_step, initial_accumulator_value, l1_regularization_strength, l2_regularization_strength).minimize(cost, global_step = global_step)

def proxgrad (cost, learning_rate, global_step, l1_regularization_strength=0.0, l2_regularization_strength=0.0):
    return tf.train.ProximalAdagradOptimizer (learning_rate, global_step, l1_regularization_strength, l2_regularization_strength).minimize(cost, global_step = global_step)

def clip (cost, learning_rate, global_step, min_, max_):
    train_op = tf.train.AdamOptimizer (learning_rate = learning_rate)
    gradients = train_op.compute_gradients (cost)
    capped_gradients = [(tf.clip_by_value (grad, min_, max_), var) for grad, var in gradients]
    return train_op.apply_gradients (capped_gradients, global_step = global_step)
