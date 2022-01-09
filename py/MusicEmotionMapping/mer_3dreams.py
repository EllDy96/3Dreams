import pyaudio
import wave
import wavio
import sys
import librosa
import soundfile as sf
import tensorflow as tf
from tensorflow import keras
from keras.models import load_model
import struct
import numpy as np
import math
from MoodMapping import get_color_for_point
from MoodMapping import create_2d_color_map
import cv2
import matplotlib.pyplot as plt
from pythonosc import udp_client


#Set OSC port
ip = "127.0.0.1"
port = 57121

client = udp_client.SimpleUDPClient(ip, port)



class AudioFile:
    chunk = 22050
    SR = 44100
    # choose the number of 500 ms audio cuncks on which apply the avarage
    avg_blocks = 6
    TESTING= True #set that to True if you want to dynamically see the output color for each avg_blocks from this script, but remamber to fix that to False at the testing-end 

    def __init__(self, file):
        
        """ ---------- Create the color map ----------  """ 

        colors = {  "red": [200, 0, 0],
                            "orange": [255, 120, 20],
                            "coral": [255,127,80], 
                            "pink": [255, 192, 203],
                            "yellow": [204, 204, 0], 
                            "lightGreen": [0, 225, 0],
                            "green": [0, 190, 0],
                            "darkGreen": [0, 100, 0],
                            "purple":[85, 0, 100],
                            "lightBlue": [0, 0, 205],
                            "blue": [0, 0, 150],
                            "darkBlue": [0, 0, 139]} 
        angry_pos = [-0.8, 0.5]#red
        fear_pos = [-0.3, 0.8]#coral
        allert_pos = [-0.1, 0.9]#orange
        happy_pos = [0.8, 0.1]#yellow 
        serene_pos = [0.2, -0.5]#lightgreen
        relaxed_pos=[0.7,-0.6]#green
        calm_pos = [0.3,-0.7]#DarkGreen
        sad_pos = [-0.9, -0.1] #purple
        depressed_pos = [-0.6, -0.5] #lighBlue
        depressed_pos_2 = [-0.3, -0.5]#lightBlue
        bored_pos = [-0.8, -0.7] #blue 
        fatigue_pos= [-0.3,-0.8]#darkBlue

 
        bgr = create_2d_color_map([angry_pos, fear_pos, allert_pos,  happy_pos, serene_pos,relaxed_pos,
                                    calm_pos, sad_pos, depressed_pos,depressed_pos_2, bored_pos, fatigue_pos], 
                                    [colors["red"],  colors["coral"],colors["orange"], colors["yellow"], 
                                    colors["lightGreen"], 
                                    colors["green"],colors["darkGreen"],colors["purple"],colors["lightBlue"], 
                                    colors["lightBlue"],colors["blue"], colors["darkBlue"]], 400, 400)

 
        cv2.imshow('VA_ColorMap', bgr)
        ch = cv2.waitKey(10000)
        

        """ ---------- Audio Analysis and Color Mapping ---------- """ 
        
        
        
        #Load the audio and resampling it at 44100
        
        audio, nativeSampleRate = librosa.load(file, sr=None)
        audio = librosa.resample(audio, nativeSampleRate, self.SR)
        sf.write(audio_path, audio, self.SR)
        print("Sampling rate: ", librosa.get_samplerate(file))
        
        
        #Load the model

        pred_model = load_model("py/MusicEmotionMapping/best_model.hdf5", compile=False)
        
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
           
        """ ---------- Scaling VA Values ---------- """
        
        scaling_factor_val = 1.5
        scaling_factor_ar = 2
        val = []
        ar = []
        
        for i in range(self.numAvgValues):
            
            val.append(self.va[i][1])
            ar.append(self.va[i][0]) 
        
        val = np.array(val)
        ar = np.array(ar)
        
        val = np.multiply(val, scaling_factor_val)
        ar = np.multiply(ar, scaling_factor_ar)       
        
        val = np.clip(val, -1, 1)
        ar = np.clip(ar, -1, 1)
        
        val = val.tolist()
        ar = ar.tolist()
        
        for i in range(self.numAvgValues):
            self.va[i] = [ar[i], val[i]]
            
            
                    
        
        """ ---------- Color Mapping for each VA avg value ---------- """ 
        
        self.colorMapped = []
        
        
        for i in range(self.numAvgValues):
            
            arousal = self.va[i][0]
            valence = self.va[i][1]
            
            color =  get_color_for_point([valence, arousal], [angry_pos, fear_pos, allert_pos,  happy_pos, serene_pos,relaxed_pos,
                                    calm_pos, sad_pos, depressed_pos,depressed_pos_2, bored_pos, fatigue_pos], 
                                    [colors["red"],  colors["coral"],colors["orange"], colors["yellow"], 
                                    colors["lightGreen"], 
                                    colors["green"],colors["darkGreen"],colors["purple"],colors["lightBlue"], 
                                    colors["lightBlue"],colors["blue"], colors["darkBlue"]])
            
            
            color = [round(color[0]), round(color[1]), round(color[2])]
            
            
            self.colorMapped.append(color)
            

        
        
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
        
        #Send an OSC message every 'self.avg_blocks' chuncks
        
        data = self.wf.readframes(self.chunk)
        
        while (data != '') & (cnt<=(self.numChunks-1)):  
                     
            if(cnt%self.avg_blocks == 0):
                #Send OSC message with the RGB values    
                print("Arousal avarage num  ", i, " : ",  self.va[i][0])
                print("Valence avarage num  ", i, " : ", self.va[i][1])
                print("Corresponding RGB color : ", self.colorMapped[i], "\n\n")
                
                #sending the OSC messagge
                client.send_message("/RGB", self.colorMapped[i]) 

                #Testing the color with a real time plot                
                if (self.TESTING):
                    plt.imshow([[(self.colorMapped[i][0],self.colorMapped[i][1],self.colorMapped[i][2])]])
                    plt.ion()
                    plt.show()
                    plt.pause(0.001)  
                
                i = i + 1
                    
            
            cnt = cnt + 1
            
            self.stream.write(data)
            data = self.wf.readframes(self.chunk)
    
            

    def close(self):
        """ Graceful shutdown """ 
        self.stream.close()
        self.p.terminate()
        




#Set the path of the audio file
audio_path="py/MusicEmotionMapping/DemoMix.wav"
          

# Usage example for pyaudio
a = AudioFile(audio_path)
a.play()
a.close()