import base64
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests


class ImageGenerator:
    def __init__(self, model_name):
        self.model_name = model_name

    def fetch_image_url(self, prompt):
        url = f"https://api.deepinfra.com/v1/inference/{self.model_name}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"bearer {os.getenv('DEEPINFRA_API_KEY')}",
        }
        payload = {
            "prompt": prompt,
            "num_inference_steps": 20,
            "width": 1920,
            "height": 1080,
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                response_data = response.json()
                images = response_data.get("images", [])
                return images[0]
            else:
                print("Request failed:", response.status_code, response.text)
                return "No image URL found"
        except Exception as e:
            print("An error occurred:", str(e))
            return "No image URL found"

    def generate_images(self, prompts):
        img_links = []
        with ThreadPoolExecutor() as executor:
            future_to_prompt = {
                executor.submit(self.fetch_image_url, prompt): prompt
                for prompt in prompts
            }
            for future in as_completed(future_to_prompt):
                try:
                    img_links.append(future.result())
                except Exception as e:
                    print(f"Error fetching image URL: {e}")
                    img_links.append("No image URL found")
        return img_links

    def save_images(self, img_links):
        saved_image_paths = []
        for idx, base64_string in enumerate(img_links):
            try:
                image_data = base64.b64decode(base64_string.split(",")[-1])
                file_name = f"image_{idx}.png"
                with open(file_name, "wb") as image_file:
                    image_file.write(image_data)
                saved_image_paths.append(file_name)
            except Exception as e:
                print(f"Error saving image {idx}: {e}")
        return saved_image_paths

    def upload_images(self, saved_image_paths):
        hosted_urls = []
        url = "https://freeimage.host/api/1/upload"

        for image_path in saved_image_paths:
            try:
                with open(image_path, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode("utf-8")

                payload = {
                    "key": "6d207e02198a847aa98d0a2a901485a5",
                    "action": "upload",
                    "source": base64_image,
                    "format": "json",
                }

                response = requests.post(url, data=payload)

                if response.status_code == 200:
                    response_data = response.json()
                    hosted_urls.append(
                        response_data.get("image", {}).get("url", "No image URL found")
                    )
                else:
                    print("Request failed:", response.status_code, response.text)

            except Exception as e:
                print("An error occurred:", str(e))
        return hosted_urls
