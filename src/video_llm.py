
from google.cloud import storage
import os
import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as generative_models
from pathlib import Path
from prompt import RPOMPT_DESC, PROMPT_NARRATION, THEME
from openai import OpenAI
from config import QWEN_API_KEY, QWEN_BASE_URL, QWEN_MODEL
import json_repair
import json

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/home/pan/Documents/2025/github/video-understanding/resources/ai-2c-gemini.json"

class VideoDesc:
    def __init__(self):
        vertexai.init(project="ai-2c-gemini", location="us-central1")

        self.model = GenerativeModel(
            "gemini-2.0-flash",
        )

        self.text_client = OpenAI(
            api_key=QWEN_API_KEY,
            base_url=QWEN_BASE_URL
        )

        self.text_client_model = QWEN_MODEL

    @staticmethod
    def _upload_to_gcs(source_file_name, destination_blob_name, bucket_name="ai-2c-video"):
        """Uploads a file to the bucket."""

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        # Upload the file
        blob.upload_from_filename(source_file_name)

        print(f"File {source_file_name} uploaded to {destination_blob_name}.")
        return {
            "name": blob.name,
            "size": blob.size,
            "content_type": blob.content_type,
            "public_url": blob.public_url
        }
    
    def _deal_with_video(self, input_video_path:str):
        # 上传视频
        video_name = Path(input_video_path).name
        destination_blob_name = f"videos/{video_name}"
        # self._upload_to_gcs(input_video_path, destination_blob_name)

        video_url = f"gs://ai-2c-video/{destination_blob_name}"
        video_file = Part.from_uri(video_url, mime_type="video/mp4")

        return video_file
    
    def generate(self, input_video_path_list:list):
        video_desc_list = []
        for input_video_path in input_video_path_list:
            video_desc = self.describe(input_video_path)
            video_desc_list.append(video_desc)

        res = self.narration(video_desc_list)

        return res
    
    def describe(self, input_video_path:str):
        # 视频预处理
        video_file = self._deal_with_video(input_video_path)

        res =self.model.generate_content([video_file, RPOMPT_DESC])

        return res.text
    

    def narration(self, video_desc_list: list):
        prompt_narration = PROMPT_NARRATION.replace("{theme}", THEME)
        messages = []
        messages.append({"role": "system", "content": prompt_narration})

        video_descs = "每个视频对应的描述是：\n"
        for i, video_desc in enumerate(video_desc_list):
            video_descs += f"视频{i}:" + "\n"
            video_descs += video_desc + "\n"

        messages.append({"role": "user", "content": video_descs})

        res = self.text_client.chat.completions.create(
            model=QWEN_MODEL,
            messages=messages,
        )
        res_json = res.choices[0].message.content.replace("```json", "").replace("```", "")
        res_json = json.loads(res_json)
        # res_json = res.choices[0].message.content.replace("'''json", "").replace("'''", "")
        # res_json = json_repair.repair_json(res_json)

        return res_json

    
if __name__ == "__main__":
    video_desc = VideoDesc()
    video_list = []
    video_list.append("/home/pan/Documents/2025/github/video-understanding/test_resources/videos/1.mp4")
    video_list.append("/home/pan/Documents/2025/github/video-understanding/test_resources/videos/2.mp4")
    video_list.append("/home/pan/Documents/2025/github/video-understanding/test_resources/videos/3.mp4")
    res = video_desc.generate(video_list)
    print(res)

