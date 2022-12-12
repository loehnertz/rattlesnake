import pyaudio
import wave
import io

CHUNK = 1

def print_all_devices():
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        device = p.get_device_info_by_index(i)
        print(
            (device["index"], device["name"]),
            "\t", ("max input/output channels",device["maxInputChannels"],device["maxOutputChannels"]),
            "\t", ("default_sample_rate", device["defaultSampleRate"])
        )

print_all_devices()

output_device_id = int(input("The output device ID is? __"))

with open("/Users/yingshaoxo/Downloads/noisy talk_DeepFilterNet2.wav", 'rb') as f:
    the_wav_file_bytes = f.read()

wave_instance = wave.open(io.BytesIO(the_wav_file_bytes), 'rb')
width = wave_instance.getsampwidth()
channels = wave_instance.getnchannels()
rate = wave_instance.getframerate()
print(width, channels, rate)

pa = pyaudio.PyAudio()

output_stream = pa.open(
    output_device_index=output_device_id,
    format=pyaudio.get_format_from_width(width),
    channels=channels,
    rate=rate,
    output=True
)

while True:
    file_wav_chunk_data = wave_instance.readframes(CHUNK)
    if file_wav_chunk_data == b'':
        wave_instance = wave.open("/Users/yingshaoxo/Downloads/noisy talk_DeepFilterNet2.wav", 'rb')
    else:
        output_stream.write(file_wav_chunk_data)
