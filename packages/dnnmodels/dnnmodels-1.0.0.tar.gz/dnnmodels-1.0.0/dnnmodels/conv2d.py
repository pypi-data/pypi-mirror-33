from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import tensorflow as tf
import numpy as np
from .layer import Layer


class Conv2D (Layer):

    def __init__(self, kernel_shape, strides, padding, nr_filters, name='conv'):
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
            # store each element of input_shape in different variables
            batch_size, rows, cols, input_channels = input_shape
            # add input & output to kernel shape
            kernel_shape = tuple(self.kernel_shape) + \
                (input_channels, self.nr_filters)
            # define kernel init
            kernel_init = tf.random_normal(kernel_shape, dtype=tf.float32)
            kernel_init = kernel_init / tf.sqrt(1e-7 + tf.reduce_sum(tf.square(kernel_init),
                                                                     axis=(0, 1, 2)))
            # initialize kernel
            self.kernel = tf.Variable(kernel_init, name="weights")
            # define bias
            self.b = tf.Variable(
                np.zeros((self.nr_filters,)).astype('float32'), name="biases")
            # set input shape
            self.input_shape = list(input_shape)
            # set output shape
            self.set_output_shape(input_shape, batch_size)

    def set_output_shape(self, input_shape, batch_size):
        """
        This method will compute the output shape
        """
        input_shape = list(input_shape)
        # set batch_size to 1
        input_shape[0] = 1
        # create dummy output
        dummy_batch = tf.zeros(input_shape)
        dummy_output = self.fprop(dummy_batch)
        # get shape of output
        output_shape = [int(e) for e in dummy_output.get_shape()]
        output_shape[0] = batch_size
        # set shape
        self.output_shape = tuple(output_shape)

    def fprop(self, input):
        """
        Implements forward propagation as required by CleverHans Model Interface
        """
        with tf.name_scope(self.name):
            conv_out = tf.nn.conv2d(
                input, self.kernel, strides=(1,) + tuple(self.strides) + (1,),
                padding=self.padding)
            # add bias
            bias = tf.nn.bias_add(conv_out, self.b)
            # return
            return bias

    def get_params(self):
        """
        Implements get_params as required by CleverHans Model Interface
        """
        return [self.kernel, self.b]
