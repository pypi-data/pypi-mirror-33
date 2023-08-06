from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np
import tensorflow as tf
from cleverhans.utils_tf import model_train, model_eval, tf_model_load
from cleverhans.utils import AccuracyReport, set_log_level


class Trainer():

    def __init__(self, sess, inference, data_params, train_params):
        """
        Saves parameters and 
        """
        self.session = sess
        self.inference = inference
        # data params
        self.data_params = data_params
        # train params
        self.train_params = train_params
        # instantiate report
        self.report = AccuracyReport()
        # define placeholders
        self.x = tf.placeholder(tf.float32, shape=self.data_params['x_shape'])
        self.y = tf.placeholder(tf.float32, shape=self.data_params['y_shape'])

        # define random number generator
        self.rng = np.random.RandomState([2017, 8, 30])

    def train(self, save=False):
        """
        Wrapper around cleverhans model_train with pre-setup
        """

        model = self.inference
        self.preds = model.get_probs(self.x)

        model_train(sess=self.session,
                    x=self.x,
                    y=self.y,
                    X_train=self.data_params['X_train'],
                    Y_train=self.data_params['Y_train'],
                    predictions=self.preds,
                    evaluate=self.evaluate,
                    save=self.train_params['save_model'],
                    args=self.train_params,
                    rng=self.rng,
                    var_list=model.get_params())

    def evaluate(self):
        """
        Wrapper aroud cleverhans model_eval
        """
        eval_params = {'batch_size': self.train_params['batch_size']}
        acc = model_eval(
            self.session, self.x, self.y, self.preds, self.data_params['X_test'], self.data_params['Y_test'], args=eval_params)
        self.report.clean_train_clean_eval = acc
        print('Test accuracy on legitimate examples: %0.4f' % acc)

    def restore(self, path):
        """
        Wrapper around cleverhans tf.model_load
        """
        return tf_model_load(self.session, path)
