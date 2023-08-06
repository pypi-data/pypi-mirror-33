from iminuit import Minuit
import numpy as np
from pprint import pprint


class Func:
    trace = []

    def __call__(self, x):
        self.trace.append(x.copy())
        return np.sum((x - 1) ** 2)


class Grad:
    trace = []

    def __call__(self, x):
        self.trace.append(x.copy())
        return 2 * (x - 1)


func = Func()
grad = Grad()

# func.trace = []
# grad.trace = []

# Minuit.from_array_func(func, np.zeros(2),
#                        pedantic=False, print_level=1).migrad()

# pprint("No gradient")
# pprint(func.trace)
# pprint(grad.trace)

Minuit.from_array_func(func, np.zeros(2), grad=grad,
                       pedantic=False, print_level=1).migrad()

pprint("With gradient")
pprint(func.trace)
pprint(grad.trace)