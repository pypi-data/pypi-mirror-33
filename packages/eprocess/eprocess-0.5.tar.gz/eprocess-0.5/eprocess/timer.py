# -*- coding: utf-8 -*-

from eprocess import eprocess
from eprocess.decorators import profile


@profile
def timer_eprocess(data):
    print('timer_eprocess')
    print('length: {}'.format(len(data)))

    def callback(data_slice):
        return ['prefix-{}'.format(each) for each in data_slice]

    eprocess(data, n=5, callback=callback)


@profile
def timer_process(data):
    print('timer_process')
    print('length: {}'.format(len(data)))
    result = []
    for each in data:
        result.append('prefix-{}'.format(each))


if __name__ == '__main__':
    data = list(range(100000000))
    # timer_eprocess(data)
    timer_process(data)
