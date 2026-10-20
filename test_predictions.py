from utils.feature_extraction import extract_features
from utils.prediction import predict_voice

audio_path = r"C:\Users\alwyn\OneDrive\Desktop\MCA_miniproject\parkinson\archive (11)\Parkinson_Dataset\Healthy\healthy_002.wav"

features = extract_features(audio_path)
result = predict_voice(features)

print("\nVoiceSense Prediction")
print("---------------------")
print("Prediction:", result["label"])
print(f'Confidence: {result["confidence"]:.2f}%')
print(
    f'Healthy probability: '
    f'{result["healthy_probability"]:.2f}%'
)
print(
    f'Parkinson probability: '
    f'{result["parkinson_probability"]:.2f}%'
)