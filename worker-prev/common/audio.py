from elevenlabs.client import ElevenLabs
from elevenlabs import save
import ffmpeg._probe
import requests
import logging
import ffmpeg


def create_voiceover(
        api_key, 
        output_file,
        text, 
        voice = "Brian",
        model = "eleven_multilingual_v2",
        voice_settings = None,
        speed_coefficient = 1
    ):
    elevenlabs_client = ElevenLabs(
        api_key = api_key,
    )
    audio = elevenlabs_client.generate(
        text = text, # Use prompts.TEST_TTS_PROMPT for testing
        voice = voice,
        model = model,   
        voice_settings = voice_settings
    )

    save(audio, output_file)
    if speed_coefficient != 1:
        change_speed(output_file, output_file, speed_coefficient)
    
def change_speed(input_file, output_file, speed_coefficient):
    upload_url = "https://audiotrimmer.com/audio-speed-changer/up-load.php"
    change_speed_url = "https://audiotrimmer.com/audio-speed-changer/change-media.php"

    # File to upload
    file_path = input_file

    # Step 1: Upload the file
    form_data_upload = {
        "playable": "yes",
    }

    files = {
        "input": open(file_path, "rb"),
    }

    response_upload = requests.post(upload_url, data=form_data_upload, files=files)

    # Close the file
    files["input"].close()

    # Check if the upload was successful
    if response_upload.status_code == 200:
        response_data = response_upload.json()  # Parse the JSON response
        print(f"Upload successful: {response_data}")

        # Extract details for the next request
        track_url = response_data["url"]
        track_name = response_data["name"]
        track_ext = response_data["ext"]
        folder = response_data["folder"]

        # Step 2: Change the speed of the uploaded file
        form_data_speed = {
            "track_url": track_url,
            "track_name": track_name,
            "track_ext": track_ext,
            "folder": folder,
            "speed": str(speed_coefficient),  # Desired speed multiplier
        }

        response_speed = requests.post(change_speed_url, data=form_data_speed)

        # Check the response for the speed change
        if response_speed.status_code == 200:
            response_speed_data = response_speed.json()

            download_url = f"https://audiotrimmer.com/download.php?date={folder}&file={response_speed_data['file']}"


            headers = {
                "Referer": "https://audiotrimmer.com/audio-speed-changer/",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Sec-Fetch-Site": "same-origin",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            }
            response = requests.get(
                download_url,
                headers = headers
            )

            # Check if the request was successful
            if response.status_code == 200:
                # Save the downloaded file
                with open(output_file, "wb") as audio_file:
                    audio_file.write(response.content)
            else:
                print("Failed to download the file.")
                print(f"Status code: {response.status_code}")
                print(f"Response: {response.text}")
        else:
            print("Failed to change speed.")
            print("Response:", response_speed.text)

    else:
        print("Failed to upload the file.")
        print("Response:", response_upload.text)

def get_mp3_length(file_path):
    """
    Get the length of an MP3 file in seconds.

    Args:
        file_path (str): Path to the MP3 file.

    Returns:
        float: Length of the MP3 file in seconds.
    """
    try:
        probe = ffmpeg._probe.probe(filename = file_path)
        duration = float(probe['format']['duration'])
        return duration
    except Exception as e:
        logging.info(f"Error: {e}")
        return None
    