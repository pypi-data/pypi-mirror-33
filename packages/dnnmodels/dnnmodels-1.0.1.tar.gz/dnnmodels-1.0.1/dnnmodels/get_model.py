from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import tensorflow as tf

# TODO: find a better way for this
from .conv2d import Conv2D
from .flatten import Flatten
from .fully_connected import FullyConnected
from .layer import Layer
from .lrn import LocalResponseNormalization
from .max_pool import MaxPool
from .relu import ReLU
from .softmax import Softmax
from .mlp import MLP


def basic_cnn(nb_filters=64, nb_classes=10, input_shape=(None, 28, 28, 1)):
    """
    The default input shape is set to MNIST images
    """
    layers = [Conv2D((8, 8), (2, 2), "SAME", nb_filters, name='conv_1'),
              ReLU(name='relu_1'),
              Conv2D((6, 6), (2, 2), "VALID",
                     nb_filters*2, name='conv_2'),
              ReLU(name='relu_2'),
              Conv2D((5, 5), (1, 1), "VALID",
                     nb_filters*2, name='conv_3'),
              ReLU(name='relu_3'),
              Flatten(name='fc_1'),
              FullyConnected(nb_classes, name='logits'),
              Softmax(name='probs')]

    model = MLP(layers, input_shape)

    return model
