import sys
import math
import wave
import struct
import pyaudio
import matplotlib.pyplot as plt

# PyAudio object variable
pa = pyaudio.PyAudio()

# Size of each read-in chunk
CHUNK = 1
# Amount of channels of the live recording
CHANNELS = 2
# Sample width of the live recording
WIDTH = 2
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
    print('Now noise-cancelling the file')

    # Read in the given file
    (waveform, stream) = readin(sys.argv[2])

    # Collecting the volume levels in decibels in a list
    decibel_levels = []

    # Counting the iterations of the while-loop
    iteration = 0

    # Read a first chunk and continue to do so for as long as there is a stream to read in
    original = waveform.readframes(CHUNK)
    while original != b'':
        # Invert the original audio
        inverted = invert(original)

        # Play back both audios
        stream.write(original)
        stream.write(inverted)

        # On every 1000th iteration append the difference between the level of the source audio and the inverted one
        if iteration % 1000 == 0:
            decibel_levels.append(calculate_decibel(original) - calculate_decibel(inverted))

        # Read in the next chunk of data
        original = waveform.readframes(CHUNK)

        # Add up one to the iterations
        iteration += 1

    # Outputting feedback regarding the end of the file
    print('Finished noise-cancelling the file')

    # Stop the stream after there is no more data to read
    stream.stop_stream()
    stream.close()

    # Plot the results
    plot_results(decibel_levels)

    # Terminate PyAudio
    pa.terminate()


def livemode():
    # Start live recording
    print('Now noise-cancelling live')

    # Create a new PyAudio object using the preset constants
    stream = pa.open(
        format=pa.get_format_from_width(WIDTH),
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        frames_per_buffer=CHUNK,
        input=True,
        output=True
    )

    # Collecting the volume levels in decibels in a list
    decibel_levels = []

    # Grab a chunk of data in iterations according to the preset constants
    try:
        for i in range(0, int(SAMPLE_RATE / CHUNK * sys.maxunicode)):
            # Read in a chunk of live audio on each iteration
            original = stream.read(CHUNK)

            # Invert the original audio
            inverted = invert(original)

            # Play back the inverted audio
            stream.write(inverted, CHUNK)

            # On every 1000th iteration append the difference between the level of the source audio and the inverted one
            if i % 1000 == 0:
                decibel_levels.append(calculate_decibel(original) - calculate_decibel(inverted))
    except (KeyboardInterrupt, SystemExit):
        plot_results(decibel_levels)


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


def calculate_decibel(data):
    """
    Calculates the volume level in decibel of the given data

    :param data: A bytestring used to calculate the decibel level
    :return db: The calculated volume level in decibel
    """

    count = len(data) / 2
    form = "%dh" % count
    shorts = struct.unpack(form, data)
    sum_squares = 0.0
    for sample in shorts:
        n = sample * (1.0/32768)
        sum_squares += n * n
    rms = math.sqrt(sum_squares / count) + 0.0001
    db = 20 * math.log10(rms)
    return db


def plot_results(data):
    """
    Plots the list it receives and cuts off the first ten entries to circumvent the plotting of initial silence

    :param data: A list of data to be plotted
    """

    plt.plot(data[10:])
    plt.xlabel('Time (every 1000th byte)')
    plt.ylabel('Volume level (in dB)')
    plt.show()


main()
