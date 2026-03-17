import json
import uuid
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sara.schemas.websocket import (
    WSErrorMessage,
    WSRecognitionMessage,
    WSStatusMessage,
    WSTranscriptMessage,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/v1/audio-stream")
async def audio_stream(websocket: WebSocket):
    await websocket.accept()
    session_id = uuid.uuid4()
    audio_buffer = bytearray()

    logger.info("WebSocket conectado, session_id=%s", session_id)

    try:
        # Enviar estado inicial
        await websocket.send_json(WSStatusMessage(status="listening").model_dump())

        while True:
            message = await websocket.receive()

            if "bytes" in message:
                # Audio binario recibido
                audio_buffer.extend(message["bytes"])

                # Verificar si hay suficiente audio acumulado (>1s a 16kHz, 16bit)
                # 16000 samples/s * 2 bytes/sample = 32000 bytes/s
                if len(audio_buffer) >= 32000:
                    await websocket.send_json(WSStatusMessage(status="processing").model_dump())

                    try:
                        from sara.services.audio_service import audio_service
                        from sara.services.speaker_service import speaker_service
                        from sara.services.stt_service import stt_service
                        from sara.models.database import async_session

                        # Convertir audio a WAV
                        wav_bytes = await audio_service.convert_to_wav(bytes(audio_buffer))

                        async with async_session() as db:
                            # Verificar hablante
                            verify_result = await speaker_service.verify(
                                audio_bytes=wav_bytes, db=db
                            )

                            if verify_result.recognized:
                                # Usuario reconocido
                                await websocket.send_json(
                                    WSRecognitionMessage(
                                        recognized=True,
                                        user_id=str(verify_result.user_id),
                                        name=verify_result.name,
                                        confidence=verify_result.confidence,
                                    ).model_dump()
                                )

                                # Generar y enviar saludo TTS
                                from sara.services.tts_service import tts_service

                                greeting = f"¡Hola {verify_result.name}! ¿Cómo estás?"
                                audio_response = await tts_service.synthesize(greeting)
                                await websocket.send_bytes(audio_response)
                            else:
                                # Usuario no reconocido - iniciar enrolamiento
                                await websocket.send_json(
                                    WSRecognitionMessage(recognized=False).model_dump()
                                )

                                # Pedir nombre
                                from sara.services.tts_service import tts_service

                                prompt = "Hola, soy Sara. No te he reconocido. ¿Cómo te llamas?"
                                audio_response = await tts_service.synthesize(prompt)
                                await websocket.send_bytes(audio_response)

                                # Esperar respuesta con el nombre
                                await websocket.send_json(
                                    WSStatusMessage(status="listening").model_dump()
                                )

                                # Acumular audio de respuesta
                                name_buffer = bytearray()
                                while True:
                                    name_msg = await websocket.receive()
                                    if "bytes" in name_msg:
                                        name_buffer.extend(name_msg["bytes"])
                                        if len(name_buffer) >= 32000:
                                            break
                                    elif "text" in name_msg:
                                        data = json.loads(name_msg["text"])
                                        if data.get("type") == "end_utterance":
                                            break

                                # Transcribir nombre
                                name_wav = await audio_service.convert_to_wav(bytes(name_buffer))
                                transcript = await stt_service.transcribe(name_wav)
                                name = transcript.get("text", "").strip()

                                await websocket.send_json(
                                    WSTranscriptMessage(text=name).model_dump()
                                )

                                if name:
                                    # Enrolar nuevo usuario
                                    await speaker_service.enroll(
                                        audio_bytes=wav_bytes,
                                        name=name,
                                        db=db,
                                    )

                                    confirm = f"Encantada, {name}. Te recordaré la próxima vez."
                                    audio_confirm = await tts_service.synthesize(confirm)
                                    await websocket.send_bytes(audio_confirm)

                    except Exception as e:
                        logger.error("Error procesando audio: %s", e)
                        await websocket.send_json(WSErrorMessage(message=str(e)).model_dump())

                    # Reset buffer
                    audio_buffer = bytearray()
                    await websocket.send_json(WSStatusMessage(status="listening").model_dump())

            elif "text" in message:
                # Mensaje de control JSON
                try:
                    data = json.loads(message["text"])
                    msg_type = data.get("type")

                    if msg_type == "config":
                        logger.info("Config recibida: %s", data)
                    elif msg_type == "end_utterance":
                        # El cliente indica fin de habla manualmente
                        pass
                except json.JSONDecodeError:
                    await websocket.send_json(WSErrorMessage(message="JSON inválido").model_dump())

    except WebSocketDisconnect:
        logger.info("WebSocket desconectado, session_id=%s", session_id)
