# -*- coding: utf-8 -*-

import numpy as np


from ztlearn.utils import LogIfBusy
from ztlearn.utils import computebar
from ztlearn.utils import minibatches
from ztlearn.dl.layers import Activation
from ..objectives import ObjectiveFunction as objective

class Sequential:

    def __init__(self, init_method = 'he_normal'):
        self.layers = []
        self.init_method = init_method

    @property
    def get_layers(self):
        return self.layers

    def add(self, layer):
        if self.layers:
            layer.input_shape = self.layers[-1].output_shape

        if hasattr(layer, 'weight_initializer'):
            layer.weight_initializer = self.init_method
        self.append_layer(layer)

        if hasattr(layer, 'layer_activation') and layer.layer_activation is not None:
            self.append_layer(Activation(layer.layer_activation, input_shape = self.layers[-1].output_shape))

    def append_layer(self, layer):
        layer.prep_layer()
        self.layers.append(layer)

    def compile(self, loss = 'categorical_crossentropy', optimizer = {}):
        self.loss = loss
        for layer in self.layers:
            if hasattr(layer, 'weight_optimizer'):
                layer.weight_optimizer = optimizer

    @LogIfBusy
    def fit(self, train_data, train_label, batch_size, epochs, validation_data = (), shuffle_data = True, verbose = True):
        fit_stats = {"train_loss": [], "train_acc": [], "valid_loss": [], "valid_acc": []}

        for epoch_idx in np.arange(epochs):
            batch_stats = {"batch_loss": [], "batch_acc": []}

            for train_batch_data, train_batch_label in minibatches(train_data, train_label, batch_size, shuffle_data):
                loss, acc = self.train_batches(train_batch_data, train_batch_label)

                batch_stats["batch_loss"].append(loss)
                batch_stats["batch_acc"].append(acc)

                if verbose:
                    print('TRAINING: Epoch-{} loss: {:.2f} accuracy: {:.2f}'.format(epoch_idx+1, loss, acc))

            fit_stats["train_loss"].append(np.mean(batch_stats["batch_loss"]))
            fit_stats["train_acc"].append(np.mean(batch_stats["batch_acc"]))

            if validation_data:
                val_loss, val_acc = self.test_batches(validation_data[0], validation_data[1])

                fit_stats["valid_loss"].append(val_loss)
                fit_stats["valid_acc"].append(val_acc)

                if verbose:
                    print('VALIDATION: Epoch-{} loss: {:.2f} accuracy: {:.2f}'.format(epoch_idx+1, val_loss, val_acc))
            
            if not verbose:
                computebar(epochs, epoch_idx)
            
        return fit_stats

    def train_batches(self, train_batch_data, train_batch_label):
        predictions = self.foward_pass(train_batch_data, train_mode = True)

        loss = np.mean(objective(self.loss).forward(predictions, train_batch_label))
        acc = objective(self.loss).accuracy(predictions, train_batch_label)

        self.backward_pass(objective(self.loss).backward(predictions, train_batch_label))

        return loss, acc

    def test_batches(self, test_batch_data, test_batch_label, train_mode = False):
        predictions = self.foward_pass(test_batch_data, train_mode = train_mode)

        loss = np.mean(objective(self.loss).forward(predictions, test_batch_label))
        acc = objective(self.loss).accuracy(predictions, test_batch_label)

        return loss, acc

    @LogIfBusy
    def evaluate(self, test_data, test_label, batch_size = 128, shuffle_data = True, verbose = True):
        eval_stats = {"loss": [], "acc": []}

        for test_data_batch_data, test_batch_label in minibatches(test_data, test_label, batch_size, shuffle_data):
            loss, acc = self.test_batches(test_data_batch_data, test_batch_label)

            eval_stats["loss"].append(loss)
            eval_stats["acc"].append(acc)

            if verbose:
                print('VALIDATION: loss: {:.2f} accuracy: {:.2f}'.format(loss, acc))

        return eval_stats

    def predict(self, sample_input, train_mode = False):
        return self.foward_pass(sample_input, train_mode = train_mode)

    def summary(self): pass

    def foward_pass(self, inputs, train_mode = False):
        layer_output = inputs
        for layer in self.layers:
            layer_output = layer.pass_forward(layer_output, train_mode)
        return layer_output

    def backward_pass(self, loss_grad):
        for layer in reversed(self.layers):
            loss_grad = layer.pass_backward(loss_grad)