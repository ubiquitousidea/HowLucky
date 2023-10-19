import time
import yaml
from numpy.random import permutation, exponential
from yaml import Loader, Dumper
from json import dumps
from PIL import Image
from numpy import array


# -----------------------------------------------------------------------------
# - basic i/o functions -------------------------------------------------------
# -----------------------------------------------------------------------------


def load_yaml(f):
    """
    load a yaml file into a dictionary
    :param f: yaml input file name
    :return: dictionary
    """
    with open(f) as stream:
        d = yaml.load(stream, Loader=Loader)
    return d


def write_yaml(data, fname):
    """
    output a dictionary as a yaml file
    :param data: dictionary
    :param fname: yaml output file name
    :return: None
    """
    if not fname.lower().endswith("yaml"):
        fname = fname.split(".")[0] + ".yaml"
    with open(fname, "w") as stream:
        yaml.dump(data, stream, Dumper=Dumper)
    return None


def dump_json(d):
    """
    output dictionary as a json string
    :param d: dictionary
    :return: string
    """
    return dumps(d, indent=4, sort_keys=True)


# -----------------------------------------------------------------------------
# - randomizing functions -----------------------------------------------------
# -----------------------------------------------------------------------------


class Randomize(object):
    """
    a class for iterating in a random order
    """

    def __init__(self, iterable, limit=None):
        self.iterable = iterable
        self._n = len(self.iterable)
        self._limit = limit

    def __iter__(self):
        j = 0
        for i in permutation(self._n):
            j += 1
            if self._limit is not None and j > self._limit:
                raise StopIteration
            yield self.iterable[i]


def sleep_random(beta=60, quiet=False):
    """
    sleep for a random time (exponential distributed)
    :param beta: expected value
    :param quiet: if False, print the sleep time before sleeping
    :return: None
    """
    n = 1 + exponential(beta, 1)[0]
    if not quiet:
        print(f"sleeping {round(n, 2)} seconds")
    time.sleep(n)
    return None


def just_try(func):
    """
    decorator to default object lookup failure to return an empty string
    :param func: function to be decorated
    :return: function that returns blank string if call fails
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return None

    return wrapper


# - Color operations -


def opposite_color(path):
    """
    :param imgurl: image url
    :return: opposite average color
    """
    average_color = array(Image.open(path)).mean(axis=0).mean(axis=0)
    return array([255, 255, 255]) - average_color
