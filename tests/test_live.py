# import pytest
import quantdome.data as data
import quantdome.event as event
import quantdome.livealpaca as live
import queue
import pandas as pd
import datetime


def create_handler():
    events = queue.Queue()
    return live.LiveAlpacaExecutionHandler()

def run_test():
    bars = create_handler()
    print(bars.getLiveData())

run_test()
