#!/usr/bin/env python
# coding: utf-8

# In[1]:


import speech_recognition as sr
from os import path
import os.path
import operator
from os import system
from os import listdir
from os.path import isfile, join
import wave
import scipy as sc
import librosa
import IPython.display as ipd
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import math
import librosa as lb
import scipy
from sklearn.decomposition import PCA
import pandas as pd
from os import listdir
from os.path import isfile, join
import time
from itertools import product
import datetime
import sys
import librosa.display
import contextlib
import argparse


parser = argparse.ArgumentParser()

#pathF = argv[1]
#randomSeedF = argv[2]
#trainPercentF = argv[3]
#validationPercentF = argv[4]
#testPercentF = argv[5]

parser.add_argument("-p", "--path", dest ="pathF", help="Path to read in the input audio wav file")
parser.add_argument("-output", "--outputPath", dest ="outputPath", help="Path for where to write the new audio wav file")
parser.add_argument("-f", "--frequency", dest = "frequencyF", help="This is the frequency of the sine wave generated", type=int)
parser.add_argument("-i", "--intensity", dest ="intensityF", help="This is the intensity of the sine wave generated", type=int)
parser.add_argument("-window", "--windowSize", dest ="windowSize", help="This is the size of the window inverted in the TDI Attack", type=int)
parser.add_argument("-type", "--typeOfAttack", dest ="type", 
help="Select which type of command to use: TDI, HFA, Time Scale") #add required=True at the end
parser.add_argument("--tempo", dest ="tempo", help="Adjust the tempo of the audio sample for Time Scaling attack") #add required=True at the end




args = parser.parse_args()


# In[3]:


def transcribe(my_path,model):
    wit_key = ''

    AUDIO_FILE =  path.join(my_path)

    # use the audio file as the audio source
    r = sr.Recognizer()
    with sr.AudioFile(my_path) as source:
        audio = r.record(source)  # read the entire audio file

    if(model == 'google'):
        # Google
        try:
            return r.recognize_google(audio)
        except sr.UnknownValueError:
             print("Google: -_-")
            
        except sr.RequestError as e:
            print("Google error; {0}".format(e))

#Time Domain Interval Attack (#1 in paper)
def TDIAttack(type, inputPath, outputPath, windowSize):
    fs, data = scipy.io.wavfile.read(inputPath)
    n = int(len(data)/windowSize)

    #Breaks array into buckets of elements
    #Each bucket has 'windowSize' amount of elements
    def createBuckets(arr, n):
        length = len(arr)
        return [ arr[i*length // n: (i+1)*length // n] 
                 for i in range(n) ]

    #Load audio file
    arr = np.copy(data)
    
    #Store split array into variable
    splitArray = createBuckets(arr,n)

    l = list()

    for x in splitArray[:n]:
        #print(np.fliplr([x])[0])
        l.extend(np.fliplr([x])[0])
    
    #Stores the modified array and casts it as int
    data2 = np.asanyarray(l)
    data2= np.asarray(data2,dtype=np.int16)
    
    #new_audio_path = path[0:-4]+''+str(fs)+'_TDI_WindowSize_'+str(windowSize)+'.wav'

    scipy.io.wavfile.write(outputPath, fs, data2)

    print("\nOriginal Audio Transcription:")
    print(transcribe(inputPath, "google"))
    print("\nPerturbed Audio Transcription:")
    print(transcribe(outputPath, "google"))
    
    
#Time Scaling Attack (#4 in paper)
def TimeScaling(type, inputWav, outputWav, tempo):
    #Uses the sox command from Linux to adjust the tempo of new audio file
    command = "sox " + inputWav + " " + outputWav +  " tempo " + tempo
    os.system(command)
    print("\nOriginal Audio Transcription:")
    print(transcribe(inputWav, "google"))
    print("\nPerturbed Audio Transcription:")
    print(transcribe(outputWav, "google"))


#High Frequency Addition Attack (#3 in paper)
def HFA(type, inputPath, outputPath, frequency, intensity):
    fs, data = scipy.io.wavfile.read(inputPath)
    length = len(data)
    
    #2. Generates a high frequency sin wave
    #Allows the sine wave to be broadcastable to the audio file we are testing
    sampleRate = fs #give it the same sample rate as the original audio
    frequency = frequency
    duration = length/sampleRate #how long the audio sound is in seconds  #4.52

    t = np.linspace(0, duration, sampleRate * duration)  #  Produces a 'duration' long Audio-File in seconds
    y = np.sin(frequency * 2 * np.pi * t) * (intensity)  #Use to control the intensity of the sin wave

    #Uncomment the below line if you want to listen to the sin wave that you have produced from the above line
    #scipy.io.wavfile.write(path[0:-4]+''+'_SINEwav_Frequency'+''+str(fs)+'_Intensity'+str(intensity)+'.wav', sampleRate, y)
    #plt.plot(y)
    #print("This is the length of the sin sound wave:",len(y))

    #3. Merges the sine wave high frequency with the original piece of audio
    resultSound = np.add(data[:length] , y[:length] )

    #4. Casts the result sound from a float to an int
    resultSound = np.asarray(resultSound,dtype=np.int16)
    #print(resultSound)

    #5. Writes the audio file and then transcribes it 
    #new_audio_path = path[0:-4]+''+'_OutputWav_Frequency'+''+str(fs)+'_Intensity'+str(intensity)+'.wav'
    scipy.io.wavfile.write(outputPath, sampleRate, resultSound)
    
    print("\nOriginal Audio Transcription:")
    print(transcribe(inputPath, "google"))
    print("\nPerturbed Audio Transcription:")
    print(transcribe(outputPath, "google"))



#Determines which attack to run based off the input parameter for --type
if (args.type == "TDI"):
    TDIAttack(args.type, args.pathF, args.outputPath, args.windowSize)
elif (args.type == "Time Scale"):
    TimeScaling(args.type, args.pathF, args.outputPath, args.tempo)
elif (args.type == "HFA"):
    HFA(args.type, args.pathF, args.outputPath, args.frequencyF, args.intensityF)
else:
    print("Write the name of the attack surrounded by quotes. Refer to attack.py --help for name of the attacks")



