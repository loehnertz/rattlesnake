# rattlesnake
A python application that does noise cancellation


## Motive
*Following soon*


## Explanation
This python tool can do *Active Noise Cancellation (ANC)* respectively *Active Noise Reduction (ANR)*.
It reads in a stream of audio, either live or from a pre-recorded file and calculates an inverted signal for every bit
of the data stream utilizing an XOR operation.    
*More details soon to follow*


## Installation
Clone the repo and install the requirements via pip:    
`pip install -r requirements.txt`


## Usage
Run the python script from your terminal and specify the mode you want to use:    
`python3 start.py --mode`

Argument     | Description
--------     | -----------
--live (-l)  | This is the 'live-mode' which records audio and inverts it on-the-fly.
--file (-f)  | This is the more basic 'file-mode' which expects a wave audio file (.wav) as a second argument. It then plays back the original file as well as the inverted audio to effectively cancel it out.

Both modes are self-adjusting themselves during execution.


## License
[MIT](LICENSE)
