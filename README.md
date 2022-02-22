# 3Dreams Artistic VR Experience



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
## Color Mapping


## Environment
### Framework

## Boids Behaviour  

### Main Behaviour

The boids behavior  is regulated by main parameters each linked to the norm of a specific force vector applied to each: 
**Alignment**: the steering force inducing to follow the same direction of the neighbor’s boids.
**Separation**: repulsion force to prevent collision and to define how much space is in between. 
**Cohesion**: A force pointing toward the center of the neighbors, allows the creation of groups of swarms.
**Speed**: the speed force.

### Low-level features mapping
In order to make more dynamic and creative the boid's behaviour just described we 
chose to exploit some low level features extracted from the audio.
These features are mapped to some of the boid's behaviour parameters and modify them
in a certain range.
In particular we focused on:
- **SPECTRAL FLUX**, that affects the separation in the boid system of the *Happy Area*
- **ENERGY**, mapped to the speed of the *Peacful* and Happy *Area*
- **SPECTRAL-ENTROPY**, that influences the alignment value of the *Tension Area* and 
the speed of the *Sad Area*
- **ZERO-CROSSING-RATE** , that modifies the cohesion value of the *Tension Area*








##How to use 

### Dependencies

* ............

### Installing

* ................

### Executing program

* How to run the program

```
code blocks for commands
```

## Authors

Francesco Boarino
Davide Lionetti
Giovanni Affatato
Alessandro Molteni



## References

Inspiration, code snippets, etc.
* [Festivalle21](https://github.com/ammlyy/festivalle21)
* [MedievalDataset](http://www.multimediaeval.org/datasets/)
* [boids-webworkers](????)

* M. Schindler and J. W. Goethe, Goethe’s theory of colour. London: New Knowledge, 1970.​
* J. Itten, The Art of Color: The Subjective Experience and Objective Rationale of Color. Van Nostrand Reinhold Company, 1974.
