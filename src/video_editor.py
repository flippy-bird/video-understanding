from moviepy import VideoFileClip
import os

# 我需要按照要求切分视频
def clip_video(input_video_path, start_time, end_time):
    """
    剪辑单个视频片段
    
    Args:
        input_video_path (str): 输入视频路径
        start_time (float): 开始时间（秒）
        end_time (float): 结束时间（秒）
    
    Returns:
        str: 输出视频路径
    """
    # 加载视频
    video = VideoFileClip(input_video_path)
    
    # 剪辑视频
    clipped_video = video.subclipped(start_time, end_time)
    
    # 保存剪辑后的视频
    # clipped_video.write_videofile(output_path)
    
    # 关闭视频对象
    # video.close()
    # clipped_video.close()
    
    return clipped_video

def clip(video_path_list, video_narration_info):
    """
    处理多个视频片段的剪辑
    
    Args:
        video_path_list (list): 视频路径列表
        video_narration_info (list): 视频解说信息列表，每个元素包含 start_time 和 end_time
    
    Returns:
        list: 剪辑后的视频路径列表
    """
    clipped_videos = []
    
    for video_path, narration_info in zip(video_path_list, video_narration_info):
        start_time = narration_info.get('start_time', 0)
        end_time = narration_info.get('end_time')
        
        if end_time is None:
            # 如果没有指定结束时间，则使用视频总时长
            video = VideoFileClip(video_path)
            end_time = video.duration
            video.close()
        
        clipped_path = clip_video(video_path, start_time, end_time)
        clipped_videos.append(clipped_path)
    
    return clipped_videos

if __name__ == "__main__":
    video_path = "/home/pan/Documents/2025/github/video-understanding/test_resources/videos/1.mp4"

    clip_res = clip_video(video_path, 0, 10)
    clip_res.write_videofile("./cache/output.mp4")
        # clip_res.close()

