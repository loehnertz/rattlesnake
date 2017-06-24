import sys
import wave
import pyaudio

# PyAudio object
pa = pyaudio.PyAudio()
# Size of each read in chunk
chunk = 1


def main():
    (waveform, stream) = readin(sys.argv[1])

    # Read a first chunk and continue to do so for as long as there is a stream to read in
    original = waveform.readframes(chunk)
    while original != '':
        inverted = invert(original)

        playback(stream, original)
        playback(stream, inverted)

        original = waveform.readframes(chunk)

    # Stop the stream after there is no more data to read and terminate PyAudio
    stream.stop_stream()
    stream.close()
    pa.terminate()


def readin(file):
    # Open the waveform from the command argument
    waveform = wave.open(file, 'r')

    # Load PyAudio and create a useable waveform object
    stream = pa.open(format=pa.get_format_from_width(waveform.getsampwidth()),
                     channels=waveform.getnchannels(),
                     rate=waveform.getframerate(),
                     output=True)

    return waveform, stream


def invert(data):
    # Convert the bytestring into an integer
    intwave = int.from_bytes(data, byteorder='big')
    # Invert the integer
    intwave ^= 2147483647
    # Convert the integer back into a bytestring
    inverted = intwave.to_bytes(4, byteorder='big')
    # Return the inverted audio data
    return inverted


def playback(stream, data):
    # Play back the audio data
    stream.write(data)


main()
