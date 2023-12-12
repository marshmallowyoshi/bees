# import pickle
import torch
import torchaudio
from torchaudio.transforms import *
import os

class MyPipeline(torch.nn.Module):
    def __init__(
        self,
        input_freq=16000,
        resample_freq=8000,
        n_fft=1024,
        n_mel=256,
        stretch_factor=0.8,
    ):
        super().__init__()
        self.resample = Resample(orig_freq=input_freq, new_freq=resample_freq)

        self.spec = Spectrogram(n_fft=n_fft, power=2)

        self.spec_aug = torch.nn.Sequential(
            TimeStretch(stretch_factor, fixed_rate=True),
            FrequencyMasking(freq_mask_param=80),
            TimeMasking(time_mask_param=80),
        )

        self.mel_scale = MelScale(
            n_mels=n_mel, sample_rate=resample_freq, n_stft=n_fft // 2 + 1)

    def forward(self, waveform: torch.Tensor) -> torch.Tensor:
        # Resample the input
        resampled = self.resample(waveform)

        # Convert to power spectrogram
        spec = self.spec(resampled)

        # Apply SpecAugment
        spec = self.spec_aug(spec)

        # Convert to mel-scale
        mel = self.mel_scale(spec)

        return mel

class BeeDataset(torch.utils.data.Dataset):
    def __init__(self, files):
        self.files = files

    def __getitem__(self, index):
        label = self._get_sample_label(self.files[index])
        waveform, sample_rate = torchaudio.load(self.files[index])
        return waveform

    def __len__(self):
        return len(self.files)

if __name__ == "__main__":
    pass

print(torch.__version__)
print(torchaudio.__version__)

torch.random.manual_seed(0)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print(device)

SUBFOLDER = "audio\wav"
all_files = [SUBFOLDER + "\\" + f for f in os.listdir(SUBFOLDER) if f.endswith(".wav")]

for f in all_files:
    print(f)
    waveform, sample_rate = torchaudio.load(f)
    # Instantiate a pipeline
    pipeline = MyPipeline()

    # Move the computation graph to CUDA
    pipeline.to(device=torch.device("cuda"), dtype=torch.float32)
    waveform = waveform.to(device=torch.device("cuda"), dtype=torch.float32)

    # Perform the transform
    features = pipeline(waveform)
    