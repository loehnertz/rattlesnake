import sys
import time
import pyaudio
import numpy as np


def print_all_devices():
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        device = p.get_device_info_by_index(i)
        print(
            (device["index"], device["name"]),
            "\t", ("max input/output channels",device["maxInputChannels"],device["maxOutputChannels"]),
            "\t", ("default_sample_rate", device["defaultSampleRate"])
        )


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
# Determines the ratio of the mix
ratio = 1.0


def invert(input_data: bytes):
    """
    Inverts the byte data it received utilizing an XOR operation.

    :param data: A chunk of byte data
    :return inverted: The same size of chunked data inverted bitwise
    """
    data = np.frombuffer(input_data, dtype=np.int16)
    # Invert the integer
    result = np.invert(data)
    # Return the inverted audio data
    return result


def live_mode():
    global ratio

    # Select devices
    print_all_devices()
    print()
    input_device_id = int(input("The input device ID is? __"))
    print("__", end="")
    output_device_id = int(input("The output device ID is? __"))
    print("__", end="")

    # Start live recording
    print('Noise-cancelling is working now...')
    print("Press the ctrl+c to quit.")

    def input_callback(in_data, frame_count, time_info, status):
        # callback function to stream audio, another thread.
        audio = invert(input_data=in_data)
        return (audio, pyaudio.paContinue)

    input_and_output_stream = pa.open(
        input_device_index=input_device_id,
        output_device_index=output_device_id,
        format=pa.get_format_from_width(WIDTH),
        channels= 1,
        rate=SAMPLE_RATE,
        frames_per_buffer=CHUNK,
        input=True,
        output=True,
        stream_callback = input_callback # type: ignore
     )

    while True:
        try:
            input_and_output_stream.start_stream()
            while input_and_output_stream.is_active():
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            # Terminate the program
            input_and_output_stream.stop_stream()
            input_and_output_stream.close()

            pa.terminate()
            sys.exit()


live_mode()
