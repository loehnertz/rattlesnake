import pyaudio
import wave
import sys


def playback():
    # Size of each read in chunk
    chunk = 1024

    # Open the waveform from the command argument
    waveform = wave.open(sys.argv[1], 'r')

    # Load PyAudio and create a useable waveform object
    pa = pyaudio.PyAudio()
    stream = pa.open(format=pa.get_format_from_width(waveform.getsampwidth()),
                     channels=waveform.getnchannels(),
                     rate=waveform.getframerate(),
                     output=True)

    # Read a first chunk and continue to do so for as long as there is a stream to read in
    data = waveform.readframes(chunk)
    while data != '':
        # Write the read-in data into the PyAudio object to play it back
        stream.write(data)
        data = waveform.readframes(chunk)

    # Stop the stream after there is no more data to read and terminate PyAudio
    stream.stop_stream()
    stream.close()
    pa.terminate()

playback()
