import pickle
from datetime import datetime

class enum:
    def __init__(self, ns):
        for idx, n in enumerate(ns):
            setattr(self, n, idx)

exports = {
    'pickle': pickle,
    'datetime': datetime,
    'enum': enum
}

def run_tests():
    pass
