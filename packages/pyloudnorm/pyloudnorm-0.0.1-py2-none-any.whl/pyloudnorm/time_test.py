import scipy.io.wavfile
import pyloudnorm.loudness
import pyloudnorm.util

rate, data = scipy.io.wavfile.read("Vox2_16bit.wav")
data = pyloudnorm.util.validate_input_data(data, rate)

for i in range(1000):
    pyloudnorm.loudness.measure_gated_loudness(data, rate)


