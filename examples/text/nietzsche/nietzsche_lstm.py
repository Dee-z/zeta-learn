# -*- coding: utf-8 -*-

from ztlearn.utils import plot_loss
from ztlearn.utils import plot_accuracy
from ztlearn.utils import train_test_split
from ztlearn.utils import gen_char_sequence_xtym

from ztlearn.dl.models import Sequential
from ztlearn.dl.optimizers import register_opt
from ztlearn.dl.layers import LSTM, Flatten, Dense


text = open('../../data/text/nietzsche_short.txt').read().lower()
x, y, len_chars = gen_char_sequence_xtym(text, maxlen = 30, step = 1)
del text

train_data, test_data, train_label, test_label = train_test_split(x, y, test_size = 0.4)
opt = register_opt(optimizer_name = 'rmsprop', momentum = 0.1, learning_rate = 0.01)

# Model definition
model = Sequential()
model.add(LSTM(128, activation = "tanh", input_shape = (30, len_chars)))
model.add(Flatten())
model.add(Dense(len_chars,  activation = 'softmax'))
model.compile(loss = 'categorical-cross-entropy', optimizer = opt)

model_epochs = 20
fit_stats = model.fit(train_data,
                      train_label,
                      batch_size = 128,
                      epochs = model_epochs,
                      validation_data = (test_data, test_label))

plot_loss(model_epochs, fit_stats['train_loss'], fit_stats['valid_loss'])
plot_accuracy(model_epochs, fit_stats['train_acc'], fit_stats['valid_acc'])
