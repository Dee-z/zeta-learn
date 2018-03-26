# -*- coding: utf-8 -*-

import numpy as np
from .base import Layer
from ztlearn.utils import im2col_indices
from ztlearn.utils import col2im_indices

class Pool(Layer):

    def __init__(self, pool_size = (2, 2), strides = (1, 1), padding = 'valid'):
        self.pool_size = pool_size
        self.strides = strides
        self.padding = padding

        # unpack to enhance clarity
        self.pool_height, self.pool_width = self.pool_size
        self.stride_height, self.stride_width = self.strides

    def prep_layer(self): pass

    @property
    def output_shape(self):
        input_channels, input_height, input_width = self.input_shape
        out_height = (input_height - self.pool_height) / self.stride_height + 1
        out_width = (input_width - self.pool_width) / self.stride_width + 1
        assert out_height % 1 == 0
        assert out_width % 1 == 0
        return input_channels, int(out_height), int(out_width)

    def pass_forward(self, inputs, train_mode = True, **kwargs):
        input_num, input_depth, input_height, input_width = inputs.shape
        self.inputs = inputs

        assert (input_height - self.pool_height) % self.stride_height == 0, 'Invalid height'
        assert (input_width - self.pool_width) % self.stride_width == 0, 'Invalid width'

        output_height = (input_height - self.pool_height) / self.stride_height + 1
        output_width = (input_width - self.pool_width) / self.stride_width + 1

        input_reshaped = inputs.reshape(input_num * input_depth, 1, input_height, input_width)
        self.input_col = im2col_indices(input_reshaped, self.pool_height, self.pool_width, padding = ((0, 0), (0, 0)), stride = self.stride_height)

        output, self.pool_cache = self.pool_forward(self.input_col)

        output = output.reshape(int(output_height), int(output_width), input_num, input_depth)
        return output.transpose(2, 3, 0, 1)

    def pass_backward(self, grad):
        input_num, input_depth, input_height, input_width = self.inputs.shape
        self.pool_height, self.pool_width = self.pool_size

        d_input_col = np.zeros_like(self.input_col)
        grad_col = grad.transpose(2, 3, 0, 1).ravel()

        d_input = self.pool_backward(d_input_col, grad_col, self.pool_cache)

        d_input = col2im_indices(d_input_col, (input_num * input_depth, 1, input_height, input_width), self.pool_height, self.pool_width, padding = ((0, 0), (0, 0)), stride = self.stride_height)
        return d_input.reshape(self.inputs.shape)


class MaxPooling2D(Pool):

    def __init__(self, pool_size = (2, 2), strides = (1, 1), padding = 'valid'):
        super().__init__(pool_size, strides, padding)

    def pool_forward(self, input_col):
        max_id = np.argmax(input_col, axis = 0)
        out = input_col[max_id, range(max_id.size)]
        return out, max_id

    def pool_backward(self, d_input_col, grad_col, pool_cache):
        d_input_col[pool_cache, range(grad_col.size)] = grad_col
        return d_input_col


class AveragePool2D(Pool):

    def __init__(self, pool_size = (2, 2), strides = (1, 1), padding = 'valid'):
        super().__init__(pool_size, strides, padding)

    def pool_forward(self, input_col):
        out = np.mean(input_col, axis = 0)
        return out, None

    def pool_backward(self, d_input_col, grad_col, pool_cache = None):
        d_input_col[:, range(grad_col.size)] = 1. / d_input_col.shape[0] * grad_col
        return d_input_col