import requests

def create_subtitles(audio, output_file):
    """
    Generate subtitles for an audio file using Whisper.

    Args:
        audio (str): Path to the audio file.
        output_file (str): Path to save the output SRT file.
    Creates an SRT file with one-word-per-subtitle segments.
    """

    '''
    model = whisper.load_model("medium")  # Change to your desired model
    transcription = model.transcribe(audio = audio, word_timestamps=True)
    '''

    data = {
        "timestamp_granularities[]": ["word"],
        "stream": False,
        "response_format": "verbose_json",
        "language": "en"
    }
    
    with open(audio, "rb") as file:
        files = {
            "file": file
        }
        transcription = requests.post("http://localhost:8000/v1/audio/transcriptions", files = files, data =  data)

    transcription = transcription.json()


    processed_segments = process_word_timestamps(transcription)

    output_srt = segments_to_srt(processed_segments)
    with open(output_file, "w", encoding = "utf-8") as file:
        file.write(output_srt)

def process_word_timestamps(transcription):
    """
    Process Whisper transcription with word timestamps to generate one-word-per-subtitle segments.

    Args:
        transcription (dict): The transcription dictionary from Whisper with 'segments' and word timestamps.
    
    Returns:
        List of one-word subtitle segments as dictionaries.
    """
    processed_segments = []
    for segment in transcription['segments']:
        words = segment.get('words', [])
        for word in words:
            processed_segments.append({
                'start': word['start'],
                'end': word['end'],
                'text': word['word']
            })
    return processed_segments

# Convert processed segments into SRT format
def segments_to_srt(processed_segments):
    """
    Convert processed subtitle segments into SRT format.

    Args:
        processed_segments (list): List of subtitle segments as dictionaries.
    
    Returns:
        str: Subtitles in SRT format.
    """
    srt_lines = []
    for i, segment in enumerate(processed_segments, start=1):
        start_time = segment['start']
        end_time = segment['end']
        text = segment['text']
        
        # Format timestamps
        start_time_str = f"{int(start_time // 3600):02}:{int((start_time % 3600) // 60):02}:{int(start_time % 60):02},{int((start_time % 1) * 1000):03}"
        end_time_str = f"{int(end_time // 3600):02}:{int((end_time % 3600) // 60):02}:{int(end_time % 60):02},{int((end_time % 1) * 1000):03}"
        
        srt_lines.append(f"{i}\n{start_time_str} --> {end_time_str}\n{text}\n\n")
    
    return "".join(srt_lines)

if __name__ == "__main__":
    create_subtitles("output_data/test_audio.mp3", "test_output.srt")