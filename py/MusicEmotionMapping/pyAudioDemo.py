import pyaudio
import wave
import sys
import librosa
import soundfile as sf
import tensorflow as tf
from tensorflow import keras
from keras.models import load_model

SR= 44100

#Set the path of the audio file
audio_path="./Audio_Chopin.wav"
audio, nativeSampleRate = librosa.load("./Audio_Chopin.wav", sr= None)


print("SampleRate of the loaded track: ", nativeSampleRate)

#checking for the correct samplingRate

if (nativeSampleRate!=SR):
  audio = librosa.resample(audio,nativeSampleRate, SR)
  sf.write("Audio_Chopin.wav", audio, SR)
  #audio_path="./resampled_track.wav"
  print("This is the new sample rate: ", librosa.get_samplerate(audio_path))

##
class AudioFile:
    chunk = 22050

    def __init__(self, file):
        """ Init audio stream """ 
        self.wf = wave.open(file, 'rb')

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format = self.p.get_format_from_width(self.wf.getsampwidth()),
            channels = self.wf.getnchannels(),
            rate = self.wf.getframerate(),
            output = True
        )

    def play(self):
        """ Play entire file """
        data = self.wf.readframes(self.chunk)
        while data != '':
            self.stream.write(data)
            data = self.wf.readframes(self.chunk)

    def close(self):
        """ Graceful shutdown """ 
        self.stream.close()
        self.p.terminate()
    
        

# Usage example for pyaudio
a = AudioFile("Audio_Chopin.wav")
#a.play()
#a.close()