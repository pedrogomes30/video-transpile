import cv2
import os
import re

def extract_timestamps_from_blog(blog_text):
    timestamps = []
    matches = re.findall(r"\[(\d+\.\d+) - (\d+\.\d+)\]", blog_text)
    for match in matches:
        timestamps.append(float(match[0]))
    return timestamps

def capture_frames_by_timestamps(video_path, timestamps, output_dir):
    frames_dir = os.path.join(output_dir, "frames")
    os.makedirs(frames_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    for timestamp in timestamps:
        frame_number = int(timestamp * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        if ret:
            frame_path = os.path.join(frames_dir, f"frame_{timestamp:.2f}.jpg")
            cv2.imwrite(frame_path, frame)

    cap.release()
    return frames_dir