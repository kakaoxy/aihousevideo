import os
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
import json
import requests
from io import BytesIO
import re
import subprocess
import time
import logging
from dotenv import load_dotenv

# 设置环境变量
# 加载.env文件
load_dotenv()

# 获取API密钥
api_key = os.environ.get('API_KEY')

print('接收到API密钥', api_key)




# 设置日志记录
logging.basicConfig(level=logging.INFO, filename='video_generation.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# 设置 ffmpeg 路径
FFMPEG_BINARY = os.path.join(os.path.dirname(__file__), 'ffmpeg')
os.environ["IMAGEIO_FFMPEG_EXE"] = FFMPEG_BINARY

def generate_voice(house_info):
    print('接收到房屋信息', house_info)

    voice_url = 'https://api.coze.cn/v1/workflow/run'
    headers = {
        'Authorization': 'Bearer {api_key}',
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

    voice_res = requests.post(voice_url, headers=headers, json=data)
    
    if voice_res.status_code == 200:
        voice_data = voice_res.json()
        inner_data = json.loads(voice_data['data'])
        print(inner_data)
        return {
            'output': inner_data['output'],
            'output_text': inner_data['output_text']
        }
    else:
        return None

def download_audio_file(audio_url, target_folder):
    response = requests.get(audio_url)
    if response.status_code == 200:
        audio_file_path = os.path.join(target_folder, 'audio.mp3')
        with open(audio_file_path, 'wb') as f:
            f.write(response.content)
        return audio_file_path
    else:
        raise Exception(f"Failed to download audio file: {response.status_code}")

def get_audio_duration(audio_file_path):
    audio_clip = AudioFileClip(audio_file_path)
    duration = audio_clip.duration
    audio_clip.close()
    return duration




def generate_srt_file(output_text, audio_duration, srt_file_path):
    # 将文案按句分割
    sentences = output_text.split('。')
    sentences = [s for s in sentences if s.strip()]  # 去除空句子

    # 分割长句子并清理内容
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

    # 计算每句的显示时间
    sentence_duration = audio_duration / len(short_sentences)

    with open(srt_file_path, 'w', encoding='utf-8') as f:
        for i, sentence in enumerate(short_sentences):
            start_time = i * sentence_duration
            end_time = (i + 1) * sentence_duration
            start_time_str = f"{int(start_time // 3600):02d}:{int((start_time % 3600) // 60):02d}:{int(start_time % 60):02d},{int((start_time % 1) * 1000):03d}"
            end_time_str = f"{int(end_time // 3600):02d}:{int((end_time % 3600) // 60):02d}:{int(end_time % 60):02d},{int((end_time % 1) * 1000):03d}"
            f.write(f"{i + 1}\n")
            f.write(f"{start_time_str} --> {end_time_str}\n")
            f.write(f"{sentence.strip()}\n\n")



def add_srt_to_video(video_file, srt_file, output_video_file):
    # 使用ffmpeg将字幕文件合并到视频中
    # 定义文件路径
    srt_file = srt_file.replace("\\", "/")
    video_file = video_file.replace("\\", "/")
    output_video_file = output_video_file.replace("\\", "/")

    # 创建 FFmpeg 命令
    command = [
        "ffmpeg",
        "-i", video_file,
        "-vf", f"subtitles={srt_file}:force_style='Fontsize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BackColour=&H00000000,BorderStyle=1,Outline=2,MarginV=60'",
        output_video_file
    ]
    print(f"FFmpeg command: {command}")

    # 执行命令
    subprocess.run(command)


    # os.system(command)

def generate_video(house_title,house_desc, image_paths, output_folder=None):
    logger.info('信息已经准备好，开始生成视频，请稍等...')
    print('信息已经准备好，开始生成视频，请稍等...', house_title, house_desc, image_paths)
    start_time = time.time()
    print('接受到信息，开始生成音频，请稍等...')
    audio_url = generate_voice(house_desc)
    print('音频已经生成，开始下载音频，请稍等...')
    if audio_url:
        audio_file_url = audio_url['output']
        output_text = audio_url['output_text']
        images_folder = os.path.dirname(image_paths[0])
        audio_file_path = download_audio_file(audio_file_url, images_folder)
        print('音频已经下载，开始合成视频，请稍等...')

        image_clips = [ImageClip(image_path, duration=3) for image_path in image_paths]
        audio_duration = get_audio_duration(audio_file_path)
        total_image_duration = sum([clip.duration for clip in image_clips])
        while total_image_duration < audio_duration:
            for clip in image_clips:
                if total_image_duration >= audio_duration:
                    break
                total_image_duration += clip.duration
                image_clips.append(clip)

        final_video = concatenate_videoclips(image_clips, method="compose")
        audio_clip = AudioFileClip(audio_file_path)
        final_video = final_video.set_audio(audio_clip)

        if output_folder is None:
            output_folder = images_folder
        video_file = os.path.join(output_folder, f"Video_of_{house_title.replace(' ', '_')}.mp4")
        final_video.write_videofile(
            video_file, 
            fps=15,  # 降低帧率
            codec='libx264', 
            bitrate='500k',  # 降低比特率
            preset='ultrafast'  # 使用最快的预设
            )

        # 生成SRT字幕文件
        srt_file_path = os.path.join(output_folder, rf"Subtitles_of_{house_title.replace(' ', '_')}.srt")
        generate_srt_file(output_text, audio_duration, srt_file_path)

        # 将字幕文件与视频合并
        final_video_with_subs = os.path.join(output_folder, f"Final_Video_of_{house_title.replace(' ', '_')}.mp4")
        add_srt_to_video(video_file, srt_file_path, final_video_with_subs)

        logger.info('视频生成完成，耗时：%.2f 秒' % (time.time() - start_time))
        return final_video_with_subs
    else:
        return None


if __name__ == '__main__':
    # test_generate_video_normal()
    pass