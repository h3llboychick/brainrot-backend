import shutil
import json
from pathlib import Path
from typing import Dict, Any
from random import randint

from celery.utils.log import get_task_logger
from elevenlabs import VoiceSettings
import ffmpy

from ...domain.video_format import VideoFormatStrategy
from ...domain.service_container import ServiceContainer
from ...services.video_formats.registry import VideoFormatRegistry
from ...prompts.would_you_rather import WOULD_YOU_RATHER_PROMPT
from ...utils.ai_helpers import parse_json_response, retry_with_backoff, build_chat_messages
from ...utils.audio import get_mp3_length
from ...settings import settings as worker_settings


logger = get_task_logger(__name__)


@VideoFormatRegistry.register
class WouldYouRatherFormat(VideoFormatStrategy):
    @property
    def format_name(self) -> str:
        return "would_you_rather"
    
    @property
    def required_services(self) -> list[str]:
        return ['ai_client', 'voiceover', 'pexels', 'event_publisher', 'video_storage_manager']
    
    def setup_workspace(self, job_id: str, base_dir: Path) -> Path:
        """Create workspace with scenarios/images and scenarios/audios directories."""
        workspace = base_dir / job_id
        
        # Clean any existing workspace
        if workspace.exists():
            shutil.rmtree(workspace, ignore_errors=True)
        
        # Create directory structure
        scenarios_dir = workspace / "scenarios"
        images_dir = scenarios_dir / "images"
        audios_dir = scenarios_dir / "audios"
        
        images_dir.mkdir(parents=True, exist_ok=True)
        audios_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Created workspace structure for 'would_you_rather': {workspace}")
        
        return workspace
    
    def cleanup_workspace(self, workspace_root: Path) -> None:
        """Remove entire workspace directory."""
        if workspace_root.exists():
            shutil.rmtree(workspace_root, ignore_errors=True)
            logger.info(f"Cleaned up workspace: {workspace_root}")
    
    def generate(
        self,
        job_id: str,
        workspace_root: Path,
        format_settings: Dict[str, Any],
        services: ServiceContainer
    ) -> Path:
        # Get services
        ai_client = services.get('ai_client')
        voiceover_service = services.get('voiceover')
        pexels_client = services.get('pexels')
        event_publisher = services.get('event_publisher')
        video_storage_manager = services.get('video_storage_manager')
        
        # Define paths
        scenarios_dir = workspace_root / "scenarios"
        images_dir = scenarios_dir / "images"
        audios_dir = scenarios_dir / "audios"
        output_video_path = workspace_root / "video.mp4"
        script_path = workspace_root / "script.json"
        
        # Static assets
        background_video_path = Path("media/videos/template.mp4")
        audios_path = Path("media/audios")
        or_audio_path = audios_path / "or.mp3"
        timer_and_ringing_audio_path = audios_path / "timer_and_ringing.mp3"
        silence_audio_path = audios_path / "silence.mp3"
        
        # Step 1: Generate script
        event_publisher.publish_event(job_id, "generating_script", stage="generating_script")
        
        prompt = format_settings.get('prompt', 'Сгенерируй сценарий для видео')
        script = self._generate_script(ai_client, prompt)
        
        # Save script
        with open(script_path, "w", encoding="utf-8") as f:
            json.dump(script, f, indent=2, ensure_ascii=False)
        
        event_publisher.publish_event(job_id, "script_generated", stage="generating_script")
        logger.info(f"Script generated with {len(script)} scenarios")
        
        # Step 2: Fetch assets
        event_publisher.publish_event(job_id, "fetching_assets", stage="fetching_assets")
        
        self._fetch_assets(
            script=script,
            images_dir=images_dir,
            audios_dir=audios_dir,
            voiceover_service=voiceover_service,
            pexels_client=pexels_client,
            job_id=job_id,
            event_publisher=event_publisher
        )
        
        event_publisher.publish_event(job_id, "assets_fetched", stage="fetching_assets")
        logger.info("All assets fetched successfully")
        
        # Step 3: Assemble video
        event_publisher.publish_event(job_id, "assembling", stage="assembling")
        
        self._assemble_video(
            script=script,
            images_dir=images_dir,
            audios_dir=audios_dir,
            output_video_path=output_video_path,
            background_video_path=background_video_path,
            or_audio_path=or_audio_path,
            timer_and_ringing_audio_path=timer_and_ringing_audio_path,
            silence_audio_path=silence_audio_path
        )
        
        event_publisher.publish_event(job_id, "assembled", stage="assembling")
        logger.info(f"Video assembled: {output_video_path}")

        # Step 4: Upload video to permanent storage
        event_publisher.publish_event(job_id, "uploading", stage="uploading")
        video_url = video_storage_manager.upload_video(
            object_name=f"{job_id}.mp4",
            file_path=str(output_video_path)
        )

        event_publisher.publish_event(job_id, "uploaded", stage="uploading", video_url=video_url)
        
        return output_video_path
    
    def _generate_script(self, ai_client, prompt: str) -> Dict[str, Any]:
        """Generate script using AI with retry logic."""
        
        def _attempt_generation():
            messages = build_chat_messages(
                system_prompt=WOULD_YOU_RATHER_PROMPT,
                user_prompt=prompt
            )
            
            response = ai_client.chat_completion(
                messages=messages,
                model=worker_settings.AI_MODEL,
                temperature=worker_settings.AI_TEMPERATURE,
                max_tokens=worker_settings.AI_MAX_TOKENS
            )
            
            script = parse_json_response(response)
            
            # Validate script structure
            if not self._validate_script(script):
                raise ValueError("Invalid script structure")
            
            return script
        
        return retry_with_backoff(
            func=_attempt_generation,
            max_attempts=2,
            exceptions=(json.JSONDecodeError, ValueError),
            operation_name="script generation"
        )
    
    def _validate_script(self, script: Dict[str, Any]) -> bool:
        """Validate that script has the correct structure."""
        if len(script) < 3:
            logger.warning("Script has fewer than 3 scenarios")
            return False
        
        for scenario_key, scenario in script.items():
            if not isinstance(scenario, dict):
                return False
            
            if "option_A" not in scenario or "option_B" not in scenario:
                logger.warning(f"Scenario {scenario_key} missing options")
                return False
            
            for option in [scenario["option_A"], scenario["option_B"]]:
                required_fields = ["short", "long", "stock_image_keyword"]
                if not all(k in option for k in required_fields):
                    logger.warning(f"Option missing required fields: {required_fields}")
                    return False
        
        return True
    
    def _fetch_assets(
        self,
        script: Dict[str, Any],
        images_dir: Path,
        audios_dir: Path,
        voiceover_service,
        pexels_client,
        job_id: str,
        event_publisher
    ) -> None:
        """Fetch all voiceovers and images for the script."""
        def generate_and_save_voiceover(output_file: str, text: str, voice_settings: VoiceSettings = VoiceSettings(stability=0.1, similarity_boost=0.8)) -> None:
            voiceover_service.generate_voiceover(
                output_file=output_file,
                text=text,
                voice_settings=voice_settings,
            )
            if not Path(output_file).exists():
                raise FileNotFoundError(f"Voiceover file not created: {output_file}")
        
        def fetch_and_save_photo(keyword: str, photo_path: str) -> None:
            pexels_client.get_photo(
                keyword=keyword,
                photo_path=photo_path
            )
            if not Path(photo_path).exists():
                raise FileNotFoundError(f"Photo file not created: {photo_path}")

        for scenario_key, scenario in script.items():
            for option_key, option in scenario.items():
                audio_filename = f"{scenario_key}_{option_key}.mp3"
                image_filename = f"{scenario_key}_{option_key}.jpeg"
                
                # Generate voiceover with retry
                try:
                    retry_with_backoff(
                        func=lambda: generate_and_save_voiceover(
                            output_file=str(audios_dir / audio_filename),
                            text=option.get("long", ""),
                            voice_settings=VoiceSettings(stability=0.1, similarity_boost=0.8),
                        ),
                        max_attempts=2,
                        exceptions=(Exception,),
                        operation_name=f"voiceover generation for {audio_filename}"
                    )
                except Exception as e:
                    event_publisher.publish_event(
                        job_id, "failed", stage="fetching_assets",
                        error="VOICEOVER_FAILED", detail=audio_filename
                    )
                    raise RuntimeError(f"Failed to generate voiceover: {audio_filename}")
                # Fetch image with retry
                try:
                    retry_with_backoff(
                        func=lambda: fetch_and_save_photo(
                            keyword=option.get("stock_image_keyword", ""),
                            photo_path=str(images_dir / image_filename)
                        ),
                        max_attempts=2,
                        exceptions=(Exception,),
                        operation_name=f"image fetch for {image_filename}"
                    )
                except Exception as e:
                    event_publisher.publish_event(
                        job_id, "failed", stage="fetching_assets",
                        error="IMAGE_FETCH_FAILED", detail=image_filename
                    )
                    raise RuntimeError(f"Failed to fetch image: {image_filename}")
    
    def _assemble_video(
        self,
        script: Dict[str, Any],
        images_dir: Path,
        audios_dir: Path,
        output_video_path: Path,
        background_video_path: Path,
        or_audio_path: Path,
        timer_and_ringing_audio_path: Path,
        silence_audio_path: Path
    ) -> None:
        """Assemble final video using FFmpeg."""
        
        # Build FFmpeg inputs and filters
        inputs: Dict[str, str | None] = {
            str(background_video_path): None,
            str(or_audio_path): None,
            str(timer_and_ringing_audio_path): None,
            str(silence_audio_path): None,
        }
        
        audio_track = (
            "[3:a][4:a][3:a][1:a][3:a][5:a][3:a][2:a][3:a][3:a]"
            "[8:a][3:a][1:a][3:a][9:a][3:a][2:a][3:a][3:a]"
            "[12:a][3:a][1:a][3:a][13:a][3:a][2:a]"
            "concat=n=26:v=0:a=1[aout]; "
        )
        
        current_index = 6
        photos_scale = ""
        photos_overlay = ""
        percents_text = ""
        current_video_duration = 0.0
        or_sound_duration = get_mp3_length(str(or_audio_path))
        timer_and_ringing_sound_duration = get_mp3_length(str(timer_and_ringing_audio_path))
        
        for key in script.keys():
            scenario_option_a = f"{key}_option_A"
            scenario_option_b = f"{key}_option_B"
            
            inputs[str(audios_dir / f"{scenario_option_a}.mp3")] = None
            inputs[str(audios_dir / f"{scenario_option_b}.mp3")] = None
            inputs[str(images_dir / f"{scenario_option_a}.jpeg")] = None
            inputs[str(images_dir / f"{scenario_option_b}.jpeg")] = None
            
            photos_scale += f"[{current_index}:v]scale=800:500[{scenario_option_a}]; "
            photos_scale += f"[{current_index + 1}:v]scale=800:500[{scenario_option_b}];"
            
            scenario_option_a_audio_duration = get_mp3_length(str(audios_dir / f"{scenario_option_a}.mp3"))
            scenario_option_b_audio_duration = get_mp3_length(str(audios_dir / f"{scenario_option_b}.mp3"))
            
            first_option_percents = randint(1, 100)
            second_option_percents = 100 - first_option_percents
            
            percents_text += (
                f"drawtext=text='{first_option_percents}%':x=(w-text_w)/2:y=(745):expansion=none:"
                f"fontfile=video_formats/would_you_rather/media/fonts/Proxima-Nova-Bold.ttf:fontsize=72:"
                f"fontcolor=white:bordercolor=black:borderw=5:"
                f"enable='between(t,{current_video_duration + scenario_option_a_audio_duration + or_sound_duration + scenario_option_b_audio_duration + timer_and_ringing_sound_duration - 0.9},"
                f"{current_video_duration + scenario_option_a_audio_duration + or_sound_duration + scenario_option_b_audio_duration + timer_and_ringing_sound_duration + 1.1})', "
            )
            percents_text += (
                f"drawtext=text='{second_option_percents}%':x=(w-text_w)/2:y=(1135):expansion=none:"
                f"fontfile=video_formats/would_you_rather/media/fonts/Proxima-Nova-Bold.ttf:fontsize=72:"
                f"fontcolor=white:bordercolor=black:borderw=5:"
                f"enable='between(t,{current_video_duration + scenario_option_a_audio_duration + or_sound_duration + scenario_option_b_audio_duration + timer_and_ringing_sound_duration - 0.9},"
                f"{current_video_duration + scenario_option_a_audio_duration + or_sound_duration + scenario_option_b_audio_duration + timer_and_ringing_sound_duration + 1.1})',"
            )
            
            if photos_overlay:
                photos_overlay += (
                    f"[v][{scenario_option_a}]overlay=140:160:"
                    f"enable='between(t,{current_video_duration + 0.4},"
                    f"{current_video_duration + scenario_option_a_audio_duration + or_sound_duration + scenario_option_b_audio_duration + timer_and_ringing_sound_duration + 1.1})'[v];"
                )
                photos_overlay += (
                    f"[v][{scenario_option_b}]overlay=140:1250:"
                    f"enable='between(t,{current_video_duration + scenario_option_a_audio_duration + or_sound_duration + 0.8},"
                    f"{current_video_duration + scenario_option_a_audio_duration + or_sound_duration + scenario_option_b_audio_duration + timer_and_ringing_sound_duration + 1.1})'[v];"
                )
            else:
                photos_overlay += (
                    f"[0:v][{scenario_option_a}]overlay=140:160:"
                    f"enable='between(t,{current_video_duration + 0.4},"
                    f"{current_video_duration + scenario_option_a_audio_duration + or_sound_duration + scenario_option_b_audio_duration + timer_and_ringing_sound_duration + 1.1})'[v];"
                )
                photos_overlay += (
                    f"[v][{scenario_option_b}]overlay=140:1250:"
                    f"enable='between(t,{current_video_duration + scenario_option_a_audio_duration + or_sound_duration + 0.8},"
                    f"{current_video_duration + scenario_option_a_audio_duration + or_sound_duration + scenario_option_b_audio_duration + timer_and_ringing_sound_duration + 1.1})'[v];"
                )
            
            current_index += 4
            current_video_duration += (
                scenario_option_a_audio_duration
                + or_sound_duration
                + scenario_option_b_audio_duration
                + timer_and_ringing_sound_duration
                + 1.1
            )
        
        percents_text = "[v]" + percents_text[:-1] + "[v]\" "
        inputs[str(background_video_path)] = f"-ss 00:00:00 -t {current_video_duration} "
        
        # Run FFmpeg
        try:
            ff = ffmpy.FFmpeg(
                global_options=["-y", "-hide_banner", "-loglevel error"],
                inputs=inputs,
                outputs={
                    str(output_video_path): (
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
                },
            )
            ff.run()
        except ffmpy.ffmpy.FFRuntimeError as e:
            logger.error(f"FFmpeg runtime error: {e}")
            raise RuntimeError(f"FFmpeg assembly failed: {e}")

