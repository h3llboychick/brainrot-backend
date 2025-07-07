from dotenv import load_dotenv

import ffmpy

from video_formats.dual_video.prompts import DUAL_FORMAT_PROMPT, SYSTEM_DUAL_FORMAT_PROMPT

from common.subtitles import create_subtitles
from common.audio import get_mp3_length, create_voiceover
from common.redis_publisher import update_status

import os
import typing
import openai
import logging




load_dotenv()


def generate(
        system_prompt: str, 
        prompt: str, 
        ai_client: openai.OpenAI, 
        model: str = "DeepSeek-V3-0324",
        temperature: float = 0.8,
        max_tokens: int = 512
    ) -> typing.Union[dict, None]:
    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": prompt,
        }
    ]

    response = ai_client.chat.completions.create(
        model = model,
        messages = messages,
        max_tokens = max_tokens,
        max_completion_tokens = max_tokens,
        temperature = temperature
    )
    
    text = response.choices[0].message.content
    return text

def create_video(
    video_id: str,
):
    path_to_video = f"{video_id}"
    '''try:
        os.mkdir(f"{path_to_video}")
    except FileExistsError:
        for root, dirs, files in os.walk(path_to_video, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))'''

    balls_path = os.path.join(os.getcwd(), "media", "videos", "balls.mp4")
    parkour_path = os.path.join(os.getcwd(), "media", "videos", "parkour.mp4")
    mask_path = os.path.join(os.getcwd(), "media", "images", "mask.png")
    voiceover_path = os.path.join(path_to_video, "voiceover.mp3")
    subtitles_path = os.path.join(path_to_video, "subtitles.srt")
    #fonts_path = os.path.join(os.getcwd(), "video_formats", "dual_video", "media", "fonts")
    voiceover_duration = get_mp3_length(voiceover_path)

    sambanova_api_key = os.getenv("SAMBANOVA_API_KEY")
    eleven_labs_api_key = os.getenv("ELEVENLABS_API_KEY")

    # Generating and saving script for a video
    ai_client = openai.OpenAI(
        api_key = sambanova_api_key,
        base_url = "https://api.sambanova.ai/v1"
    )
    '''
    logging.info("Generating and saving script for a video")
    text = generate(
        system_prompt = SYSTEM_DUAL_FORMAT_PROMPT,
        prompt = DUAL_FORMAT_PROMPT, 
        ai_client = ai_client,
        max_tokens = 1024
    )

    logging.info("Generating voiceover")
    create_voiceover(
        output_file = voiceover_path,
        text = text,
        api_key = eleven_labs_api_key
    )

    logging.info("Generating subtitles")
    create_subtitles(
        audio = voiceover_path,
        output_file = subtitles_path
    )'''
       
    inputs = {
        parkour_path: f"-ss 00:00:00 -t {voiceover_duration} ",
        balls_path: f"-ss 00:00:00 -t {voiceover_duration} ",
        mask_path: None,
        voiceover_path: None
    }

    subtitles_path = f"{path_to_video}/subtitles.srt"
    ff = ffmpy.FFmpeg(
        global_options = ["-y", "-hide_banner"],
        inputs = inputs,
        outputs = {
            "output.mp4": (
                "-filter_complex \""
                "[1:v]crop=1080:960[ovr]; [2:v]scale=1080:960[mask]; [ovr][mask]alphamerge[ovr_alpha]; [0:v][ovr_alpha]overlay=0:960[out]; "
                f"[out]subtitles={subtitles_path}:force_style='Alignment=10,FontName=Proxima Nova Rg,FontSize=16,PrimaryColour=&H00FFFFFF,Outline=1,OutlineColour=&H00000000'[out]; "
                "\" "
                "-map \"[out]\" " 
                "-map 3:a:0 "      
                "-c:v h264_nvenc "      
                "-c:a libmp3lame "   
            )
        } 
    )

    #print(ff.cmd)
    ff.run()

if __name__ == "__main__":
    logging.basicConfig(
        level = logging.INFO,
        format = "%(asctime)s - %(levelname)s - %(message)s",
    )
    logging.info("Starting video generation")
    # Пример использования функции
    create_video(
        video_id = "example_video",
    )

