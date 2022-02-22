# 3Dreams Experince
# 3Dreams


## Introduction

The purpose of the appication is to enhance the music listening experience by immersing the user in a dreamlike environment where music emotion is not only conveyed through sound, but also through sight.
The song's mood mdifies the colours and shapes of the virtual 3D world in which the user is immerse through the use of a VR Headset.
In order to extract the mood of a musical piece  two high level features are exploited: **Valence**, refered to the level of pleasantness
that a musical event generates, and **Arousal**, defined as the level of 
autonomic activation that a musical event creates.
Starting from a musical piece, a music emotion recognition model extracts these features every 500 ms and after a normalization and avaraging process of the values, they're mapped in to the correspondent color, associated to a certain emotion.

##### The user can listen to all the music you want with whoever you want, but in a different place!

3Dreams is designed so that the user can feed it with every song he wants, and its emotional trajectory will be extracted and displayed in the virtual world, which can be accessed by many users at the same time.

## Neural Network

### Training
The training is based on the MediaEval Dataset, that contains the arousal and valence values of 1000 songs of different genres.

### Layers Structure
The architecture involves two convolutional layers with different kernel size: one is dedicated to observe the phase variatons within a frame, and the other one (with bigger kernel size) to capture patterns and periodic behaviour.
The combination of these two layers go through a Time distributed fully connected layer,
that combined with a bidirectional GRU learn the temporal information. 
The advantage of Bidirectional GRU is its ability to propagate information 
both in future and past direction (optimal for a musical context).
At the end a Dense Layer is placed to match the desire shape of the output.

## Audio Pre-Processing
A customizable preprocessing chain is implemented exploiting the PedalBoard python library in order to provide to the users, depending on the input audio, to make more robust the model and to tune the value ranges of the low level features.

## Valence and Arousal Russell Plane
