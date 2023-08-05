# -*- coding: utf-8 -*-
import time


def profile(task_function):
    def wrapper(*args, **kwargs):
        starts = time.time()
        task_function(*args, **kwargs)
        ends = time.time()
        print("--- {} seconds ---".format((ends - starts)))

    return wrapper
