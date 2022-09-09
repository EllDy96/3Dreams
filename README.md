# 3Dreams Artistic VR Experience

## How to use 


### Installing

* Clone the repository and run `npm install`. 
* Run `npm install` also in the **web** directory.
* Install all the depedencies required by the python script **py/MusicEmotionMapping/mer_3dreams.py** using `pip install`

### Executing program

* The application runs on a web server. To set up the server find the IP address of your machine and paste it as suggested by the comments in the files server.js and web/socket.js  (NOTE: the server and all the clients must be connected to the same private network, i.e. the same WiFi, hotspot and so on)
* Run `npm start` to start the server
* Connect using Chrome to `https://x.x.x.x:3000/` where `x.x.x.x` is the IP address (NOTE: is important to use https protocol in order to access the smartphone's sensors for virtual reality mode. Chrome might also notify the connection as unsafe because we created the certificates by ourselves)
* Go into **py/MusicEmotionMapping/mer_3dreams.py**, paste your own file audio path on the variable "audio_path" at the end of the script an then run it. Enjoy a visual immersive rappresentation of your song! 


## Introduction

3Dreams is a New media art application that aims to enhance the music listening experience by giving shapes and colors to the emotional contour conveyed by one music track selected by the user. it's is a VR experience that immerses the user in a dreamlike virtual 3D environment where the music emotions are reflected  in real-time through the changes of the environment.
The song's emotional contour tunes the colours and the swarm behaviour of the virtual 3D world, in which the user is immerse through the use of a VR Headset.
### Music emotion extraction
In order to extract the mood of a musical piece  two high level features are exploited: **Valence**, refered to the level of pleasantness
that a musical event generates, and **Arousal**, defined as the level of 
autonomic activation that a musical event creates.
Starting from a musical piece, a music emotion recognition model extracts these features every 500 ms and after a normalization and avaraging process of the values, they're mapped in to the correspondent color, associated to a certain emotion. If you are interested you can watch a [short demo video](https://drive.google.com/file/d/16BqqSO9iSKyAyB1cbe3xZnKxpoE9ZWbf/view).

**The user can listen to all the music he wants with whoever he wants, but in a different place!**

3Dreams is designed so that the user can feed it with every song he wants, and its emotional trajectory will be extracted and displayed in the virtual world, which can be accessed by many users at the same time.


## System Architecture

 ![alt text](https://github.com/EllDy96/3Dreams/blob/main/images/architecture.png) 

The general structure of the project is divided into two stages: analysis and visualization. Song’s high and low-level features are extracted using python and then sent via OSC to a web server. 
The web server hosts the virtual world, so that the user can access it from any device by connecting using a browser. It also forwards the received OSC messages to the clients via a WebSocket interface, in order to synchronize the world with the evolution of the music.

## Neural Network

![alt text](https://github.com/EllDy96/3Dreams/blob/main/images/NN.png) 


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
A customizable preprocessing chain is implemented exploiting the PedalBoard python library in order to provide to the users the possibility to apply some filters to the original audio track before the Music emotion mapping. For example, reducing the dynamic of a extremely loud and compressed audio file applying a Gain(gain_db=-12) in the pre processing stage, allows the model to extract the Valence and Arousal in a much accurrate way, ensuring the best perfermance.

## Valence and Arousal Russell Plane
### Music emotion recogniction
For the music emotion recognition strategy, we used a conceptualization approach called the Dimensional model: it aims to define emotions based on a continuum descriptors domain.  Emotions cannot be divided into discrete and independent categories, all the affective states arrive from common, overlapping neurophysiological systems. We decided to use the model developed by psychologist James Russell called the circumplex model of emotion. Russell proposes that each emotional state can be modeled as a linear combination of two fundamental neurophysiological systems related to: 
1.	Valence: high level of valence is linked with high pleasantness, on the other hand, a low level of Valence is associated with displeasure.
2.	Arousal or alertness: it expresses the level of emotional activation; it ranges from calm (low) to excited (high).

Joy, for example, is conceptualized as the product of strong activation in the neural systems associated with positive valence or pleasure, together with moderate activation in the neural systems associated with arousal.
Russell creates these 2D planes to describe all the possible human emotions placing the valence in the horizontal axes and the Arousal in the vertical one. By sampling this 2D plane we could retrieve all the human emotions. Rossell also designed a mapping of the Valence-Arousal space, identifying a set of human emotions as specific points of the VA space.  

## Color Mapping
 ![alt text](https://github.com/EllDy96/3Dreams/blob/main/images/ColorMapping1.png) 
The adoption of Russell’s model made it necessary to create an appropriate colors plan that reﬂects the correspondence between points in the VA plane and the color-emotion theory.
We implement our color space by identifying one suitable starting color, one for each of the 4 quadrants, based on the fusion of two color-emotion theories by Ryber’s [5] and by Goethe’s one [4]. 

According to Ryberg’s theory, red represents the most powerful and energetic color, while blue represents emotions with less energy. Goethe’s theory, instead, considers the negative colors as blue and red-blue, and the positive colors as yellow, red-yellow. In the resulting model, we associated the first quadrant with yellow the second with green, the third with blue, and the fourth with red.

The colors that are most powerful, red-like as orange and coral, are placed at the higher arousal zone, while more peaceful colors, like blue and green, end up at the lower arousal zone.
Associating each VA-points with this color plan we can map all the different emotions melting these 4 basic colors together. They are smoothed into one another to avoid sharp boundaries and they get weaker towards the center where arousal and valence are more neutral. 


## Environment
### Framework

### Lights
![alt text](https://github.com/EllDy96/3Dreams/blob/main/images/secondary.png) 


### Terrain
![alt text](https://github.com/EllDy96/3Dreams/blob/main/images/Animation%20terrain.gif) 


## Boids System

### Obstacles
![alt text](https://github.com/EllDy96/3Dreams/blob/main/images/Obstacles.gif) 


### Boids Main Behaviour mapping

We can model the Boids swarm behavior tuning fours parameters linked to the norm of 4 force vectors applied to each boid:  
- **Alignment**: the steering force inducing to follow the same direction of the neighbor’s boids.
- **Separation**: repulsion force to prevent collision and to define how much space is in between. 
- **Cohesion**: A force pointing toward the center of the neighbors, allows the creation of groups of swarms.
- **Speed**: the speed force.

We update these parameters to make the swarm reflects the emotional contour of the playback track in real-time using OSC messages. 
To design a meaningful mapping, we want to establish some dependency on the current VA-space’s point where the song is, to have an overall effective swarm behavior.

### VA-Space clustering
![alt text](https://github.com/EllDy96/3Dreams/blob/main/images/VA-Clustering.png) 

We split the VA-space into 5 clusters each associated with a specific emotion, to each cluster we designed a specific boids behavior that best describes the respecting emotion, by fixing 2 or more of the 4 Boid parameters. Inside each cluster, we introduce some novelty situations by tuning in real-time the remaining Boid’s parameters with specific instantaneous low-level features.


 

 
 -	**Happy cluster**, associated with the yellow parts, has maximum alignment and cohesion to create one single swarm that fluctuates around in a harmonic dance. 
 
 ![alt text](https://github.com/EllDy96/3Dreams/blob/main/images/Animation4.gif) 
 
  -	**Tension cluster**, associated with the orange part, has maximum separation and the maximum speed that does not generate any swarm, all the boids fluctuate randomly around in a nervous way.
 
 ![alt text](https://github.com/EllDy96/3Dreams/blob/main/images/Animation3.gif) 
 
 - **Fear** cluster, associated with the red part, has maximum alignment but minimum cohesion, in this way each Boid tries to follow the neighbour’s direction but without creating any swarm for the low 
 ![alt text](https://github.com/EllDy96/3Dreams/blob/main/images/Animation7.gif) 
 
 - **Sad cluster**, associated with the blue part, has maximum cohesion, minimum separation, and alignment. In this area, the boids barely move, they are split into little depressed still groups that do not move for the low alignment and the high cohesion. 

 ![alt text](https://github.com/EllDy96/3Dreams/blob/main/images/Animation2.gif) 
 
 - **The peaceful cluster**, associated with the green part, has maximum cohesion and minimum separation to create multiple compact swarms that fluctuate in a chilly way.
 
 ![alt text](https://github.com/EllDy96/3Dreams/blob/main/images/PeacefulBoids.gif)


### Low-level features mapping
In order to make more dynamic and creative the boid's behaviour just described we 
chose to exploit some low level features extracted from the audio.
These features are mapped to some of the boid's behaviour parameters and modify them
in a certain range.
In particular we focused on:
- **SPECTRAL FLUX**, that affects the separation in the boid system of the *Happy Area*
- **ENERGY**, it modifies the speed of the *Peacful* and Happy *Area* 
- **SPECTRAL-ENTROPY**, that influences the alignment value of the *Tension Area* and 
the speed of the *Sad Area*
- **ZERO-CROSSING-RATE** , that modifies the cohesion value of the *Tension Area*


## Authors

Francesco Boarino

Davide Lionetti

Giovanni Affatato

Alessandro Molteni



## References

* [Festivalle21](https://github.com/ammlyy/festivalle21)
* [MedievalDataset](http://www.multimediaeval.org/datasets/)
* [boids-webworkers](https://github.com/ercang/boids-js)
* M. Schindler and J. W. Goethe, Goethe’s theory of colour. London: New Knowledge, 1970.​
* J. Itten, The Art of Color: The Subjective Experience and Objective Rationale of Color. Van Nostrand Reinhold Company, 1974.
