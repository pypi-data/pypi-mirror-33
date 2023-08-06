from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np
import tensorflow as tf
from .layer import Layer


class FullyConnected(Layer):

    def __init__(self, nr_hidden, name='fc'):
        """
        All parameters are processed by __dict__.update(locals())
        Unfortunately the method also processes 'self' so it is removed
        """
        self.__dict__.update(locals())
        del self.self

    def set_input_shape(self, input_shape):
        """
        This method initializes all layer variables
        """
        with tf.name_scope(self.name):
            # store each element of input shape in different variables
            batch_size, dim = input_shape
            # define weight & bias init
            weight_init = tf.random_normal(
                [dim, self.nr_hidden], dtype=tf.float32)
            weight_init = weight_init / tf.sqrt(1e-7 + tf.reduce_sum(tf.square(weight_init), axis=0,
                                                                     keepdims=True))
            bias_init = tf.constant_initializer(value=0)
            # define weight and bias
            self.W = tf.Variable(weight_init)
            self.b = tf.Variable(np.zeros((self.nr_hidden,)).astype('float32'))
            # set input shape
            self.input_shape = [batch_size, dim]
            # set output shape
            self.set_output_shape(batch_size)

    def set_output_shape(self, batch_size):
        """
        Just sets the output shape
        """
        self.output_shape = [batch_size, self.nr_hidden]

    def fprop(self, input):
        """
        Implements forward propagation as required by CleverHans Model Interface
        """
        with tf.name_scope(self.name):
            return tf.matmul(input, self.W) + self.b

    def get_params(self):
        """
        Implements get_params as required by CleverHans Model Interface
        """
        return [self.W, self.b]
