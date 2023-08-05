import itertools
import logging


def eprocess(data, n=10, callback=None, pct=False):
    """
    Process a list of data by batching with n sequences and return the slice
    Args:
        :param data: [] => The list of data
        :param n: int = the slice number
        :param callback: function = The function to process the slice
        :param pct: bool = Show the percentage

    Returns:
        [] = A list of slices
    """
    start = 0
    end = n

    while True:
        input_data = data[start:end]

        if not input_data:
            break

        yield input_data

        if pct:
            length = len(data)
            info = '{} of {} - {}%'.format(end, length, round(end / length * 100))
            logging.info(info)
            print(info)

        if callback:
            callback(input_data)

        start = end
        end += n


def eprocessr(data, n=10, callback=None, pct=False):
    """
    Process a list of data by batching with n sequences and return the result of the callback that process the slice
    Args:
        :param data: [] => The list of data
        :param n: int = the slice number
        :param callback: function = The function to process the slice
        :param pct: bool = Show the percentage

    Returns:
        [] = A list of slices
    """
    start = 0
    end = n

    while True:
        input_data = data[start:end]

        if not input_data:
            break

        if pct:
            length = len(data)
            info = '{} of {} - {}%'.format(end, length, round(end / length * 100))
            logging.info(info)
            print(info)

        if callback:
            yield callback(input_data)

        start = end
        end += n


def eprocessd(data, n=10, callback=None, pct=False):
    """
    Process a dict of data by batching with n sequences and return the slice
    Args:
        :param data: dict = The dictionary of data
        :param n: int = the slice number
        :param callback: function = The function to process the slice
        :param pct: bool = Show the percentage

    Returns:
        [] = A list of slices
    """
    start = 0
    end = n

    while True:
        input_data = dict(itertools.islice(data.items(), start, end))

        if not input_data:
            break

        yield input_data

        if pct:
            length = len(data)
            info = '{} of {} - {}%'.format(end, length, round(end / length * 100))
            logging.info(info)
            print(info)

        if callback:
            callback(input_data)

        start = end
        end += n


def eprocessdr(data, n=10, callback=None, pct=False):
    """
    Process a dict of data by batching with n sequences and return the result of the callback that process the slice
    Args:
        :param data: dict = The dictionary of data
        :param n: int = the slice number
        :param callback: function = The function to process the slice
        :param pct: bool = Show the percentage

    Returns:
        [] = A list of slices
    """
    start = 0
    end = n

    while True:
        input_data = dict(itertools.islice(data.items(), start, end))

        if not input_data:
            break

        if pct:
            length = len(data)
            info = '{} of {} - {}%'.format(end, length, round(end / length * 100))
            logging.info(info)
            print(info)

        if callback:
            yield callback(input_data)

        start = end
        end += n
