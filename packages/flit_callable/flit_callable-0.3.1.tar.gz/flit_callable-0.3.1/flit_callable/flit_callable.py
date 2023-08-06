"""An awesome python package"""

__version__ = '0.3.0'


from sklearn.metrics import accuracy_score

from flit_callable.bar import baz


def foo(name):
    print('function in fun')
    baz(name)


def accuracy(test_labels, test_predicts):
    acc = accuracy_score(test_labels, test_predicts)
    return acc
