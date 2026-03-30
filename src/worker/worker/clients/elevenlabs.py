from elevenlabs import save
from elevenlabs.client import ElevenLabs

from ..settings import settings


class ElevenLabsClient:
    def __init__(self, api_key: str):
        self.client = ElevenLabs(api_key=api_key)
        self.text_to_speech = self.client.text_to_speech

    def create_voiceover(
        self,
        output_file,
        text,
        voice="nPczCjzI2devNBz1zQrb",
        model="eleven_multilingual_v2",
        voice_settings=None,
    ) -> None:
        audio = self.text_to_speech.convert(
            text=text,
            voice_id=voice,
            model_id=model,
            voice_settings=voice_settings,
        )

        save(audio, output_file)


def get_elevenlabs_client(
    api_key: str = settings.ELEVENLABS_API_KEY,
) -> ElevenLabsClient:
    return ElevenLabsClient(api_key=api_key)
