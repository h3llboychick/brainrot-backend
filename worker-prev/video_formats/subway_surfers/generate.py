from moviepy import VideoFileClip, AudioFileClip, CompositeVideoClip, TextClip, CompositeAudioClip, ImageClip, vfx, afx
from moviepy.video.tools.subtitles import SubtitlesClip
import moviepy

import openai

import os
import typing
import dotenv
import redis

from common.audio import create_voiceover, get_mp3_length
from common.subtitles import create_subtitles
from common.redis_publisher import update_status

from .prompts import VIDEO_GENERATION_SYSTEM_PROMPT, TITLE_GENERATION_PROMPT, TAGS_PROMPT

dotenv.load_dotenv()

def generate(
        system_prompt: str, 
        prompt: str, 
        ai_client: openai.OpenAI, 
        model: str = "Meta-Llama-3.3-70B-Instruct",
        temperature: float = 0.8,
        max_tokens: int = 512
    ) -> typing.Union[str, None]:
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
        temperature = temperature,
    )
    
    text = response.choices[0].message.content
    return text

def create_video(
    user_prompt: str,
    video_id: str,
    redis_client: redis.Redis,
    chat_id: int,
    status_message_id: int
) -> None:
    path_to_video = f"../videos/{video_id}"

    try:
        os.mkdir(path_to_video)
    except FileExistsError:
        for root, dirs, files in os.walk(path_to_video, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

    voice_output = os.path.join(path_to_video, "audio.mp3")
    subtitles_output = os.path.join(path_to_video, "subtitles.srt")
    video_output = os.path.join(path_to_video, "video.mp4")

    videos_path = os.path.join(os.getcwd(), "video_formats", "subway_surfers", "media", "videos")
    music_path = os.path.join(os.getcwd(), "video_formats", "subway_surfers", "media", "music")
    
    sambanova_api_key = os.getenv("SAMBANOVA_API_KEY")
    
    eleven_labs_api_key = os.getenv("ELEVENLABS_API_KEY")


    ai_client = openai.OpenAI(
        api_key = sambanova_api_key,
        base_url="https://api.sambanova.ai/v1"
    )

    text = generate(
        system_prompt = VIDEO_GENERATION_SYSTEM_PROMPT,
        prompt = user_prompt, 
        ai_client = ai_client,
        max_tokens = 92
    )

    title = generate(
        system_prompt = TITLE_GENERATION_PROMPT,
        prompt = text,
        ai_client = ai_client,
    )

    description = generate(
        system_prompt = TAGS_PROMPT,
        prompt = text,
        ai_client = ai_client
    )

    print(
        {
            "title": title,
            "description": description,
            "text": text
        }
    )
    
    create_voiceover(
        output_file = voice_output,
        text = text,
        api_key = eleven_labs_api_key
    )

    create_subtitles(
        audio = voice_output,
        output_file = subtitles_output
    )
    
    audio_size = get_mp3_length(voice_output)

    videos = [os.path.join(videos_path, video) for video in os.listdir(videos_path)]
    
    video = VideoFileClip(
        videos[1], 
        audio = False
    ).with_effects([vfx.MultiplySpeed(1.3)])

    music_clip = AudioFileClip(
        os.path.join(
            music_path,
            "blade_runner_2049.mp3"
        )
    ).with_effects([afx.MultiplyVolume(0.1)]).subclipped(0, audio_size + 0.2)
    
    audio = AudioFileClip(voice_output)

    generator = lambda txt: TextClip(
        font = "/usr/share/fonts/Proxima-Nova-Bold.otf", 
        text = txt, 
        font_size = 72, 
        color = "white",
        method = "caption",
        text_align = "center",
        stroke_color = "black",
        stroke_width = 2,
        size = (video.w, video.h),
    )

    subtitles = SubtitlesClip(
        subtitles_output, 
        make_textclip = generator
    )

    audio_tracks = CompositeAudioClip([audio, music_clip])
    
    sub_clip = video.subclipped(5, audio_size + 5.2)
    
    sub_clip: moviepy.CompositeVideoClip = CompositeVideoClip(
        [sub_clip, subtitles.with_position(('center', 'center'))]
    ).with_audio(audio_tracks)

    sub_clip.write_videofile(
        video_output,
        codec = "libx264",
        audio_bitrate = "96k",
        ffmpeg_params = [
            "-crf", "32", "-profile:v", "main"
        ],
        threads = 4,
        preset = "ultrafast"
    )
    
    return {
        "title": title,
        "description": description,
        "text": text
    }

if __name__ == "__main__":
    create_video(
        user_prompt = "Albert Einstein created a formula for wealth. He says that wealth equals gambling x 100%"
    )
    '''model = openai.OpenAI(
        api_key = os.getenv("SAMBANOVA_API_KEY"),
        base_url="https://api.sambanova.ai/v1",
    )'''
    #print(generate(system_prompt = VIDEO_GENERATION_SYSTEM_PROMPT, prompt = "Elon Musk tells that gambling is the only future for humanity.", model = model))