from iminuit import Minuit
Minuit(lambda x: -x ** 2, pedantic=False, print_level=10).migrad()
