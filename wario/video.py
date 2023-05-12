import math
import ffmpeg
import os
import subprocess
import re

items_path = os.path.join(os.path.dirname(__file__), "items/")
ffmpeg_items = os.path.join(os.getcwd(), "items")
platform_extension = ".exe" if os.name == "nt" else ""

def makeVideo(videoPath, text = None, *, gif=False):
    #make epicgamer overlay and audio
    intro = ffmpeg.input(items_path + "intro.mp4")
    intro_audio = intro.audio
    if gif == True:
        videoPath = add_slient_audio_encode(videoPath)
    video_with_frame_path = make_frame(videoPath)
    stream = ffmpeg.input(video_with_frame_path)
    info = ffmpeg.probe(video_with_frame_path, cmd=os.path.join(ffmpeg_items, "ffprobe") + platform_extension)["streams"][0]
    #info = ffmpeg.probe(video_with_frame_path, cmd=items_path + "ffprobe" + platform_extension)["streams"][0]
    stream_audio = stream.audio
    
    intro = ffmpeg.filter(intro, "scale", info["width"], info["height"]) #メイン動画に合わせてサイズ変更
    stream = ffmpeg.filter(stream, "tpad", start_duration="1.3", stop_duration=0) #イントロ1.3秒 #アウトロ2秒
    stream_audio = ffmpeg.filter(stream_audio, "afade", duration="0.5") #音声フェード（In）
    stream_audio = ffmpeg.filter(stream_audio, "adelay", delays=1300, all=1) #1300 = 1.3
    intro = ffmpeg.filter(intro, "colorkey", color="red", similarity=0.1, blend=0.3) #イントロ赤背景透過
    merge_stream = ffmpeg.overlay(stream, intro, x=0, y=0) #overlay intro

    outro = ffmpeg.input(items_path + "outro.mp4", itsoffset=f"{int(float(info['duration'])) + 2}") #itsoffsetで遅延させる
    outro_audio = outro.audio
    outro = ffmpeg.filter(outro, "scale", info["width"], info["height"]) #メイン動画に合わせてサイズ変更
    outro = ffmpeg.filter(outro, "colorkey", color="red", similarity=0.1, blend=0.3) #アウトロの赤背景透過
    outro_audio = ffmpeg.filter(outro_audio, "adelay", delays=f"{int(float(info['duration'])) + 2}s", all=1) #アウトロの音声遅延
    merge_stream = ffmpeg.overlay(merge_stream, outro, x=0, y=0) #overlay outro

    audio = ffmpeg.filter([stream_audio, intro_audio, outro_audio], 'amix', 3) #三つの音を合成
    if (text != None):
        if check_in_kanji(text) == False:
            font = "analog.ttf"
        else:
            font = "kyoukasyo.ttc"
        if text.isascii() == True:
            text_list = split_text(text, 18)
        else:
            text_list = split_text(text, 12)
        text = "\n\n".join(text_list)
        first_text_size = info["width"] * 1.5
        second_text_size = info["width"] / 15
        merge_stream = ffmpeg.filter(merge_stream, "drawtext",x=str(info["width"] / 2) + "-text_w / 2",y=str(info["height"] / 2) + "-text_h / 2",
            text=text ,fontfile=items_path + font, fontcolor="white",
            borderw=(info["width"]) / 75, bordercolor="black", enable=f"between(t,1.2,1.5)", fontsize=f'{first_text_size}+({second_text_size}-{first_text_size})*(t-0)/(1.6-0)')

        merge_stream = ffmpeg.filter(merge_stream, "drawtext",x=str(info["width"] / 2) + "-text_w / 2",y=str(info["height"] / 2) + "-text_h / 2",
            text=text ,fontfile=items_path + font, fontcolor="white",
            borderw=(info["width"]) / 75, bordercolor="black", fontsize=second_text_size, enable=f"between(t,1.5,4)")
    #print(str((info["width"] + info["height"]) / 2))
    #print(str((info["width"] + info["height"]) / 20))

    #出力
    filename = os.path.splitext(videoPath)[0] + "_wario.mp4"
    output_options = {"c:v": "libx264", "preset": "slow", "movflags": "+faststart", "flags": "+cgop", "r": "30", "threads": math.ceil(os.cpu_count() / 2)}
    stream = ffmpeg.output(merge_stream, audio, filename, **output_options)
    ffmpeg.run(stream, cmd=os.path.join(ffmpeg_items, "ffmpeg") + platform_extension, overwrite_output=True)
    #ffmpeg.run(stream, cmd=items_path + "ffmpeg" + platform_extension, overwrite_output=True)
    os.remove(video_with_frame_path)
    if gif == True:
        os.remove(videoPath)
    return filename

def make_frame(videoPath, *, gif=False):
    stream_info = ffmpeg.probe(videoPath, cmd=os.path.join(ffmpeg_items, "ffprobe") + platform_extension)["streams"][0]
    #stream_info = ffmpeg.probe(videoPath, cmd=items_path + "ffprobe" + platform_extension)["streams"][0]
    frame_info = ffmpeg.probe(items_path + "bg.png", cmd=os.path.join(ffmpeg_items, "ffprobe") + platform_extension)["streams"][0]
    #frame_info = ffmpeg.probe(items_path + "bg.png", cmd=items_path + "ffprobe" + platform_extension)["streams"][0]
    stream = ffmpeg.input(videoPath)
    frame = ffmpeg.input(items_path + "bg.png")
    audio = stream.audio
    #stream = ffmpeg.filter(stream, "anullsrc", channel_layout="stereo")

    frame_width = int(abs(stream_info["width"] / 9))
    frame_height = int(abs(stream_info["height"] / 9.3))
    if big_height(stream_info) == True:
        frame = ffmpeg.filter(frame, "scale", frame_info["width"], stream_info["height"] + frame_height * 2)
        stream = ffmpeg.filter(stream, "pad", frame_info["width"], stream_info["height"] + frame_height * 2, x=abs(frame_info["width"] - stream_info["width"] / 2), y=frame_height)
    else:
        frame = ffmpeg.filter(frame, "scale", stream_info["width"] + frame_width * 2, stream_info["height"] + frame_height * 2)
        stream = ffmpeg.filter(stream, "pad", stream_info["width"] + frame_width * 2, stream_info["height"] + frame_height * 2, x=frame_width, y=frame_height)
    merge_stream = ffmpeg.overlay(stream, frame, x=0, y=0)

    filename = os.path.splitext(videoPath)[0]
    #options = {"b:a": "192k", "aac_coder": "twoloop", "threads": math.ceil(os.cpu_count() / 2)}
    options = {"b:a": "192k", "aac_coder": "twoloop", "threads": 4}
    stream = ffmpeg.output(merge_stream, audio, filename + "_with_frame.mp4", **options)
    ffmpeg.run(stream, cmd=os.path.join(ffmpeg_items, "ffmpeg") + platform_extension, overwrite_output=True)
    #ffmpeg.run(stream, cmd=items_path + "ffmpeg" + platform_extension, overwrite_output=True)
    return filename + "_with_frame.mp4"

def add_slient_audio_encode(videoPath):
    filename = os.path.splitext(videoPath)[0]
    subprocess.run(f"{items_path}ffmpeg{platform_extension} -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 -i {videoPath} -c:v copy -c:a aac -shortest -threads {math.ceil(os.cpu_count() / 2)} -y {filename}_added_slient_audio.mp4", shell=True)
    return f"{filename}_added_slient_audio.mp4"

def big_height(info):
    if info["height"] >= 590:
        if info["width"] <= 880:
            return True
    return False

def check_in_kanji(text):
    pattern = re.compile('[一-鿐]+')
    if pattern.search(text) == None:
        return False
    return True

def split_text(text, count):
    #12文字目で区切る
    if count >= len(text):
        return [text]
    limit_num = 0
    text_list = []
    while True:
        if limit_num >= 50:
            break
        limit_num += 1 
        add_split_text = text[0:count]
        text_list.append(add_split_text)
        if len(text[count:]) >= count:
            text = text[count:]
        else:
            if text[count:] != "":
                text_list.append(text[count:])
            break
    return text_list

#import glob
#files = glob.glob("./debug_items/*.mp4")
#for file in files:
#    makeVideo(file, "あいうえおかきくけこ")
#loop = asyncio.get_event_loop()
#loop.run_until_complete(makeVideo("./debug_items/test1_v.mp4", "TEST09"))
#makeVideo("debug_items/car.mp4", "はしれ")