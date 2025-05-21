from google.cloud import storage
import os
import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as generative_models

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/home/pan/Documents/2025/github/video-understanding/resources/ai-2c-gemini.json"

def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # Upload the file
    blob.upload_from_filename(source_file_name)

    return {
        "name": blob.name,
        "size": blob.size,
        "content_type": blob.content_type,
        "public_url": blob.public_url
    }

    print(f"File {source_file_name} uploaded to {destination_blob_name}.")

bucket_name = "ai-bmct-us"  # The name of your GCS bucket
source_file_name = "/home/pan/Downloads/1_en.mp4"
destination_blob_name = "videos/video.mp4"

vertexai.init(project="ai-bmct", location="us-central1")

model = GenerativeModel(
    "gemini-1.5-flash",
)

generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}

language = "Chinese"
prompt = """
# 角色设定：
你是一位影视解说专家，擅长根据剧情描述视频的画面和故事生成一段有趣且吸引人的解说文案。你特别熟悉 tiktok/抖音 风格的影视解说文案创作。

# 任务目标：
1.	根据给定的剧情描述，详细描述视频画面并展开叙述，尤其是对重要画面进行细致刻画。
2.	生成风格符合 tiktok/抖音 的影视解说文案，使其节奏快、内容抓人。
3.	最终结果以 JSON 格式输出，字段包含：
  • "picture"：画面描述
  • "timestamp"：时间戳（表示画面出现的时间-画面结束的时间）
  • "narration"：对应的解说文案

# 输入示例：
```text
在一个黑暗的小巷中，主角缓慢走进，四周静谧无声，只有远处隐隐传来猫的叫声。突然，背后出现一个神秘的身影。
```

# 输出格式：
```json
[
    {
        "picture": "黑暗的小巷中，主角缓慢走进，四周静谧无声，远处有模糊的猫叫声。",
        "timestamp": "00:00-00:17",
        "narration": "昏暗的小巷里，他独自前行，空气中透着一丝不安，隐约中能听到远处的猫叫声。 "
    },
    {
        "picture": "主角背后突然出现一个神秘的身影，气氛骤然紧张。",
        "timestamp": "00:17-00:39",
        "narration": "就在他以为安全时，一个身影悄无声息地出现在他身后，危险一步步逼近！ "
    }
    ...
]
```
# 提示：
  - 生成的解说文案应简洁有力，符合短视频平台用户的偏好。
  - 叙述中应有强烈的代入感和悬念，以吸引观众持续观看。
  - 文案语言为：%s
""" % (language)

video_url = f"gs://{bucket_name}/{destination_blob_name}"
video_file = Part.from_uri(video_url, mime_type="video/mp4")
res = model.generate_content([video_file, prompt])
print(res.text)


