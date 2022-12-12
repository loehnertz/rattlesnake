# rattlesnake

A python application that does noise cancellation in thoery

## Motive

During the spring semester of 2017 I had to do a project for my studies at university.
The topic was to think of experiments regarding audio, sound, sonic waves etc. that we could prepare for fellow students
to experience during future lectures with the goal of imparting acoustics to the students.
During this project I came up with the idea of demonstrating _Active Noise Cancellation_ with a custom script.

## Explanation

This python tool can do _Active Noise Cancellation (ANC)_ respectively _Active Noise Reduction (ANR)_.
It reads in a stream of audio, either live or from a pre-recorded file and calculates an inverted signal for every byte
of the data stream utilizing an XOR operation.  
After the execution is finished the program calculates a median of the difference levels which reflects
the results of the algorithm. It also plots a graph with the results and displays it afterwards.

_More details soon to follow_

## Installation

Clone the repo and install the requirements via pip:

```bash
pip install -r requirements.txt
```

or

```bash
poetry install
```

## Usage

```
poetry run rattlesnake

or

poetry run rattlesnake_callback_version
```

## License

[MIT](LICENSE)
