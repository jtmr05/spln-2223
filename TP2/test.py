import whisper

model = whisper.load_model("base")

# load audio and pad/trim it to fit 30 seconds
audio = whisper.load_audio("./O_QUE_E_A_INTELIGENCIA_ARTIFICIAL_AI.mp3")
audio = whisper.pad_or_trim(audio)
print(audio.shape)

# make log-Mel spectrogram and move to the same device as the model
mel = whisper.log_mel_spectrogram(audio.flatten()).to(model.device)

# detect the spoken language
_, probs = model.detect_language(mel)
print(f"Detected language: {max(probs, key=probs.get)}")

# decode the audio
options = whisper.DecodingOptions()
result = whisper.decode(model, mel, options)

# print the recognized text
print(result.text)
