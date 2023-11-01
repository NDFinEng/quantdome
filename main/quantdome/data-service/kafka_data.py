import datetime
import os, os.path
from abc import ABCMeta, abstractmethod

class DataHandler(object):

    __metaclass__ = ABCMeta

    def update_bars(self):

        raise NotImplementedError("Should implement update_bars()")


class HistoricCSVDataHandler(DataHandler):

    def __init__(self, csv_path, symbol_list):

        