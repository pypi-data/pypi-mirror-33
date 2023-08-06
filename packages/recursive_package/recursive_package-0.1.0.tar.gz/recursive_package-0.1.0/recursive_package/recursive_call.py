from flit_callable.flit_callable import foo
from sklearn.metrics import accuracy_score


def call_foo_fun(name):
    foo(name)


def call_accuracy(test_label, test_predict):
    return accuracy_score(test_label, test_predict)