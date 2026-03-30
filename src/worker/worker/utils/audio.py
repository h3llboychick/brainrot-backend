import ffmpeg
import requests  # type: ignore
from celery.utils.log import get_logger

logger = get_logger(__name__)


def change_speed(
    input_file: str, output_file: str, speed_coefficient: float
) -> None:
    logger.info(
        f"Changing speed of {input_file} by a factor of {speed_coefficient}, saving to {output_file}"
    )

    # Upload the audio file
    upload_url = "https://audiotrimmer.com/audio-speed-changer/up-load.php"
    change_speed_url = (
        "https://audiotrimmer.com/audio-speed-changer/change-media.php"
    )

    file_path = input_file
    form_data_upload = {
        "playable": "yes",
    }

    with open(file_path, "rb") as f:
        files = {"input": f}
        response_upload = requests.post(
            upload_url, data=form_data_upload, files=files
        )  # nosec: B113

    # Check if the upload was successful
    if response_upload.status_code == 200:
        response_data = response_upload.json()  # Parse the JSON response
        logger.info(
            f"Audio file {file_path} uploaded successfully for speed change"
        )

        # Extract details for the next request
        track_url = response_data["url"]
        track_name = response_data["name"]
        track_ext = response_data["ext"]
        folder = response_data["folder"]

        # Change the speed of the uploaded file
        form_data_speed = {
            "track_url": track_url,
            "track_name": track_name,
            "track_ext": track_ext,
            "folder": folder,
            "speed": str(speed_coefficient),  # Desired speed multiplier
        }

        logger.info(
            f"Sending request to change speed of audio file {file_path}"
        )
        response_speed = requests.post(change_speed_url, data=form_data_speed)  # nosec: B113

        # Check the response for the speed change
        if response_speed.status_code == 200:
            logger.info(
                f"Speed change request successful for {file_path}. Trying to download the modified file..."
            )
            response_speed_data = response_speed.json()

            download_url = f"https://audiotrimmer.com/download.php?date={folder}&file={response_speed_data['file']}"

            headers = {
                "Referer": "https://audiotrimmer.com/audio-speed-changer/",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Sec-Fetch-Site": "same-origin",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            }
            response = requests.get(download_url, headers=headers)  # nosec: B113

            # Check if the request was successful
            if response.status_code == 200:
                logger.info(
                    f"Speed changed successfully, downloading the file to {output_file}"
                )

                # Save the downloaded file
                with open(output_file, "wb") as audio_file:
                    audio_file.write(response.content)

                logger.info(f"Modified audio file saved to {output_file}")
            else:
                logger.error(
                    f"Failed to download the file. Status code: {response.status_code}, Response: {response.text}"
                )
        else:
            logger.error(
                f"Failed to change speed. Response: {response_speed.text}"
            )

    else:
        logger.error(
            f"Failed to upload the file. Response: {response_upload.text}"
        )


def get_mp3_length(file_path: str) -> float:
    try:
        logger.info(f"Getting length of MP3 file: {file_path}")
        probe = ffmpeg.probe(filename=file_path)
        duration = float(probe["format"]["duration"])
        logger.info(f"Duration of {file_path}: {duration} seconds")
        return duration
    except Exception as e:
        logger.error(f"Error while getting MP3 length: {e}")
        raise
