import pyaudio
import wave
import numpy as np
import wavio
import sys
import librosa
import soundfile as sf
import tensorflow as tf
from tensorflow import keras
from keras.models import load_model
import struct
import matplotlib.pyplot as plt

import math
from MoodMapping import get_color_for_point
from MoodMapping import create_2d_color_map
import cv2
from scipy.spatial import KDTree
import webcolors 
 
class AudioFile:
    chunk = 22050
    SR = 44100
    # choose the number of 500 ms audio cuncks on which apply the avarag
    avg_blocks = 3


    def __init__(self, file):
        
        """ ---------- Create the color map ----------  """ 

        colors = {"coral": [255,127,80],
                    "pink": [255, 192, 203],
                    "orange": [255, 165, 0],
                    "blue": [0, 0, 205],
                    "green": [0, 205, 0],
                    "red": [205, 0, 0],
                    "yellow": [204, 204, 0]}
        angry_pos = [-0.8, 0.5]
        fear_pos = [-0.3, 0.8]
        happy_pos = [0.6, 0.6]
        calm_pos = [0.4, -0.5]
        sad_pos = [-0.6, -0.4]

        bgr = create_2d_color_map([angry_pos, fear_pos, happy_pos,
                                    calm_pos, sad_pos],
                                    [colors["red"],  colors["yellow"],
                                    colors["orange"], colors["green"],
                                    colors["blue"]], 200, 200)

        cv2.imshow('Signal', bgr)
        ch = cv2.waitKey(10000)
        
        
        
        
        
        """ ---------- Audio Analysis and Color Mapping ---------- """ 
    
        #Load the audio and resampling it at 44100
        
        audio, nativeSampleRate = librosa.load(file, sr=None)
        audio = librosa.resample(audio, nativeSampleRate, self.SR)
        sf.write(audio_path, audio, self.SR)
        print("Sampling rate: ", librosa.get_samplerate(file))
        
        
        #Load the model

        pred_model = load_model("./best_model.hdf5", compile=False)
        
        #Stream the data 

        stream = librosa.stream(file,
                        block_length=1,
                        frame_length=self.chunk,
                        hop_length=self.chunk)

        self.numChunks = 1

        valence_avg = 0
        arousal_avg = 0
        
        self.va = []

        #Predict the VA values for each chunk
        
        for y in stream:

            buff = np.array(np.zeros(22050))
            buff[0:y.shape[0]] = y[:]
            buff = np.expand_dims(buff, axis=0)  
                   
            #Valence and Arousal computation
            valence_avg += (pred_model.predict(buff)[0])[1]
            arousal_avg += (pred_model.predict(buff)[0])[0]
            
            #print("Arousal and Valence   ", (pred_model.predict(buff)[0])[1], (pred_model.predict(buff)[0])[0])

            #Store the VA avarage values  
            if(self.numChunks%self.avg_blocks == 0):

                valence_avg = valence_avg/self.avg_blocks
                arousal_avg = arousal_avg/self.avg_blocks
                
                #print("\n\nAVARAGE -> Arousal and valence  ", arousal_avg, valence_avg, "\n\n")
                
                
                self.va.append([arousal_avg, valence_avg])
                    
                valence_avg = 0
                arousal_avg = 0
    
            self.numChunks = self.numChunks + 1
        

        
        self.numAvgValues = math.floor((self.numChunks-1)/self.avg_blocks)
        
        print("Number of Avagarage Values : ", self.numAvgValues, "\nNumber of chuncks processed : ", self.numChunks, "\nNumber of chuncks of each avarage: ",  self.avg_blocks, "\n")
           
        """ ---------- PROVA NORMALIZZAZIONE ---------- """
        
        scaling_factor = 1.5
        val = []
        ar = []
        
        for i in range(self.numAvgValues):
            
            val.append(self.va[i][1])
            ar.append(self.va[i][0]) 
        
        val = np.array(val)
        ar = np.array(ar)
        
        val = np.multiply(val, scaling_factor)
        ar = np.multiply(ar, scaling_factor)       
        
        val = np.clip(val, -1, 1)
        ar = np.clip(ar, -1, 1)
        
        val = val.tolist()
        ar = ar.tolist()
        
        for i in range(self.numAvgValues):
            self.va[i] = [ar[i], val[i]]
            #print("Arousal and Valence : ", self.va[i])  
            
                    
        
        """ ---------- Color Mapping for each VA avg value ---------- """ 
        
        self.colorMapped = []
        
        
        for i in range(self.numAvgValues):
            #print(i)
            #print("Arousal avarage :", self.va[i][0])
            #print("Valence avarage :", self.va[i][1])
            
            arousal = self.va[i][0]
            valence = self.va[i][1]
            
            color =  get_color_for_point([arousal, valence], [angry_pos, fear_pos, happy_pos,
                            calm_pos, sad_pos], [colors["red"],  colors["yellow"],
                            colors["orange"], colors["green"],
                            colors["blue"]])
            
            
            self.colorMapped.append(color)
            
        
            
        #print("number of chuncks processed : ", self.numChunks)
        #print("number of VA avarage values : ", self.numAvgValues, "\n \n")

        
        
        """ ---------- Init the audio stream ---------- """ 
  
        self.wf = wave.open(file, 'rb')   
        self.p = pyaudio.PyAudio()
    
        self.stream = self.p.open(
                format = self.p.get_format_from_width(self.wf.getsampwidth()),
                channels = self.wf.getnchannels(),
                rate = self.wf.getframerate(),
                output = True)
    
    
    
    
    
    def play(self):
        
        """ ---------- Play entire file and Send OSC ---------- """      
        
        cnt = 1
        i = 0
        valence_avg = 0
        arousal_avg = 0 
        
        #Send an OSC message every 'self.avg_blocks' chuncks
        
        data = self.wf.readframes(self.chunk)
        
        while (data != '') & (cnt<=(self.numChunks-1)):  
                     
            if(cnt%self.avg_blocks == 0):
                #Send OSC message with the RGB values    
                print("Arousal avarage num  ", i, " : ",  self.va[i][0])
                print("Valence avarage num  ", i, " : ", self.va[i][1])
                print("Corresponding RGB color : ", self.colorMapped[i], "\n\n")
                
                
                #print("Corresponding hex value of the color", webcolors.rgb_to_hex((round(self.colorMapped[i][0]),round(self.colorMapped[i][1]),round(self.colorMapped[i][2]))))
                #Showing the color into an image, it will block for a bit the script then keep going
                plt.imshow([[(round(self.colorMapped[i][0]),round(self.colorMapped[i][1]),round(self.colorMapped[i][2]))]])
                
                plt.show(block=False)
                plt.pause(2)  
                plt.close()
                
                # plt.pause(0.1)
                # plt.close()
                #actual_name, closest_name = get_colour_name(self.colorMapped[i])
                #print("Corresponding  color name : ",closest_name)
                #print(i)
                i = i + 1
                    
            
            #print(cnt)
            cnt = cnt + 1
            
              
            self.stream.write(data)
            data = self.wf.readframes(self.chunk)
    
            

    def close(self):
        """ Graceful shutdown """ 
        self.stream.close()
        self.p.terminate()
        


def closest_colour(requested_colour):
    min_colours = {}
    for key, name in webcolors.css3_hex_to_names.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]

def get_colour_name(requested_colour):
    try:
        closest_name = actual_name = webcolors.rgb_to_name(requested_colour)
    except ValueError:
        closest_name = closest_colour(requested_colour)
        actual_name = None
    return actual_name, closest_name





# def convert_rgb_to_names(rgb_tuple):
    
#     # a dictionary of all the hex and their respective names in css3
#     css3_db = css3_hex_to_names
#     names = []
#     rgb_values = []
#     for color_hex, color_name in css3_db.items():
#         names.append(color_name)
#         rgb_values.append(hex_to_rgb(color_hex))
    
#     kdt_db = KDTree(rgb_values)
#     distance, index = kdt_db.query(rgb_tuple)
#     return f'closest match: {names[index]}'


#Set the path of the audio file
audio_path="wavTracks/Slipknot - Psychosocial.wav"
          

# Usage example for pyaudio
a = AudioFile(audio_path)
a.play()
a.close()