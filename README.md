# rattlesnake
A python application that does noise cancellation


## Motive
During the spring semester of 2017 I had to do a project for my studies at university.
The topic was to think of experiments regarding audio, sound, sonic waves etc. that we could prepare for fellow students
to experience during future lectures with the goal of imparting acoustics to the students.
During this project I came up with the idea of demonstrating *Active Noise Cancellation* with a custom script.


## Explanation
This python tool can do *Active Noise Cancellation (ANC)* respectively *Active Noise Reduction (ANR)*.
It reads in a stream of audio, either live or from a pre-recorded file and calculates an inverted signal for every byte
of the data stream utilizing an XOR operation.    
After the execution is finished the program calculates a median of the difference levels which reflects
the results of the algorithm. It also plots a graph with the results and displays it afterwards.    
    
*More details soon to follow*


## Installation
Clone the repo and install the requirements via pip:    
`pip install -r requirements.txt`


## Usage
Run the python script from your terminal and specify the mode you want to use:    
`python3 start.py --mode --result nth_iteration filename.wav`    

Every argument type only accepts one at a time.

Argument        | Description
--------        | -----------
--live (-l)     | This is the 'live-mode' which records audio and inverts it on-the-fly. (--mode)
--file (-f)     | This is the more basic 'file-mode' which expects a wave audio file (.wav) as the third argument. It then plays back the original file as well as the inverted audio to effectively cancel both out. (--mode)
--playback (-p) | This is the 'playback-mode' that does exactly what one would expect. It can be used to test an existing file. (--mode)
--decibel (-db) | This argument will cause the 'decibels' to be plotted at the end. (--result)
--waves (-wv)   | This argument will cause the 'waves' to be plotted at the end. (--result)
nth_iteration   | This argument is required and needs to be a number. It specifies on which nth iterations data is saved for calculating and plotting the results. The lower the value, the more precise the results.


## License
[MIT](LICENSE)
