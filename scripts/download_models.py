"""Script para descargar los modelos ML necesarios."""
import subprocess
import sys


def download_whisper():
    """Pre-descarga el modelo de Whisper."""
    print("Descargando modelo Whisper 'small'...")
    from faster_whisper import WhisperModel

    WhisperModel("small", device="cpu", compute_type="int8")
    print("Modelo Whisper descargado.")


def download_speechbrain():
    """Pre-descarga el modelo SpeechBrain ECAPA-TDNN."""
    print("Descargando modelo SpeechBrain ECAPA-TDNN...")
    from speechbrain.inference.speaker import EncoderClassifier

    EncoderClassifier.from_hparams(
        source="speechbrain/spkrec-ecapa-voxceleb",
        savedir="models/speechbrain",
    )
    print("Modelo SpeechBrain descargado.")


def download_piper():
    """Descarga modelo TTS de piper para español."""
    print("Descargando modelo Piper TTS para español...")
    subprocess.run(
        [
            "piper", "--model", "es_ES-davefx-medium",
            "--output_file", "/dev/null",
        ],
        input=b"test",
        capture_output=True,
    )
    print("Modelo Piper descargado.")


if __name__ == "__main__":
    download_whisper()
    download_speechbrain()
    try:
        download_piper()
    except FileNotFoundError:
        print("AVISO: piper no encontrado en PATH. Instálalo manualmente.")
    print("\nTodos los modelos descargados correctamente.")
