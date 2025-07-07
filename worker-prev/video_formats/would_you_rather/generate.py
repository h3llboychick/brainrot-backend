from dotenv import load_dotenv
from elevenlabs import VoiceSettings

import os
import openai
import typing
import uuid
import json
import logging
import sys
from random import randint
import redis

import ffmpy

from video_formats.would_you_rather.prompts import WOULD_YOU_RATHER_PROMPT

from common.formatting import remove_think_tags, remove_json_markdown 
from common.audio import get_mp3_length, create_voiceover
from common.pexels import get_photo_from_pexels
from common.redis_publisher import update_status

import pika


load_dotenv()

def generate(
        system_prompt: str, 
        prompt: str, 
        ai_client: openai.OpenAI, 
        model: str = "DeepSeek-R1-Distill-Llama-70B",
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
    
    text = remove_json_markdown(remove_think_tags(response.choices[0].message.content))

    try:
        parsed_json = json.loads(text)
    except json.JSONDecodeError:
        parsed_json = {}
                
    return parsed_json

def create_video(
    video_id: str,
    redis_client: redis.Redis,
    source: str,
    chat_id: typing.Optional[int] = None,
    status_message_id: typing.Optional[int] = None
) -> None:
    status = {
        "status": {
            "name": "started",
            "text": "Video generation started..."
        },
        "video_id": video_id,
        "source": source,
        "telegram_params": {
            "chat_id": chat_id,
            "status_message_id": status_message_id
        } if source == "telegram" else None,
        "video_url": None
    }
    redis_key = f"video:{video_id}"
    
    
    logging.info(f"Creating structure for saving video project. Video ID: {video_id}")
    update_status(
        r = redis_client, 
        key = redis_key,
        status = status
    )

    # Creating structure for saving video project
    path_to_video = os.path.join("/videos", video_id)
    try:
        os.mkdir(f"{path_to_video}")
    except FileExistsError:
        for root, dirs, files in os.walk(path_to_video, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
    os.mkdir(f"{path_to_video}/scenarios")
    os.mkdir(f"{path_to_video}/images")

    video_output_path = os.path.join(path_to_video, "video.mp4")

    scenarios_audio_output_path = os.path.join(path_to_video, "scenarios")
    scenarios_images_output_path = os.path.join(path_to_video, "images")
    script_output_path = os.path.join(path_to_video, "script.json")
    background_video_path = os.path.join(os.getcwd(), "video_formats", "would_you_rather", "media", "videos", "template.mp4")
    audios_path = os.path.join(os.getcwd(), "video_formats", "would_you_rather", "media", "audios")
    or_audio_path = os.path.join(audios_path, "or.mp3")
    timer_and_ringing_audio_path = os.path.join(audios_path, "timer_and_ringing.mp3")
    silence_audio_path = os.path.join(audios_path, "silence.mp3")

    # Getting all the API keys needed for generation
    sambanova_api_key = os.getenv("SAMBANOVA_API_KEY")
    eleven_labs_api_key = os.getenv("ELEVENLABS_API_KEY")
    pexels_api_key = os.getenv("PEXELS_API_KEY")

    # Generating and saving script for a video
    ai_client = openai.OpenAI(
        api_key = sambanova_api_key,
        base_url = "https://api.sambanova.ai/v1"
    )
    logging.info("Generating and saving script for a video")

    attempts = 2
    while attempts > 0:
        script = generate(
            system_prompt = WOULD_YOU_RATHER_PROMPT,
            prompt = "Сгенерируй сценарий для видео", 
            ai_client = ai_client,
            max_tokens = 1024
        )
        if not script:
            logging.error("Failed to generate script. Retrying...")
            attempts -= 1
            continue
        with open(script_output_path, "w", encoding = "utf-8") as f:
            json.dump(script, f, indent = 4, ensure_ascii = False)
        break
    if attempts == 0:   
        logging.error("Failed to generate script. Quitting...")
        status["status"] = {
            "name": "failed",
            "text": "Failed to generate script."
        }
        update_status(
            r = redis_client, 
            key = redis_key,
            status = status
        )
        return
    
    status["status"] = {
        "name": "script_generated",
        "text": "Script generated successfully."
    }
    logging.info("Script generated successfully")
    update_status(
        r = redis_client, 
        key = redis_key,
        status = status
    )

    logging.info("Creating a voiceover and fecthing images for each option")
    for key, scenario in script.items():
        for key_option, option in scenario.items():
            attempts = 2
            while attempts > 0:
                try:
                    create_voiceover(
                        output_file = os.path.join(scenarios_audio_output_path, f"{key}_{key_option}.mp3"),
                        text = option["long"],
                        api_key = eleven_labs_api_key,
                        voice_settings = VoiceSettings(
                            stability = 0.1,
                            similarity_boost = 0.8
                        )
                    )    
                    if not os.path.exists(os.path.join(scenarios_audio_output_path, f"{key}_{key_option}.mp3")):
                        logging.error(f"Failed to create voiceover for {key}_{key_option}.mp3. Retries left: {attempts - 1}")
                        attempts -= 1
                        continue
                    break
                except Exception as e:
                    logging.error(f"Failed to create voiceover for {key}_{key_option}.mp3. Error: {e}. Retries left: {attempts - 1}")
                    attempts -= 1
                    continue
            if attempts == 0:
                status["status"] = {
                    "name": "failed",
                    "text": "Failed to create voiceover."
                }
                logging.error(f"Failed to create voiceover for {key}_{key_option}.mp3. Qutting...")
                update_status(
                    r = redis_client, 
                    key = redis_key,
                    status = status
                )
                return
            attempts = 2
            while attempts > 0:
                try: 
                    get_photo_from_pexels(
                        api_key = pexels_api_key,
                        keyword = option["stock_image_keyword"],
                        photo_path = os.path.join(scenarios_images_output_path, f"{key}_{key_option}.jpeg")
                    )
                    if not os.path.exists(os.path.join(scenarios_images_output_path, f"{key}_{key_option}.jpeg")):
                        logging.error(f"Failed to create image for {key}_{key_option}.jpeg. Retries left: {attempts - 1}")
                        attempts -= 1
                        continue
                    break
                except Exception as e:
                    logging.error(f"Failed to create image for {key}_{key_option}.jpeg. Error: {e}. Retries left: {attempts - 1}")
                    attempts -= 1
                    continue
            if attempts == 0:
                status["status"] = {
                    "name": "failed",
                    "text": "Failed to create images for video."
                }
                logging.error(f"Failed to create image for {key}_{key_option}.jpeg. Qutting...")
                update_status(
                    r = redis_client, 
                    key = redis_key,
                    status = status
                )
                return
    status["status"] = {
        "name": "medias_generated",
        "text": "Voiceovers and images generated successfully."
    }   
    logging.info("Creating audio and video tracks for video")        
    update_status(
        r = redis_client, 
        key = redis_key,
        status = status
    )

    inputs = {
        background_video_path: None,
        or_audio_path: None,
        timer_and_ringing_audio_path: None,
        silence_audio_path: None
    }

    current_index = 6

    photos_scale = ""
    photos_overlay = ""

    audio_track = (
        "[3:a][4:a][3:a][1:a][3:a][5:a][3:a][2:a][3:a][3:a][8:a][3:a][1:a][3:a][9:a][3:a][2:a][3:a][3:a][12:a][3:a][1:a][3:a][13:a][3:a][2:a]concat=n=26:v=0:a=1[aout]; "
    )
    percents_text = ""

    or_sound_duration = get_mp3_length(or_audio_path)
    timer_and_ringing_sound_duration = get_mp3_length(timer_and_ringing_audio_path)

    current_video_duration = 0

    for key in script.keys():
        scenario_option_a = f"{key}_option_A"
        scenario_option_b= f"{key}_option_B"

        inputs[os.path.join(scenarios_audio_output_path, f"{scenario_option_a}.mp3")] = None
        inputs[os.path.join(scenarios_audio_output_path, f"{scenario_option_b}.mp3")] = None

        inputs[os.path.join(scenarios_images_output_path, f"{scenario_option_a}.jpeg")] = None
        inputs[os.path.join(scenarios_images_output_path, f"{scenario_option_b}.jpeg")] = None
        
        photos_scale += f"[{current_index}:v]scale=800:500[{scenario_option_a}]; " 
        photos_scale += f"[{current_index + 1}:v]scale=800:500[{scenario_option_b}];"

        scenario_option_a_audio_duration = get_mp3_length(os.path.join(scenarios_audio_output_path, f"{scenario_option_a}.mp3"))
        scenario_option_b_audio_duration = get_mp3_length(os.path.join(scenarios_audio_output_path, f"{scenario_option_b}.mp3"))

        first_option_percents = randint(1, 100)
        second_option_percents = 100 - first_option_percents

        percents_text += f"drawtext=text='{first_option_percents}%':x=(w-text_w)/2:y=(745):expansion=none:fontfile=video_formats/would_you_rather/media/fonts/Proxima-Nova-Bold.ttf:fontsize=72:fontcolor=white:bordercolor=black:borderw=5:enable='between(t,{current_video_duration + scenario_option_a_audio_duration + or_sound_duration + scenario_option_b_audio_duration + timer_and_ringing_sound_duration - 0.9},{current_video_duration + scenario_option_a_audio_duration + or_sound_duration + scenario_option_b_audio_duration + timer_and_ringing_sound_duration + 1.1})', "
        percents_text += f"drawtext=text='{second_option_percents}%':x=(w-text_w)/2:y=(1135):expansion=none:fontfile=video_formats/would_you_rather/media/fonts/Proxima-Nova-Bold.ttf:fontsize=72:fontcolor=white:bordercolor=black:borderw=5:enable='between(t,{current_video_duration + scenario_option_a_audio_duration + or_sound_duration + scenario_option_b_audio_duration + timer_and_ringing_sound_duration - 0.9},{current_video_duration + scenario_option_a_audio_duration + or_sound_duration + scenario_option_b_audio_duration + timer_and_ringing_sound_duration + 1.1})',"

        if photos_overlay:
            photos_overlay += f"[v][{scenario_option_a}]overlay=140:160:enable='between(t,{current_video_duration + 0.4},{current_video_duration + scenario_option_a_audio_duration + or_sound_duration + scenario_option_b_audio_duration + timer_and_ringing_sound_duration + 1.1})'[v];"
            photos_overlay += f"[v][{scenario_option_b}]overlay=140:1250:enable='between(t,{current_video_duration + scenario_option_a_audio_duration + or_sound_duration + 0.8},{current_video_duration + scenario_option_a_audio_duration + or_sound_duration + scenario_option_b_audio_duration + timer_and_ringing_sound_duration + 1.1})'[v];"

        else:
            photos_overlay += f"[0:v][{scenario_option_a}]overlay=140:160:enable='between(t,{current_video_duration + 0.4},{current_video_duration + scenario_option_a_audio_duration + or_sound_duration + scenario_option_b_audio_duration + timer_and_ringing_sound_duration + 1.1})'[v];"
            photos_overlay += f"[v][{scenario_option_b}]overlay=140:1250:enable='between(t,{current_video_duration + scenario_option_a_audio_duration + or_sound_duration + 0.8},{current_video_duration + scenario_option_a_audio_duration + or_sound_duration + scenario_option_b_audio_duration + timer_and_ringing_sound_duration + 1.1})'[v];"

        current_index += 4
        current_video_duration += scenario_option_a_audio_duration + or_sound_duration + scenario_option_b_audio_duration + timer_and_ringing_sound_duration + 1.1

    percents_text = "[v]"+ percents_text[:-1] + "[v]\" "

    inputs[background_video_path] = f"-ss 00:00:00 -t {current_video_duration} "

    try:
        ff = ffmpy.FFmpeg(
            global_options = ["-y", "-hide_banner", "-loglevel error"],
            inputs = inputs,
            outputs = {
                video_output_path: (
                    "-filter_complex \""
                    f"{audio_track}"
                    f"{photos_scale}"
                    f"{photos_overlay}"
                    f"{percents_text}"
                    "-map \"[v]\" "       
                    "-map \"[aout]\" "        
                    "-c:v libx264 "      
                    "-c:a libmp3lame "       
                )
            } 
        )
        ff.run()
    except ffmpy.ffmpy.FFRuntimeError:
        status["status"] = {
            "name": "failed",
            "text": "Failed to create video."
        }
        logging.error("Failed to create video. Quitting...")
        update_status(
            r = redis_client, 
            key = redis_key,
            status = status
        )
        return
    except Exception as e:
        status["status"] = {
            "name": "failed",
            "text": "Failed to create video."
        }
        logging.error(f"Failed to create video. Error: {e}. Quitting...")
        update_status(
            r = redis_client, 
            key = redis_key,
            status = status
        )
    status["status"] = {
        "name": "generated",
        "text": "Video generated successfully."
    }
    status["video_url"] = "127.0.0.1:8000/media/" + video_id + "/video.mp4"
    logging.info("Video generated successfully")
    update_status(
        r = redis_client, 
        key = redis_key,
        status = status
    )
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host = 'brainrot_automation-rabbit-mq-1',
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue = "video_upload")
    channel.basic_publish(
        exchange = "",
        routing_key = "video_upload",
        body = json.dumps({
            "file_path": video_output_path,
            "video_id": video_id,
            "source": source,
            "telegram_params": {
                "chat_id": chat_id,
                "status_message_id": status_message_id
            } if source == "telegram" else None
        })
    )
    channel.close()
    connection.close()

def create_video_from_sources(video_id: str):
    pass
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    redis_client = redis.Redis(
        host = "localhost",
        port = 6379
    )
    print(sys.argv)
    if len(sys.argv) > 1 and sys.argv[1] == "source":
        if len(sys.argv) == 3:
            video_id = sys.argv[2]
            if os.path.exists(os.path.join("videos", video_id)):
                create_video_from_sources(
                    video_id = video_id,
                    redis_client = redis_client
                )
            else:
                logging.error("No video with such id exists.")
    else:
        video_id = uuid.uuid4()
        create_video(
            video_id = video_id,
            redis_client = redis_client
        )
        
    
    '''video_id = "a0d264aa-3c5e-47b5-8cbd-08c5f578b793"
    create_video_from_sources(
        video_id = video_id
    )'''