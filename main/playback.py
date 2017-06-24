import pyaudio
import wave
import sys


def invert():
    # Size of each read in chunk
    chunk = 1

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
        # Convert the bytestring into an integer
        intwave = int.from_bytes(data, byteorder='big')
        # Invert the integer
        intwave ^= 2147483647
        # Convert the integer back into a bytestring
        inverted = intwave.to_bytes(4, byteorder='big')

        # Play back the original audio data
        stream.write(data)
        # Play back the inverted audio data
        stream.write(inverted)
        # Grab another chunk of data for the next iteration
        data = waveform.readframes(chunk)

    # Stop the stream after there is no more data to read and terminate PyAudio
    stream.stop_stream()
    stream.close()
    pa.terminate()
