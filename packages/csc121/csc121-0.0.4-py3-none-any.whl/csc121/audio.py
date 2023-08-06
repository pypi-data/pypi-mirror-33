"""
Wrapper module that provides a simple interface for reading/writing wav files.

Authors: John Dale, Raghuram Ramanujan, Harry Zhou
"""
from scipy.io import wavfile
import numpy as np


def read_wav(filename):
    """Returns the audio data from specified file.

    This function opens the file with the given name (which must be in the .wav
    format) and returns its audio contents as a list of integers.

    Example usage:
        samples = read_wav('foo.wav')

    This opens the audio file foo.wav and returns its audio contents
    as a list of integers that is stored in the variable named samples.

    Parameters:
        filename - a string containing the name of the wav file to be read.

    Returns:
        A list of ints, containing audio samples from the specified file.
    """
    _, samples = wavfile.read(filename)
    return samples.tolist()


def write_wav(samples, filename, sampling_rate=44100):
    """Writes the given samples to the specified wav file

    This function saves the supplied audio data to the specified file (which
    must have a .wav extension).

    Parameters:
        samples - a list of integers representing the audio data.
        filename - a string containing the name of the output file.
        sampling_rate - this optional parameter specifies the sampling rate at
                        which to encode the audio data.

    Returns:
        None
    """
    samples = np.asarray(samples, dtype=np.int16)
    wavfile.write(filename, sampling_rate, samples)
