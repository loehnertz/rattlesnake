import sys
import math
import wave
import struct
import curses
import pyaudio
import numpy as np
import matplotlib.pyplot as plt

# 'curses' configuration
stdscr = curses.initscr()
stdscr.nodelay(True)
curses.noecho()
curses.cbreak()

# PyAudio object variable
pa = pyaudio.PyAudio()

# The mode the user chose with a script argument
MODE = sys.argv[1]
# Size of each read-in chunk
CHUNK = 1
# Amount of channels of the live recording
CHANNELS = 2
# Sample width of the live recording
WIDTH = 2
# Sample rate in Hz of the live recording
SAMPLE_RATE = 44100
# Set how often data for the result will be saved (every nth CHUNK)
if MODE != '-p' and MODE != '--playback':
    try:
        NTH_ITERATION = int(sys.argv[3])
    except (ValueError, IndexError):
        print('The second argument has to be a number')
        sys.exit()


def main():
    # Execute the chosen mode
    if MODE == '--file' or MODE == '-f':
        file_mode()
    elif MODE == '--live' or MODE == '-l':
        live_mode()
    elif MODE == '--playback' or MODE == '-p':
        playback_mode()
    else:
        print('Please either choose file-mode, live-mode or playback-mode with the first argument')


def file_mode():
    # Read in the given file
    (waveform, stream) = readin(sys.argv[4])

    # Give some feedback
    stdscr.addstr('Now noise-cancelling the file')

    # Collecting the volume levels in decibels in a list
    decibel_levels = []

    # Collecting the waves into lists
    total_original = []
    total_inverted = []
    total_difference = []

    # Counting the iterations of the while-loop
    iteration = 0

    # Determines the ratio of the mix
    ratio = 1.0

    # Determines if the noise-cancellation is active
    active = True

    # Read a first chunk and continue to do so for as long as there is a stream to read in
    original = waveform.readframes(CHUNK)
    while original != b'':
        try:
            # Capture if a key was pressed
            pressed_key = stdscr.getch()

            # If the 'o' key was pressed toggle the 'active' variable
            if pressed_key == 111:
                active = not active
                # While the noise-cancellation is not activated the ratio should be 100% towards the orginial audio
                if not active:
                    ratio = 2.0
                else:
                    ratio = 1.0
            # Increase the ratio of the mix
            elif pressed_key == 43:
                ratio += 0.01
            # Decrease the ratio of the mix
            elif pressed_key == 45:
                ratio -= 0.01
            # If the 'x' key was pressed abort the loop
            elif pressed_key == 120:
                break

            # Invert the original audio
            inverted = invert(original)

            # Play back a mixed audio stream of both, original source and the inverted one
            if active:
                mix = mix_samples(original, inverted, ratio)
                stream.write(mix)
            # In case the noise-cancellation is not turned off temporarily, only play the orignial audio source
            else:
                stream.write(original)

            # On every nth iteration append the difference between the level of the source audio and the inverted one
            if iteration % NTH_ITERATION == 0:
                # Clear the terminal before outputting the new value
                stdscr.clear()
                # Calculate the difference of the source and the inverted audio
                difference = calculate_difference(original, inverted)
                # Print the current difference
                stdscr.addstr('Difference (in dB): {}\n'.format(difference))
                # Append the difference to the list used for the plot
                decibel_levels.append(difference)
                # Calculate the waves for the graph
                int_original, int_inverted, int_difference = calculate_wave(original, inverted, ratio)
                total_original.append(int_original)
                total_inverted.append(int_inverted)
                total_difference.append(int_difference)

            # Read in the next chunk of data
            original = waveform.readframes(CHUNK)

            # Add up one to the iterations
            iteration += 1

        except (KeyboardInterrupt, SystemExit):
            break

    # Stop the stream after there is no more data to read
    stream.stop_stream()
    stream.close()

    # Outputting feedback regarding the end of the file
    print('Finished noise-cancelling the file')

    # Plot the results
    if sys.argv[2] == '--decibel' or sys.argv[2] == '-db':
        plot_results(decibel_levels, NTH_ITERATION)
    elif sys.argv[2] == '--waves' or sys.argv[2] == '-wv':
        plot_wave_results(total_original, total_inverted, total_difference, NTH_ITERATION)

    # Revert the changes from 'curses'
    curses.endwin()

    # Terminate PyAudio as well as the program
    pa.terminate()
    sys.exit()


def live_mode():
    # Start live recording
    stdscr.addstr('Now noise-cancelling live')

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

    # Collecting the waves into lists
    total_original = []
    total_inverted = []
    total_difference = []

    # Determines if the noise-cancellation is active
    active = True

    # Grab a chunk of data in iterations according to the preset constants
    try:
        for i in range(0, int(SAMPLE_RATE / CHUNK * sys.maxunicode)):
            # Capture if a key was pressed
            pressed_key = stdscr.getch()

            # If the 'o' key was pressed toggle the 'active' variable
            if pressed_key == 111:
                active = not active

            # If the 'x' key was pressed abort the loop
            if pressed_key == 120:
                break

            # Read in a chunk of live audio on each iteration
            original = stream.read(CHUNK)

            # Invert the original audio
            inverted = invert(original)

            # Play back the inverted audio
            stream.write(inverted, CHUNK)

            # On every nth iteration append the difference between the level of the source audio and the inverted one
            if i % NTH_ITERATION == 0:
                # Clear the terminal before outputting the new value
                stdscr.clear()
                # Calculate the difference of the source and the inverted audio
                difference = calculate_difference(original, inverted)
                # Print the current difference
                stdscr.addstr('Difference (in dB): {}'.format(difference))
                # Append the difference to the list used for the plot
                decibel_levels.append(difference)
                # Calculate the waves for the graph
                int_original, int_inverted, int_difference = calculate_wave(original, inverted)
                total_original.append(int_original)
                total_inverted.append(int_inverted)
                total_difference.append(int_difference)

    except (KeyboardInterrupt, SystemExit):
        # Outputting feedback regarding the end of the file
        print('Finished noise-cancelling the file')

        # Plot the results
        if sys.argv[2] == '--decibel' or sys.argv[2] == '-db':
            plot_results(decibel_levels, NTH_ITERATION)
        elif sys.argv[2] == '--waves' or sys.argv[2] == '-wv':
            plot_wave_results(total_original, total_inverted, total_difference, NTH_ITERATION)

        # Revert the changes from 'curses'
        curses.endwin()

        # Terminate the program
        stream.stop_stream()
        stream.close()
        pa.terminate()
        sys.exit()


def playback_mode():
    # Read in the given file
    (waveform, stream) = readin(sys.argv[2])

    # Give some feedback
    print('Now playing back the file')

    # Read a first chunk and continue to do so for as long as there is a stream to read in
    original = waveform.readframes(CHUNK)
    while original != b'':
        try:
            # Play back the audio
            stream.write(original)

            # Read in the next chunk of data
            original = waveform.readframes(CHUNK)
        except (KeyboardInterrupt, SystemExit):
            break

    # Stop the stream after there is no more data to read
    stream.stop_stream()
    stream.close()

    # Outputting feedback regarding the end of the file
    print('Finished playing back the file')

    # Terminate PyAudio as well as the program
    pa.terminate()
    sys.exit()


def readin(file):
    """
    Reads in the given wave file and returns a new PyAudio stream object from it.

    :param file: The path to the file to read in
    :return (waveform, stream): (The actual audio data as a waveform, the PyAudio object for said data)
    """

    # Open the waveform from the command argument
    try:
        waveform = wave.open(file, 'r')
    except wave.Error:
        print('The program can only process wave audio files (.wav)')
        sys.exit()
    except FileNotFoundError:
        print('The chosen file does not exist')
        sys.exit()

    # Load PyAudio and create a useable waveform object
    stream = pa.open(
        format=pa.get_format_from_width(waveform.getsampwidth()),
        channels=waveform.getnchannels(),
        rate=waveform.getframerate(),
        output=True
    )

    # Return the waveform as well as the generated PyAudio stream object
    return waveform, stream


def invert(data):
    """
    Inverts the byte data it received utilizing an XOR operation.

    :param data: A chunk of byte data
    :return inverted: The same size of chunked data inverted bitwise
    """

    # Convert the bytestring into an integer
    intwave = np.fromstring(data, np.int32)
    # Invert the integer
    intwave = np.invert(intwave)
    # Convert the integer back into a bytestring
    inverted = np.frombuffer(intwave, np.byte)
    # Return the inverted audio data
    return inverted


def mix_samples(sample_1, sample_2, ratio):
    """
    Mixes two samples into each other

    :param sample_1: A bytestring containing the first audio source
    :param sample_2: A bytestring containing the second audio source
    :param ratio: A float which determines the mix-ratio of the two samples (the higher, the louder the first sample)
    :return mix: A bytestring containing the two samples mixed together
    """

    # Calculate the actual ratios based on the float the function received
    (ratio_1, ratio_2) = get_ratios(ratio)
    # Convert the two samples to integers
    intwave_sample_1 = np.fromstring(sample_1, np.int16)
    intwave_sample_2 = np.fromstring(sample_2, np.int16)
    # Mix the two samples together based on the calculated ratios
    intwave_mix = (intwave_sample_1 * ratio_1 + intwave_sample_2 * ratio_2).astype(np.int16)
    # Convert the new mix back to a playable bytestring
    mix = np.frombuffer(intwave_mix, np.byte)
    return mix


def get_ratios(ratio):
    """
    Calculates the ratios using a received float

    :param ratio: A float betwenn 0 and 2 resembling the ratio between two things
    :return ratio_1, ratio_2: The two calculated actual ratios
    """

    ratio = float(ratio)
    ratio_1 = ratio / 2
    ratio_2 = (2 - ratio) / 2
    return ratio_1, ratio_2


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
        n = sample * (1.0 / 32768)
        sum_squares += n * n
    rms = math.sqrt(sum_squares / count) + 0.0001
    db = 20 * math.log10(rms)
    return db


def calculate_difference(data_1, data_2):
    """
    Calculates the difference level in decibel between the received binary inputs

    :param data_1: The first binary digit
    :param data_2: The second binary digit
    :return difference: The calculated difference level (in dB)
    """

    difference = calculate_decibel(data_1) - calculate_decibel(data_2)
    return difference


def calculate_wave(original, inverted, ratio):
    """
    Converts the bytestrings it receives into plottable integers and calculates the difference between both

    :param original: A bytestring of sound
    :param inverted: A bytestring of sound
    :param ratio: A float which determines the mix-ratio of the two samples
    :return int_original, int_inverted, int_difference: A tupel of the three calculated integers
    """

    # Calculate the actual ratios based on the float the function received
    (ratio_1, ratio_2) = get_ratios(ratio)
    # Convert the two samples to integers to be able to add them together
    int_original = np.fromstring(original, np.int16)[0] * ratio_1
    int_inverted = np.fromstring(inverted, np.int16)[0] * ratio_2
    # Calculate the difference between the two samples
    int_difference = (int_original + int_inverted)

    return int_original, int_inverted, int_difference


def plot_results(data, nth_iteration):
    """
    Plots the list it receives and cuts off the first ten entries to circumvent the plotting of initial silence

    :param data: A list of data to be plotted
    :param nth_iteration: Used for the label of the x axis
    """

    # Plot the data
    plt.plot(data[10:])

    # Label the axes
    plt.xlabel('Time (every {}th {} byte)'.format(nth_iteration, CHUNK))
    plt.ylabel('Volume level difference (in dB)')

    # Calculate and output the absolute median difference level
    plt.suptitle('Difference - Median (in dB): {}'.format(np.round(np.fabs(np.median(data)), decimals=5)), fontsize=14)

    # Display the plotted graph
    plt.show()


def plot_wave_results(total_original, total_inverted, total_difference, nth_iteration):
    """
    Plots the three waves of the original sound, the inverted one and their difference

    :param total_original: A list of the original wave data
    :param total_inverted: A list of the inverted wave data
    :param total_difference: A list of the difference of 'total_original' and 'total_inverted'
    :param nth_iteration: Used for the label of the x axis
    """

    # Plot the three waves
    plt.plot(total_original, 'b')
    plt.plot(total_inverted, 'r')
    plt.plot(total_difference, 'g')

    # Label the axes
    plt.xlabel('Time (per {}th {} byte chunk)'.format(nth_iteration, CHUNK))
    plt.ylabel('Amplitude (integer representation of each {} byte chunk)'.format(nth_iteration, CHUNK))

    # Calculate and output the absolute median difference level
    plt.suptitle('Waves: original (blue), inverted (red), output (green)', fontsize=14)

    # Display the plotted graph
    plt.show()


# Execute the main function to start the script
main()
