import sys
import wave
import pyaudio

# PyAudio object variable
pa = pyaudio.PyAudio()

# Size of each read-in chunk
CHUNK = 1
# Sample width of the live recording
WIDTH = 2
# Amount of channels of the live recording
CHANNELS = 2
# Sample rate in Hz of the live recording
SAMPLE_RATE = 44100


def main():
    # Mode the program was run in
    mode = sys.argv[1]

    # Execute the chosen mode
    if mode == '--file' or mode == '-f':
        filemode()
    elif mode == '--live' or mode == '-l':
        livemode()
    else:
        print('Please either choose file-mode or live-mode')


def filemode():
    # Give some feedback
    print('Now cancelling the file')

    # Read in the given file
    (waveform, stream) = readin(sys.argv[2])

    # Read a first chunk and continue to do so for as long as there is a stream to read in
    original = waveform.readframes(CHUNK)
    while original != '':
        # Invert the original audio
        inverted = invert(original)

        # Play back both audios
        stream.write(original)
        stream.write(inverted)

        original = waveform.readframes(CHUNK)

    # Stop the stream after there is no more data to read and terminate PyAudio
    stream.stop_stream()
    stream.close()
    pa.terminate()


def livemode():
    # Start live recording
    print('Now cancelling live')

    # Create a new PyAudio object using the preset constants
    stream = pa.open(
        format=pa.get_format_from_width(WIDTH),
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        frames_per_buffer=CHUNK,
        input=True,
        output=True
    )

    # Grab a chunk of data in iterations according to the preset constants
    for i in range(0, int(SAMPLE_RATE / CHUNK * sys.maxunicode)):
        # Read in a chunk of live audio on each iteration
        original = stream.read(CHUNK)

        # Invert the original audio
        inverted = invert(original)

        # Play back the inverted audio
        stream.write(inverted, CHUNK)


def readin(file):
    """
    Reads in the given wave file and returns a new PyAudio stream object from it.

    :param file: The path to the file to read in
    :return (waveform, stream): (The actual audio data as a waveform, the PyAudio object for said data)
    """

    # Open the waveform from the command argument
    waveform = wave.open(file, 'r')

    # Load PyAudio and create a useable waveform object
    stream = pa.open(
        format=pa.get_format_from_width(waveform.getsampwidth()),
        channels=waveform.getnchannels(),
        rate=waveform.getframerate(),
        output=True
    )

    return waveform, stream


def invert(data):
    """
    Inverts the byte data it received utilizing an XOR operation.

    :param data: A chunk of byte data
    :return inverted: The same size of chunked data inverted bitwise
    """

    # Convert the bytestring into an integer
    intwave = int.from_bytes(data, byteorder='big')
    # Invert the integer
    intwave ^= 2147483647
    # Convert the integer back into a bytestring
    inverted = intwave.to_bytes(4, byteorder='big')
    # Return the inverted audio data
    return inverted


main()
