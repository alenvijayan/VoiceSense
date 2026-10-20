
import librosa
import numpy as np
import parselmouth


def extract_features(audio_path):
    """
    Extract 37 acoustic features from an audio recording.

    Audio is converted to mono and resampled to 8000 Hz,
    matching the intended sample rate of the VoiceSense model.
    """

    # Load audio
    y, sr = librosa.load(
        audio_path,
        sr=8000,
        mono=True
    )

    if len(y) < 1024:
        raise ValueError(
            "Audio is too short. Please record at least 1 second."
        )

    # 1. MFCC: 13 features
    mfcc = librosa.feature.mfcc(
        y=y,
        sr=sr,
        n_mfcc=13,
        n_fft=1024
    )

    mfcc_features = {
        f"MFCC_{i + 1}": float(np.mean(mfcc[i]))
        for i in range(13)
    }

    # 2. Chroma: 12 features
    chroma = librosa.feature.chroma_stft(
        y=y,
        sr=sr,
        n_fft=1024
    )

    chroma_features = {
        f"Chroma_{i + 1}": float(np.mean(chroma[i]))
        for i in range(12)
    }

    # 3. RMS energy
    rms = librosa.feature.rms(
        y=y,
        frame_length=1024
    )

    rms_value = float(np.mean(rms))

    # 4. Zero crossing rate
    zcr = librosa.feature.zero_crossing_rate(
        y,
        frame_length=1024
    )

    zcr_value = float(np.mean(zcr))

    # 5. Spectral features
    spectral_centroid = librosa.feature.spectral_centroid(
        y=y,
        sr=sr,
        n_fft=1024
    )

    spectral_bandwidth = librosa.feature.spectral_bandwidth(
        y=y,
        sr=sr,
        n_fft=1024
    )

    spectral_rolloff = librosa.feature.spectral_rolloff(
        y=y,
        sr=sr,
        n_fft=1024
    )

    spectral_contrast = librosa.feature.spectral_contrast(
        y=y,
        sr=sr,
        n_fft=1024,
        n_bands=5,
        fmin=200
    )

    spectral_flatness = librosa.feature.spectral_flatness(
        y=y,
        n_fft=1024
    )

    spectral_features = {
        "Spectral_Centroid": float(np.mean(spectral_centroid)),
        "Spectral_Bandwidth": float(np.mean(spectral_bandwidth)),
        "Spectral_Rolloff": float(np.mean(spectral_rolloff)),
        "Spectral_Contrast": float(np.mean(spectral_contrast)),
        "Spectral_Flatness": float(np.mean(spectral_flatness))
    }

    # 6. Tempo
    tempo, _ = librosa.beat.beat_track(
        y=y,
        sr=sr
    )

    tempo_value = float(
        np.asarray(tempo).flatten()[0]
    )

    # 7. Pitch, jitter, shimmer and HNR
    sound = parselmouth.Sound(audio_path)

    pitch = sound.to_pitch()

    pitch_values = pitch.selected_array["frequency"]
    pitch_values = pitch_values[pitch_values > 0]

    pitch_value = (
        float(np.mean(pitch_values))
        if len(pitch_values) > 0
        else 0.0
    )

    point_process = parselmouth.praat.call(
        [sound, pitch],
        "To PointProcess (cc)"
    )

    try:
        jitter = parselmouth.praat.call(
            point_process,
            "Get jitter (local)",
            0, 0, 0.0001, 0.02, 1.3
        )
    except Exception:
        jitter = 0.0

    try:
        shimmer = parselmouth.praat.call(
            [sound, point_process],
            "Get shimmer (local)",
            0, 0, 0.0001, 0.02, 1.3, 1.6
        )
    except Exception:
        shimmer = 0.0

    try:
        harmonicity = sound.to_harmonicity_cc()

        hnr = parselmouth.praat.call(
            harmonicity,
            "Get mean",
            0, 0
        )

        if not np.isfinite(hnr):
            hnr = 0.0

    except Exception:
        hnr = 0.0

    # Combine all features
    features = {}

    features.update(mfcc_features)
    features.update(chroma_features)

    features["RMS"] = rms_value
    features["ZCR"] = zcr_value

    features.update(spectral_features)

    features["Tempo"] = tempo_value
    features["Pitch"] = pitch_value
    features["Jitter"] = float(jitter)
    features["Shimmer"] = float(shimmer)
    features["HNR"] = float(hnr)

    # Validate feature output
    if len(features) != 37:
        raise ValueError(
            f"Expected 37 features, got {len(features)}."
        )

    if not all(np.isfinite(v) for v in features.values()):
        raise ValueError(
            "Some extracted features are invalid. "
            "Please try a clearer recording."
        )

    return features
