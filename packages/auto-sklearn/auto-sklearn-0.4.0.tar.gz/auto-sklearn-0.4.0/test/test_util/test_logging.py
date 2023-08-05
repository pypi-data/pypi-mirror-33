import pickle
import unittest

from autosklearn.util import get_logger


class TestLogging(unittest.TestCase):

    def test_pickle_logger(self):
        logger = get_logger('Test')
        p = pickle.dumps(logger, protocol=-1)