from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import tensorflow as tf
from .layer import Layer


class MaxPool(Layer):

    def __init__(self, ksize, strides, padding, name='maxpool'):
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
        self.input_shape = input_shape
        self.set_output_shape(input_shape)

    def set_output_shape(self, shape):
        """
        Just sets the output shape
        """
        shape = list(shape)
        # set batch size to 1
        shape[0] = 1
        # get dummy output
        dummy_batch = tf.zeros(shape)
        dummy_output = self.fprop(dummy_batch)
        # get shape of dummy output
        output_shape = [int(e) for e in dummy_output.get_shape()]
        output_shape[0] = 1
        # set output_shape
        self.output_shape = tuple(output_shape)

    def fprop(self, input):
        """
        Implements forward propagation as required by CleverHans Model Interface
        """
        with tf.name_scope(self.name):
            return tf.nn.max_pool(input,
                                  ksize=(1,) + tuple(self.ksize) + (1,),
                                  strides=(1,) + tuple(self.strides) + (1,),
                                  padding=self.padding)

    def get_params(self):
        """
        Implements get_params as required by CleverHans Model Interface
        """
        return [self.ksize, self.strides, self.padding]
