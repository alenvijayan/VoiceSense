from utils.feature_extraction import extract_features

audio_path = r"C:\Users\alwyn\OneDrive\Desktop\MCA_miniproject\parkinson\archive (11)\Parkinson_Dataset\Healthy\healthy_002.wav"

features = extract_features(audio_path)

print("Number of features:", len(features))

for name, value in features.items():
    print(f"{name}: {value}")