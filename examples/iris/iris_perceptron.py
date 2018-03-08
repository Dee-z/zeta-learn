# -*- coding: utf-8 -*-

from sklearn import datasets

from zeta.utils import unhot
from zeta.utils import one_hot
from zeta.utils import plot_acc_loss
from zeta.utils import print_results
from zeta.utils import train_test_split

from zeta.dl.optimizers import register_opt
from zeta.ml.classification import Perceptron

data = datasets.load_iris()
train_data, test_data, train_label, test_label = train_test_split(data.data,
                                                                  one_hot(data.target),
                                                                  test_size = 0.33,
                                                                  random_seed = 5)

opt = register_opt(optimizer_name = 'adam', momentum = 0.01, learning_rate = 0.001)
model = Perceptron(epochs = 500, activation = 'leaky-relu',
                                 loss = 'categorical-cross-entropy',
                                 init_method = 'he-normal',
                                 optimizer = opt)

fit_stats = model.fit(train_data, train_label, False)

print_results(unhot(model.predict(test_data)), unhot(test_label))
plot_acc_loss(len(fit_stats["train_loss"]), fit_stats['train_acc'], fit_stats['train_loss'])
