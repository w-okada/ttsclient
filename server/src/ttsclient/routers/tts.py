import io
import wave

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from simple_performance_timer.Timer import Timer

from ttsclient.models.tts import (
    GenerateVoiceParam,
    GetJpTextToUserDictRecordsParam,
    GetPhonesParam,
    GetPhonesResponse,
    OpenJTalkUserDictRecord,
)
from ttsclient.services.tts_manager import TTSManager
from ttsclient.services.tts_queue import TTSQueue

router = APIRouter(prefix="/api/tts-manager/operation")


@router.post("/generateVoice")
async def generate_voice(param: GenerateVoiceParam):
    with Timer("generateVoice total"):
        sample_rate, audio_data = await TTSQueue.get_instance().submit(param)

        audio_buffer = io.BytesIO()
        with wave.open(audio_buffer, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_data.tobytes())
        audio_buffer.seek(0)

        audio_bytes = len(audio_data.tobytes())
        duration = audio_bytes / (sample_rate * 2)

    return StreamingResponse(
        audio_buffer,
        media_type="audio/wav",
        headers={
            "Content-Disposition": "attachment; filename=output.wav",
            "X-Audio-Duration": f"{duration:.6f}",
        },
    )


@router.post("/getPhones", response_model=GetPhonesResponse)
async def get_phones(param: GetPhonesParam):
    phones, phone_symbols = TTSManager.get_instance().get_phones(param)
    return GetPhonesResponse(phones=phones, phone_symbols=phone_symbols)


@router.post("/getJpTextToUserDictRecords", response_model=list[OpenJTalkUserDictRecord])
async def get_jp_text_to_user_dict_records(param: GetJpTextToUserDictRecordsParam):
    return TTSManager.get_instance().jp_text_to_user_dict_records(param)
