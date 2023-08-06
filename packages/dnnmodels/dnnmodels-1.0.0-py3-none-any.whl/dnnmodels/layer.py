from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


class Layer(object):

    def __init__(self):
        pass

    def get_output_shape(self):
        return self.output_shape

    def set_input_shape(self, shape):
        self.input_shape = shape
        self.set_output_shape(shape)

    def set_output_shape(self, shape):
        self.output_shape = shape
