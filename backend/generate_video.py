import os
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
import json
import requests
from io import BytesIO
import re
import subprocess
import time
import logging
from typing import List, Optional
from dotenv import load_dotenv

# 设置环境变量
# 加载.env文件 获取API密钥
load_dotenv()
api_key = os.environ.get('API_KEY')

# 配置日志记录器
import logging

# 配置日志记录器
logging.basicConfig(
    level=logging.INFO,  # 设置日志级别
    format='%(asctime)s - %(levelname)s - %(message)s',  # 设置日志格式
    handlers=[
        logging.FileHandler("video_generation.log", mode='w'),  # 输出到文件
        logging.StreamHandler()  # 输出到标准输出（终端）
    ]
)

# 获取日志记录器
logger = logging.getLogger(__name__)



# 设置 ffmpeg 路径
FFMPEG_BINARY = os.path.join(os.path.dirname(__file__), 'ffmpeg')
os.environ["IMAGEIO_FFMPEG_EXE"] = FFMPEG_BINARY

def generate_voice(house_info: str) -> dict:
    logger.info('Starting voice generation...')
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Host': 'api.coze.cn',
            'Connection': 'keep-alive'
        }
        data = {
            "workflow_id": "7425542805542141952",
            "parameters": {
                "BOT_USER_INPUT": house_info,
            }
        }

        response = requests.post('https://api.coze.cn/v1/workflow/run', headers=headers, json=data)
        response.raise_for_status()  # Raises an HTTPError for bad responses

        voice_data = response.json()
        inner_data = json.loads(voice_data['data'])
        
        return {
            'output': inner_data['output'],
            'output_text': inner_data['output_text']
        }
    except requests.exceptions.HTTPError as http_err:
        logging.error(f'HTTP error occurred: {http_err}')  # Log HTTP errors
        return None
    except Exception as err:
        logging.error(f'Other error occurred: {err}')  # Log other errors
        return None
    
def download_audio_file(audio_url: str, target_folder: str) -> str:
    logger.info('Starting audio download...')
    if not os.path.exists(target_folder):
        error_msg = f"Target folder does not exist: {target_folder}"
        logging.error(error_msg)
        raise ValueError(error_msg)

    audio_file_path = os.path.join(target_folder, 'audio.mp3')

    try:
        response = requests.get(audio_url, stream=True)
        response.raise_for_status()  # Raises an HTTPError for bad responses

        with open(audio_file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        logging.info(f"Audio file downloaded successfully: {audio_file_path}")
        return audio_file_path
    except requests.exceptions.HTTPError as http_err:
        error_msg = f"HTTP error occurred while downloading audio file: {http_err}"
        logging.error(error_msg)
        raise Exception(error_msg)
    except Exception as err:
        error_msg = f"An error occurred while downloading audio file: {err}"
        logging.error(error_msg)
        raise Exception(error_msg)

def get_audio_duration(audio_file_path: str) -> float:
    logger.info('Starting get audio duration...')
    if not os.path.isfile(audio_file_path):
        error_msg = f"Audio file not found: {audio_file_path}"
        logging.error(error_msg)
        raise FileNotFoundError(error_msg)

    try:
        with AudioFileClip(audio_file_path) as audio_clip:
            duration = audio_clip.duration
        logging.info(f"Audio duration retrieved successfully: {duration} seconds")
        return duration
    except Exception as err:
        error_msg = f"Failed to get audio duration: {err}"
        logging.error(error_msg)
        raise Exception(error_msg)




def generate_srt_file(output_text: str, audio_duration: float, srt_file_path: str) -> None:
    logger.info('Starting generate srt...')
    if not output_text:
        error_msg = "Output text is empty."
        logging.error(error_msg)
        raise ValueError(error_msg)

    if audio_duration <= 0:
        error_msg = "Audio duration must be positive."
        logging.error(error_msg)
        raise ValueError(error_msg)

    sentences = output_text.split('。')
    sentences = [s for s in sentences if s.strip()]  # Remove empty sentences

    short_sentences = []
    for sentence in sentences:
        cleaned_sentence = re.sub(r'[^\w\s，。、！？；：“”‘’（）《》【】…—.,!?;:(){}<>"]', '', sentence)
        if len(cleaned_sentence) > 20:
            sub_sentences = cleaned_sentence.split('，')
            for sub_sentence in sub_sentences:
                if len(sub_sentence) > 20:
                    for i in range(0, len(sub_sentence), 20):
                        short_sentences.append(sub_sentence[i:i + 20])
                else:
                    short_sentences.append(sub_sentence)
        else:
            short_sentences.append(cleaned_sentence)

    if not short_sentences:
        error_msg = "No sentences to write to SRT file."
        logging.error(error_msg)
        raise ValueError(error_msg)

    sentence_duration = audio_duration / len(short_sentences)

    try:
        with open(srt_file_path, 'w', encoding='utf-8') as f:
            for i, sentence in enumerate(short_sentences):
                start_time = i * sentence_duration
                end_time = (i + 1) * sentence_duration
                start_time_str = f"{int(start_time // 3600):02d}:{int((start_time % 3600) // 60):02d}:{int(start_time % 60):02d},{int((start_time % 1) * 1000):03d}"
                end_time_str = f"{int(end_time // 3600):02d}:{int((end_time % 3600) // 60):02d}:{int(end_time % 60):02d},{int((end_time % 1) * 1000):03d}"
                f.write(f"{i + 1}\n")
                f.write(f"{start_time_str} --> {end_time_str}\n")
                f.write(f"{sentence.strip()}\n\n")
    except IOError as e:
        logging.error(f"Failed to write to SRT file: {e}")
        raise



# def add_srt_to_video(video_file: str, srt_file: str, output_video_file: str) -> None:
#     # 使用ffmpeg将字幕文件合并到视频中
#     logger.info('Starting add srt to video...')
#     command = [
#         "ffmpeg",
#         "-i", video_file,
#         "-vf", f"subtitles={srt_file}:force_style='Fontsize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BackColour=&H00000000,BorderStyle=1,Outline=2,MarginV=60'",
#         output_video_file
#     ]
    
#     try:
#         logging.info(f"Running FFmpeg command: {' '.join(command)}")
#         subprocess.run(command, check=True)
#     except subprocess.CalledProcessError as e:
#         logging.error(f"FFmpeg command failed: {e}")
#         raise

# import subprocess
# import logging

def add_srt_to_video(video_file: str, srt_file: str, output_video_file: str) -> None:
    # 使用 ffmpeg 将字幕文件合并到视频中
    logging.info('Starting add srt to video...')
    command = [
        "ffmpeg",
        "-i", video_file,
        "-vf", f"subtitles={srt_file}:force_style='Fontsize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BackColour=&H00000000,BorderStyle=1,Outline=2,MarginV=60'",
        output_video_file
    ]

    try:
        logging.info(f"Running FFmpeg command: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode!= 0:
            logging.error(f"FFmpeg command failed with return code {result.returncode}. Error output: {result.stderr}")
            raise subprocess.CalledProcessError(result.returncode, command, result.stderr)
    except subprocess.CalledProcessError as e:
        logging.error(f"FFmpeg command failed: {e}")
        raise

def generate_video(house_title: str, house_desc: str, image_paths: List[str], output_folder: Optional[str] = None) -> Optional[str]:
    # 参数验证
    if not house_title or not house_desc or not image_paths:
        logger.error("Input parameters are missing or invalid.")
        return None

    # 初始化变量
    start_time = time.time()
    final_video_path = None

    try:
        # 生成音频
        logger.info('Starting video generation...')
        audio_data = generate_voice(house_desc)
        if not audio_data:
            logger.error("Failed to generate audio.")
            return None
        logger.info('Voice generation completed successfully.')
        # 获取音频和字幕信息
        audio_file_url = audio_data['output']
        output_text = audio_data['output_text']

        # 确定输出文件夹
        images_folder = os.path.dirname(image_paths[0]) if image_paths else None
        output_folder = output_folder or images_folder
        if not output_folder:
            logger.error("Output folder is not specified.")
            return None

        # 下载音频文件
        audio_file_path = download_audio_file(audio_file_url, output_folder)
        if not audio_file_path:
            logger.error("Failed to download audio file.")
            return None

        # 获取音频时长
        logger.info('Voice download completed successfully.')
        audio_duration = get_audio_duration(audio_file_path)
        if audio_duration <= 0:
            logger.error("Audio duration is not valid.")
            return None
        
        logger.info('Audio duration retrieved successfully.')
        # 创建图像剪辑
        image_clips = [ImageClip(m, duration=3) for m in image_paths]
        total_image_duration = sum(clip.duration for clip in image_clips)

        # 确保图像剪辑时长至少与音频时长一样长
        while total_image_duration < audio_duration:
            image_clips.extend(image_clips)
            total_image_duration = sum(clip.duration for clip in image_clips)
        
        logger.info('Image duration retrieved successfully.')
        # 合成视频
        final_video = concatenate_videoclips(image_clips, method="compose")
        audio_clip = AudioFileClip(audio_file_path)
        final_video = final_video.set_audio(audio_clip)

        logger.info('Video generation completed successfully.')
        # 输出视频文件
        video_file = os.path.join(output_folder, f"Video_of_{house_title.replace(' ', '_')}.mp4")
        final_video.write_videofile(
            video_file,
            fps=15,
            codec='libx264',
            bitrate='500k',
            preset='ultrafast'
        )

        logger.info('Video file saved successfully.')

        # 生成字幕文件
        srt_file_path = os.path.join(output_folder, f"Subtitles_of_{house_title.replace(' ', '_')}.srt")
        generate_srt_file(output_text, audio_duration, srt_file_path)

        logger.info('SRT file generated successfully.')

        # 将字幕文件与视频合并
        final_video_with_subs = os.path.join(output_folder, f"Final_Video_of_{house_title.replace(' ', '_')}.mp4")
        if not add_srt_to_video(video_file, srt_file_path, final_video_with_subs):
            logger.error("Failed to add subtitles to video.")
            return None

        logger.info('Subtitles added to video successfully.')

        # 记录完成
        final_video_path = final_video_with_subs
        logger.info(f'Video generation completed in {time.time() - start_time:.2f} seconds.')

    except Exception as e:
        logger.exception("An error occurred during video generation: %s", e)

    return final_video_path


if __name__ == '__main__':
    # 测试代码
    house_title = "新天地河滨花园"
    house_desc = "此房南北通，高区看苏州河、长风公园，二手买入价高，税费少，业主二手买入价，新装修3年多，屋况佳，适合对装修有要求的客户；适合二孩改善家庭，\n              此房是2011年的房龄，板式住宅，高区视野，南北直通双阳台，南看小区中间花园，北看苏州河，两房朝南，一房朝北，两卫全明，很棒的一套房子！\n              2011年社区，新长宁集团开发小区环境优美 ，自带小桥流水，绿树成荫 ，，自然风景秀丽物业安保严格，古北物业，物业费3.2元，很实惠哦\n            \n           "
    image_paths = ["uploaded_images/20241105202117/0GTgbJD1TrFG89751a2c9eaf78ea6942ccf111985e5d.jpg",
    "uploaded_images/20241105202117/jzHVmPlte6bG093d0fd9bcfe58f1325fe98d7f2f735d.jpg",
    "uploaded_images/20241105202117/xJ7u9ZyVtH5X5d74982d83538f31829297c13335772f.jpg",
    "uploaded_images/20241105202117/kDuZE4FDRTxl43e8c842448671cd48acdfb521315789.jpg",
    "uploaded_images/20241105202117/aXRL4tFYlH1d2f5a55b81315938e3beb962cb786f0bf.jpg",
    "uploaded_images/20241105202117/y3eOrK83h2ohf2b72fa46aa73c3c29e1417f45453804.jpg",
    "uploaded_images/20241105202117/6P0G0ypZ7qlTd166901acf47772679a73ed2736e9550.jpg",
    "uploaded_images/20241105202117/PrHUWjQcQHkz2bca637fa5b4f804abf3b015c1179c8f.jpg",
    "uploaded_images/20241105202117/ZeyaArcvuNg7069e71b8dc401d085b9792a7ae51a91a.jpg",
    "uploaded_images/20241105202117/rw7GeQDt4n6J6d4536570743dc4fd8fa1a564057c943.jpg",
    "uploaded_images/20241105202117/Z7ZN0ompGt2569b43cf2260c9cc7f4d1e48ad1188ec1.jpg",
    "uploaded_images/20241105202117/66WHnELolufX3fb0536f1a0c674eaf00d2b4c4e7aeb5.jpg"]
    generate_video(house_title, house_desc, image_paths)
    pass