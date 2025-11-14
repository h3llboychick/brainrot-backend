from ..clients.elevenlabs import get_elevenlabs_client, ElevenLabsClient
from ..utils.audio import change_speed

class VoiceoverGenerationService:
    def __init__(self, elevenlabs_client: ElevenLabsClient):
        self.elevenlabs_client = elevenlabs_client

    def generate_voiceover(
            self, 
            output_file: str, 
            text: str, 
            voice: str = "nPczCjzI2devNBz1zQrb", 
            model: str = "eleven_multilingual_v2", 
            voice_settings: dict = None,
            speed_coefficient: float = 1
        ) -> None:
        self.elevenlabs_client.create_voiceover(
            output_file=output_file,
            text=text,
            voice=voice,
            model=model,
            voice_settings=voice_settings
        )

        if speed_coefficient != 1:
            change_speed(output_file, output_file, speed_coefficient)

def get_voiceover_generation_service(elevenlabs_client: ElevenLabsClient) -> VoiceoverGenerationService:
    return VoiceoverGenerationService(elevenlabs_client)