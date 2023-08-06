"""
Wrapper module that provides a simple interface for reading/writing JPEGs.

Author: Raghuram Ramanujan
"""
from PIL import Image
import numpy as np


def get_channel(filename, channel):
    """ Returns the data from the specified channel in the specified file.

    Example usage:
        red = get_channel('foo.jpg', 'red')

    This opens the file foo.jpg, reads the image data in that file, and
    returns the values for the red color channel for each pixel in the
    form of a nested list. The contents of the nested list are integers
    in the range 0-255.

    Parameters:
        filename - a string containing the name of the file to be opened.
        channel - one of 'red', 'green' or 'blue', to indicate which color
                  channel is to be returned.

    Returns:
        A nested list of ints representing the data from the specified
        channel.
    """
    channels = {'red': [], 'green': [], 'blue': []}
    if channel not in channels.keys():
        raise ValueError('Requested channel must be one '
                         'of {}'.format(set(channels.keys())))
    try:
        img = Image.open(filename)
    except IOError:
        raise IOError('The file {} could not be found. Is this file in the same'
                      ' folder as your code?'.format(filename))

    channels['red'], channels['green'], channels['blue'] = img.split()
    return np.array(channels[channel]).tolist()


def _is_rectangular(lst):
    """ Returns whether the supplied nested list is a rectangular 2-d array. """
    try:
        row_length = len(lst[0])
        return all(len(row) == row_length for row in lst)
    except:
        return False


def write_jpg(red, green, blue, filename):
    """ Writes the supplied image data to a jpg file with the specified name.

    This function takes the color channel information supplied via the
    the three nested lists (red, green, blue), combines them and creates a
    new jpg file in the current folder with the specified name.

    Parameters:
        red - a nested list containing the data for the red channel
        green - a nested list containing the data for the green channel
        blue - a nested list containing the data for the blue channel
               All three nested lists must have the same dimensions, and be
               composed of integers in the range 0--255
        filename - a string containing the name of the output jpg file

    Returns:
        None
    """
    if (   (not _is_rectangular(red))
        or (not _is_rectangular(green))
        or (not _is_rectangular(blue))
        or (not (len(red) == len(green) == len(blue)))
        or (not (len(red[0]) == len(green[0]) == len(blue[0])))):
        raise ValueError('Invalid image data: the red, blue and green nested'
                         ' lists must have matching dimensions (i.e., the same'
                         ' number of rows and columns).')

    img = Image.new(mode='RGB', size=(len(red[0]), len(red)))
    pixels = [(r, g, b) for r, g, b in
              zip(np.ravel(red), np.ravel(green), np.ravel(blue))]
    img.putdata(pixels)
    img.save(filename, "JPEG")
