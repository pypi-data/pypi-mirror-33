import unittest
from ttlab.optical_spectroscopy.insplorion import Insplorion
import numpy as np


class InsplorionTestCases(unittest.TestCase):

    class InsplorionDataExample:
        filename = 'tests/mock_data/light_spectrometer_example.ins'
        wavelength = np.array([350.76616465291863, 351.82069361649877, 352.87511994500551])
        time = np.array([3.0346465, 8.0355699, 13.0370031])
        intensity = np.array([[422.49-368.56, 499.73-460.23, 446.08-403.37], [422.49-367.69, 499.73-455.12, 446.08-419.51], [422.49-361.73, 499.73-450.99, 446.08-418.43]])

    def test_import_insplorion(self):
        result = Insplorion(self.InsplorionDataExample.filename)
