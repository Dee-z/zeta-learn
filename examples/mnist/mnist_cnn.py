# -*- coding: utf-8 -*-

from sklearn import datasets

from zeta.utils import unhot
from zeta.utils import one_hot
from zeta.utils import plot_loss
from zeta.utils import plot_accuracy
from zeta.utils import print_results
from zeta.utils import train_test_split
from zeta.utils import plot_mnist_img_results
from zeta.utils import plot_mnist_img_samples

from zeta.dl.models import Sequential
from zeta.dl.optimizers import register_opt
from zeta.dl.layers import BatchNomalization, Conv2d
from zeta.dl.layers import Dropout, Dense, Flatten, MaxPooling2d

data = datasets.load_digits()
plot_mnist_img_samples(data)

train_data, test_data, train_label, test_label = train_test_split(data.data,
                                                                  data.target,
                                                                  test_size = 0.33,
                                                                  random_seed = 5)

opt = register_opt(optimizer_name = 'adam', momentum = 0.01, learning_rate = 0.001)

model = Sequential(init_method = 'he-uniform')
model.add(Conv2d(filters = 32, kernel_size = (3,3), activation = 'relu', input_shape = (1,8,8), padding = 'same'))
model.add(Dropout(0.25))
model.add(BatchNomalization())
model.add(Conv2d(filters = 64, kernel_size = (3,3), activation = 'relu', padding = 'same'))
model.add(MaxPooling2d(pool_size = (2,2)))
model.add(Dropout(0.25))
model.add(BatchNomalization())
model.add(Flatten())
model.add(Dense(256, activation = 'relu'))
model.add(Dropout(0.5))
model.add(BatchNomalization())
model.add(Dense(10, activation = 'softmax')) # 10 mnist classes
model.compile(loss = 'categorical-cross-entropy', optimizer = opt)

model_epochs = 12
fit_stats = model.fit(train_data.reshape(-1,1,8,8),
                      one_hot(train_label),
                      batch_size = 128,
                      epochs = model_epochs,
                      validation_data = (test_data.reshape(-1,1,8,8), one_hot(test_label)),
                      shuffle_data = True)

predictions = unhot(model.predict(test_data.reshape(-1,1,8,8), True))

print_results(predictions, test_label)
plot_mnist_img_results(test_data, test_label, predictions)

plot_loss(model_epochs, fit_stats['train_loss'], fit_stats['valid_loss'])
plot_accuracy(model_epochs, fit_stats['train_acc'], fit_stats['valid_acc'])
