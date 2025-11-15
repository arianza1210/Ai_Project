import base64
import json
import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.groq import Groq
from agno.media import Image
from pydantic import BaseModel, Field

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")


class DetectedObject(BaseModel):
    label: str = Field(
        ...,
        description="Nama objek hasil deteksi, berupa string."
    )
    bbox: list = Field(
        ...,
        description="Bounding box berupa list 4 integer: [x_min, y_min, x_max, y_max]"
    )


class DetectionSchema(BaseModel):
    objects: list[DetectedObject] = Field(
        ...,
        description=(
            "List objek terdeteksi. "
            "Setiap item memiliki 'label: str' dan 'bbox: list[int]'."
        )
    )


class ObjectDetectionAgent:
    def __init__(self):
        self._init_agent()

    def _init_agent(self):
        self.agent = Agent(
            name="Groq Vision Object Detector",
            role=(
                "You are an object detection model. "
                "You MUST output only JSON containing detected objects with strict schema."
            ),
            model=Groq(
                id="meta-llama/llama-4-scout-17b-16e-instruct",
                api_key=API_KEY
            ),
            instructions=[
                "Deteksi semua objek terlihat pada gambar.",
                "Untuk setiap objek, berikan dua field:",
                "1. 'label' berupa string (nama objek).",
                "2. 'bbox' berupa list dari 4 integer [x_min, y_min, x_max, y_max].",
                "Pastikan JSON valid dan sesuai schema.",
                "Jangan beri penjelasan tambahan — hanya JSON."
            ],
            output_schema=DetectionSchema,
            use_json_mode=True
        )

    def detect(self, image_path: str):
        prompt = """
Lakukan object detection pada gambar ini.
"""

        result = self.agent.run(
            prompt,
            images=[Image(filepath=image_path)]
        )

        return result.content.model_dump()


if __name__ == "__main__":
    agent = ObjectDetectionAgent()

    image = "data/IMG_20230712_150617_jpg.rf.300be8ce8faef8062d1ac5a29a0f7a91.jpg"
    detections = agent.detect(image)
    print(json.dumps(detections, indent=2))
