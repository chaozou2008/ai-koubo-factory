import pytest
from app.services.tts_service import TencentMAIService


@pytest.mark.asyncio
async def test_tts_service_creates_voice():
    svc = TencentMAIService()
    result = await svc.create_voice_clone(
        audio_url="https://example.com/reference.mp3",
        voice_name="test_voice",
    )
    assert "voice_id" in result
    assert result["voice_name"] == "test_voice"


@pytest.mark.asyncio
async def test_tts_service_synthesizes():
    svc = TencentMAIService()
    result = await svc.synthesize(
        text="大家好，欢迎来到我的直播间",
        voice_id="VOICE-test123",
    )
    assert "audio_url" in result
    assert result["duration_seconds"] > 0
