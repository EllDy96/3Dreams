import pyaudio
import wave

import librosa
import soundfile as sf
#from pedalboard import Pedalboard, Compressor 
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
from pyAudioAnalysis import ShortTermFeatures


#Set OSC port
ip = "127.0.0.1"
port = 57121

client = udp_client.SimpleUDPClient(ip, port)



class AudioFile:
    chunk = 22050
    SR = 44100
    # choose the number of 500 ms audio cuncks on which apply the avarage
    avg_blocks = 6
    TESTING= False #boolean value for plotting colours in real time (used fo testing)
    MAX_VAL = 5.0
    MAX_SPEED = 10.0
    

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
        serene_pos = [0.4, -0.5]#lightgreen
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
        
        
        """ ---------- Pre Processing ---------- """
        '''
        # Make a Pedalboard object, containing multiple plugins:
        board = Pedalboard([Compressor(threshold_db=-15, ratio=4)])
        
        
        # change compressor threshold 
        board[0].threshold_db = -30

        # Pedalboard objects behave like lists, which I can append plugins:
        board.append(Gain(gain_db=10))
        board.append(Limiter())
        
        # Run the audio through this pedalboard
        processed_audio= board(audio, nativeSampleRate)

        #resampling to 44.1 kHz
        audio = librosa.resample(audio, nativeSampleRate, self.SR)
        processed_audio = librosa.resample(processed_audio, nativeSampleRate, self.SR)
        # Write the audios as a wav file:
        sf.write(audio_path, audio, self.SR)
        sf.write(processedAudio_path, processed_audio, self.SR)
        
        print("Sampling rate: ", librosa.get_samplerate(file))
        
        #read the processed audio 
        #processed_audio, self.SR = sf.read(processedAudio_path, samplerate=44100)
        
        '''
        """ ---------- VA Values Initialization and Computation ---------- """
        
        #Load the model

        pred_model = load_model("py/MusicEmotionMapping/best_model.hdf5", compile=False)
    
        
        #Stream the data 

        stream = librosa.stream(file,
                        block_length=1,
                        frame_length=self.chunk,
                        hop_length=self.chunk)

        self.numChunks = 1

        #Valence-arousal vector
        valence_avg = 0
        arousal_avg = 0
        
        self.va = []
        
        #BPM Vector
        self.bpm = []
        tempo = 0
        
        #Low-level Features Vectors
        self.energy = []
        energy_avg = 0
        
        self.entropy = []
        entropy_avg = 0
        
        self.zcr = []
        zcr_avg = 0
        
        self.flux = []
        flux_avg = 0
        

        #Predict the VA values for each chunk
        
        for y in stream:

            buff = np.array(np.zeros(22050))
            buff[0:y.shape[0]] = y[:]
            buff = np.expand_dims(buff, axis=0)  
            
            #bpm computation
            onset_env = librosa.onset.onset_strength(y, sr=self.SR)
            tempo += librosa.beat.tempo(onset_envelope=onset_env, sr=self.SR)
            
            #low-level features computation (F[2-8] are relevant fo us)
            F, f_names = ShortTermFeatures.feature_extraction(y, self.SR, 0.050*self.SR, 0.025*self.SR)
            
            energy_avg += sum(F[1]) / F.shape[1] 
            entropy_avg += sum(F[2]) / F.shape[1]
            zcr_avg += sum(F[0]) / F.shape[1]
            flux_avg += sum(F[6]) / F.shape[1]
            
            """
            print(F.shape[1])
            print(F.shape[1])
            print(sum(F[2]))
            print(f_names[2])
            """

            #Valence and Arousal computation
            valence_avg += (pred_model.predict(buff)[0])[1]
            arousal_avg += (pred_model.predict(buff)[0])[0]
            
            #Store the VA avarage values  
            if(self.numChunks%self.avg_blocks == 0):

                #Valence and Arousal 
                valence_avg = valence_avg/self.avg_blocks
                arousal_avg = arousal_avg/self.avg_blocks

                self.va.append([arousal_avg, valence_avg])
                    
                valence_avg = 0
                arousal_avg = 0
                
                #BPM Computation
                tempo = (tempo/2)/self.avg_blocks
                self.bpm.append(tempo)
                tempo = 0
                
                #Energy Computation
                energy_avg = energy_avg/self.avg_blocks
                self.energy.append(energy_avg*10)
                energy_avg = 0
                
                #Entropy Computation
                entropy_avg = entropy_avg/self.avg_blocks
                self.entropy.append(entropy_avg)
                entropy_avg = 0
                
                #ZCR Computation
                zcr_avg = zcr_avg/self.avg_blocks
                self.zcr.append(zcr_avg*10)
                zcr_avg = 0
                
                #Spectral Flux Computation
                flux_avg = flux_avg/self.avg_blocks
                self.flux.append(flux_avg)
                flux_avg = 0
        
    
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
            
            
            
        """ ---------- Boids behaviour mapping ---------- """  
        
        self.alignment = []
        self.cohesion = []
        self.separation = []
        self.speed = []
        
        for i in range(self.numAvgValues):
            
            arousal = self.va[i][0]
            valence = self.va[i][1]
            
            if (arousal>=0):
                if(valence>0.2):
                    #HAPPY area
                    '''FIXED'''
                    self.alignment.append(self.MAX_VAL)
                    self.cohesion.append(self.MAX_VAL)
                    '''CUSTOM'''
                    self.separation.append(self.MAX_VAL/2) #spectral(ent o flux)
                    #self.separation.append(self.MAX_VAL/2 + (self.flux[i]*100 - 0.6)) 
                    self.speed.append((self.MAX_SPEED*3)/4) #bpm/energy
                    #self.speed.append(((self.MAX_SPEED*3)/4)  + (self.energy[i]*10) - 13)
                    
                else:
                    if((valence<0.2) & (valence>-0.2)):
                        #TENSION area
                        '''CUSTOM'''
                        self.alignment.append(0.0) # 1 / energy-ent
                        #?????????
                        self.cohesion.append(self.MAX_VAL/2) #1/zero-crossing o 1/spectral flux
                        #self.cohesion.append(self.MAX_VAL/2 + ((0.34 - self.zcr[i])*10))
                        '''FIXED'''
                        self.separation.append(self.MAX_VAL)
                        self.speed.append(self.MAX_SPEED)   
                    
                    else:
                        #FEAR area
                        '''CUSTOM'''
                        self.alignment.append(5.0) # 1 / energy-ent
                        #?????????
                        self.cohesion.append(0.0) #1/zero-crossing o 1/spectral flux
                        #????
                        '''FIXED'''
                        self.separation.append(self.MAX_VAL)
                        self.speed.append(self.MAX_SPEED)                       
                    
                        '''
                        FEAR - DEPRESSED
                        FIXED 
                        low cohesion
                        high separation
                        CUSTOM
                        speed -> en-ent
                        align -> 1 / zero cross
                        '''
            else:
                if(valence<=0):
                    #SAD area
                    '''FIXED'''
                    self.cohesion.append(self.MAX_VAL)
                    self.separation.append(0.0)
                    '''CUSTOM'''
                    self.alignment.append(0.0) #1/ener-ent
                    self.speed.append(self.MAX_SPEED/2) #spectral-ent (da provare)
                    #self.speed.append(((self.MAX_SPEED)/2)  + ((self.energy[i]-1.0)*10))
                    
                else:
                    #peace area
                    '''FIXED'''
                    self.cohesion.append(self.MAX_VAL)
                    self.separation.append(0.0)
                    '''CUSTOM'''
                    self.alignment.append(self.MAX_VAL/3)
                    #self.alignment.append((self.MAX_VAL/3)  + ((self.flux[i]*100)-0.75)*2)
                    self.speed.append(self.MAX_SPEED/2) 
                    #self.speed.append(((self.MAX_SPEED)/2)  + ((self.energy[i]-0.65)*10))
                
                    

        
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
                print("BPM num  ", i, " : ", self.bpm[i])
                print("Energy num  ", i, " : ", self.energy[i])
                print("Entropy num  ", i, " : ", self.entropy[i])
                print("Zero-Crossing Rate num  ", i, " : ", self.zcr[i])
                print("Spectral Flux num  ", i, " : ", self.flux[i])
                #print("Corresponding RGB color : ", self.colorMapped[i], "\n\n")
                print("Alignment   ", i, " : ", self.alignment[i])
                print("Cohesion   ", i, " : ", self.cohesion[i])
                print("Separation   ", i, " : ", self.separation[i])
                print("Speed : ", self.speed[i], "\n\n")
                
                
                #sending the OSC messagges
               
                client.send_message("/RGB", self.colorMapped[i])
                
                #low-level features messages
                client.send_message("/ENERGY", self.energy[i])
                client.send_message("/ENTROPY", self.entropy[i])
                
                #boids behaviour messages
                client.send_message("/ALIGNMENT", self.alignment[i])
                client.send_message("/COHESION", self.cohesion[i])
                client.send_message("/SEPARATION", self.separation[i])
                client.send_message("/SPEED", self.speed[i])              
              
               

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
processedAudio_path="py/MusicEmotionMapping/processedMix.wav"        

# Usage example
a = AudioFile(audio_path)
a.play()
a.close()

'''
#Testing the processed Mix 
processedMix= AudioFile(processedAudio_path)
processedMix.play()
processedMix.close()

'''
