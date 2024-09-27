#  框选得到图片中所有的需要的值
import cv2

def extract_and_save_firstframe(video_path, output_image_path):
    """
    Extract the first frame from the video and save it to the specified path.

    Parameters:
    video_path (str): Path to the video file.
    output_image_path (str): Path where the extracted frame will be saved.
    """
    video = cv2.VideoCapture(video_path)
    
    if not video.isOpened():
        print("Error: Could not open video.")
        return

    ret, frame = video.read()
    
    if not ret:
        print("Error: Could not read the first frame.")
        video.release()
        return
    
    cv2.imwrite(output_image_path, frame)
    video.release()
    print(f"First frame extracted and saved to {output_image_path}")

def extract_firstframe(video_path):
    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        print("Error: Could not open video.")
        return False
    
    ret, frame = video.read()
    
    if not ret:
        print("Error: Could not read the first frame.")
        video.release()
        return False
    
    video.release()
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    

def cut_save_video(video_path, output_path):
# 打开视频文件
    video = cv2.VideoCapture(video_path)

    # 获取视频的帧率和总帧数
    fps = video.get(cv2.CAP_PROP_FPS)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    # 获取视频的宽度和高度
    frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # 计算截取的帧数（前10秒）
    num_frames_to_capture = int(fps * 10)  # 10秒的视频对应的帧数

    # 初始化视频写入器
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    # 逐帧读取视频并写入前10秒的视频
    for i in range(min(num_frames_to_capture, total_frames)):
        ret, frame = video.read()
        if ret:
            out.write(frame)
        else:
            break

    # 释放资源
    video.release()
    out.release()

    print(f"前10秒的视频已成功保存为 {output_path}")

class Framed_Values:

    def __init__(self) -> None:
        
        self.Num_Frames = 0
        self.colorRGB   = [255, 0, 0]
    
    def get():
        1


if __name__ == "__main__":

    path_video = "../0_data/video/3min_test.mp4"
    path_pic   = "../0_data/video/3min_test.png" 
    
    path_savevideo = "../0_data/video/10s_test.mp4"
    # extract_and_save_firstframe(path_video, path_pic)

    cut_save_video(path_video, path_savevideo)