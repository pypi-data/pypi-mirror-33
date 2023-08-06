import os
import sys
from typing import Tuple

import librosa
import numpy as np
from scipy.io import wavfile

from . import tools

analysis = tools.analysis
parseMusic = tools.parseMusic


def getSPB(bpm: float) -> float:
    bps = bpm/60
    return 1.0/bps


def addList(l1: list, l2: list) -> list:
    if len(l1) != len(l2):
        raise ValueError("Lists must be of Equal Length")
    comb = zip(l1, l2)
    return list(map(lambda t: t[0] + t[1], comb))


def mdArrayAverage(md: list) -> list:
    sumArr = md[0]
    for i in range(1, len(md)):
        sumArr = addList(sumArr, md[i])
    return list(map(lambda v: float(v)/len(md), sumArr))


def shiftPitchBy(noteArray: np.ndarray, sr: int, shift: float) -> np.ndarray:
    return librosa.effects.pitch_shift(noteArray, sr, shift)


def speedUpBy(noteArray: np.ndarray, sr: int, factor: float) -> np.ndarray:
    spedUp = librosa.effects.time_stretch(noteArray, factor)
    return spedUp


def speedUpTo(noteArray: np.ndarray, sr: int, shiftTo: float) -> np.ndarray:
    dur = librosa.core.get_duration(noteArray, sr)
    ratio = dur/shiftTo
    spedUp = speedUpBy(noteArray, sr, ratio)
    return spedUp


def pitchTo(noteArray: np.ndarray, sr: int, shiftTo: int, bpm: float) -> np.ndarray:
    spb = getSPB(bpm)

    currentFrequency = analysis.startingNote(noteArray, sr)
    freqRatio = shiftTo/float(currentFrequency)
    shift = np.log2(freqRatio)
    shiftedPitchWF = shiftPitchBy(noteArray, sr, 12*shift)
    return speedUpTo(shiftedPitchWF, sr, spb)

def emptyBeatTrack(likeList: np.ndarray, sr: int, bpm: float):
    spb = getSPB(bpm)
    emptyLike = np.full_like(likeList, .01)
    return speedUpTo(emptyLike, sr, spb)

def sampleIntoSong(sampleTrack: np.ndarray, sr: int, frequencyList: list, bpm: float) -> np.ndarray:
    song = np.array([])
    for freqList in frequencyList:
        nextParts = []
        for freq, duration in freqList:
            if freq != 0:
                nextParts.append(pitchTo(sampleTrack, sr, freq, bpm))
            else:
                nextParts.append(emptyBeatTrack(sampleTrack, sr, bpm))
        avgArr = np.array(mdArrayAverage(nextParts))
        song = np.concatenate((song, speedUpBy(avgArr, sr, 1.0/duration)))
    return song


def sampleWAVFileIntoMusic(
                    wavFileName: str,
                    musicFileName: str,
                    bpm: float
                    ) -> Tuple[np.ndarray, int]:
    sr, _ = wavfile.read(wavFileName)
    waveForm, _ = librosa.core.load(wavFileName, sr)

    waveForm, _ = librosa.effects.trim(waveForm)
    freqList = parseMusic.fileToFrequency(musicFileName)

    wP = sampleIntoSong(waveForm, sr, freqList, bpm=bpm)
    return (wP, sr)


if __name__ == "__main__":
    bpm = 100

    filename1 = sys.argv[1]
    filename2 = sys.argv[2]
    dir1, name1 = os.path.split(filename1)
    dir2, name2 = os.path.split(filename2)
    name1 = name1.replace(".wav", "")
    name2 = name2.replace(".music", "")

    if len(sys.argv) > 3:
        bpm = int(sys.argv[3])

    wP, sr = sampleWAVFileIntoMusic(filename1, filename2, bpm)
    librosa.output.write_wav("{0}_ShiftedTo_{1}.wav".format(name1, name2), wP, sr)
    os.system("play {0}_ShiftedTo_{1}.wav".format(name1, name2))
