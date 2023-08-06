from typing import Union

import librosa
import numpy
from scipy.io import wavfile

ndarray = numpy.ndarray
genlist = Union[ndarray, list]


# Helper functions:
def secondsToSamples(seconds: float, sr: int) -> int:
    return int(seconds*sr)


def maxIndex(l: genlist) -> int:
    maxI = 0
    maxVal = l[0]
    for i in range(1, len(l)):
        val = l[i]
        if val > maxVal:
            maxVal = val
            maxI = i
    return maxI


def chunkAverage(l: genlist, chunkSize: int) -> genlist:
    if chunkSize > len(l):
        raise ValueError("ChunkSize must be less than length of list.")
    avgList = []
    currentIndex = 0
    while (currentIndex + chunkSize) < len(l):
        avgList.append(numpy.mean(l[currentIndex:currentIndex + chunkSize]))
        currentIndex += chunkSize
    avgList.append(numpy.mean(l[currentIndex:]))
    return avgList


def loadFromFile(fileName: str) -> (list, int):
    sr, _ = wavfile.read(fileName, "rb")
    wf, _ = librosa.core.load(fileName)
    return (wf, sr)


def getNSecondsFromWaveForm(waveForm: genlist, sr: int, seconds: float) -> list:
    return waveForm[:secondsToSamples(seconds, sr)]


# Main functions:
def condenseToSingleChannel(waveForm: genlist) -> list:
    waveFormList = waveForm.tolist()
    if (isinstance(waveFormList[0], list)):
        waveFormSingleChannel = list(
            map(lambda l: l[0], waveForm)
        )
    else:
        waveFormSingleChannel = waveForm
    return waveFormSingleChannel


def rfftAudible(waveForm: genlist) -> ndarray:
    fft = numpy.fft.rfft(waveForm)
    mfft = []
    for n in range(0, len(fft)):
        if n < 150 or n > 3000:
            mfft.append(0)
        else:
            mfft.append(numpy.sqrt(fft[n].real**2 + fft[n].imag**2))
    return mfft


def startingNote(waveForm: ndarray, sr: int) -> int:
    sc = condenseToSingleChannel(waveForm)
    beatSample = getNSecondsFromWaveForm(sc, sr, 1.5)
    trimmed, _ = librosa.effects.trim(beatSample)
    adRFFT = rfftAudible(trimmed)
    return maxIndex(adRFFT)


def startingNoteFromFile(fileName: str) -> int:
    waveForm, sr = loadFromFile(fileName)
    return startingNote(waveForm, sr)
