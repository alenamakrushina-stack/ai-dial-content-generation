import asyncio
import base64
from datetime import datetime
from typing import List
import os
import dotenv
from task._models.custom_content import Attachment
from task._utils.constants import API_KEY, DIAL_URL, DIAL_CHAT_COMPLETIONS_ENDPOINT
from task._utils.bucket_client import DialBucketClient
from task._utils.model_client import DialModelClient
from task._models.message import Message
from task._models.role import Role

dotenv.load_dotenv()
API_KEY = os.getenv("DIAL_API_KEY")

content_prompt="Sunny day in Malaga with logo of DialX"

class Size:
    """
    The size of the generated image.
    """
    square: str = '1024x1024'
    height_rectangle: str = '1024x1792'
    width_rectangle: str = '1792x1024'


class Style:
    """
    The style of the generated image. Must be one of vivid or natural.
     - Vivid causes the model to lean towards generating hyper-real and dramatic images.
     - Natural causes the model to produce more natural, less hyper-real looking images.
    """
    natural: str = "natural"
    vivid: str = "vivid"


class Quality:
    """
    The quality of the image that will be generated.
     - ‘hd’ creates images with finer details and greater consistency across the image.
    """
    standard: str = "standard"
    hd: str = "hd"

async def _save_images(attachments: List[Attachment]):
    # TODO:
    #  1. Create DIAL bucket client
    #  2. Iterate through Images from attachments, download them and then save here
    #  3. Print confirmation that image has been saved locally
    async with DialBucketClient(API_KEY, DIAL_URL) as dial_bucket_client:
        for i, attachment in enumerate(attachments):
            # Determine file extension from mime type
            extension = ".png"  # default
            if attachment.type:
                if "jpeg" in attachment.type or "jpg" in attachment.type:
                    extension = ".jpg"
                elif "png" in attachment.type:
                    extension = ".png"
                elif "webp" in attachment.type:
                    extension = ".webp"
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_image_{timestamp}_{i}{extension}"
            
            # Get image bytes - either from URL or from inline data
            if attachment.url:
                # Image is stored in bucket, download it
                image_bytes = await dial_bucket_client.get_file(attachment.url)
            elif attachment.data:
                # Image is inline as base64 data
                # Remove data URL prefix if present (e.g., "data:image/png;base64,")
                data_str = attachment.data
                if ',' in data_str and data_str.startswith('data:'):
                    # Strip the data URL prefix
                    data_str = data_str.split(',', 1)[1]
                
                # Decode base64
                try:
                    image_bytes = base64.b64decode(data_str)
                except Exception as e:
                    print(f"⚠️ Skipping attachment {i}: Failed to decode base64 - {e}")
                    continue
            else:
                print(f"⚠️ Skipping attachment {i}: No URL or data found")
                continue
            
            with open(filename, "wb") as image_file:
                image_file.write(image_bytes)
            print(f"✅ Saved: {filename}")
        print(f"✅ All images have been saved locally")


def start() -> None:
    # TODO:
    #  1. Create DialModelClient
    #  2. Generate image for "Sunny day on Bali"
    #  3. Get attachments from response and save generated message (use method `_save_images`)
    #  4. Try to configure the picture for output via `custom_fields` parameter.
    #    - Documentation: See `custom_fields`. https://dialx.ai/dial_api#operation/sendChatCompletionRequest
    #  5. Test it with the 'imagegeneration@005' (Google image generation model)
    
    # Note: Size, Style, Quality are OpenAI DALL-E parameters and don't work with Google's imagegeneration@005
    # To use those parameters, switch to a DALL-E model like "dall-e-3"
    
    # # Option 1: Using Google's image generation model (no custom_fields needed)
    # dial_model_client = DialModelClient(DIAL_CHAT_COMPLETIONS_ENDPOINT, "imagegeneration@005", API_KEY)
    # message = Message(role=Role.USER, content=content_prompt)
    # response = dial_model_client.get_completion(messages=[message])
    
    # Option 2: Using DALL-E 3 with custom_fields (uncomment to use):
    dial_model_client = DialModelClient(DIAL_CHAT_COMPLETIONS_ENDPOINT, "dall-e-3", API_KEY)
    message = Message(role=Role.USER, content=content_prompt)
    response = dial_model_client.get_completion(
        messages=[message],
        custom_fields={"size": Size.square, "style": Style.vivid, "quality": Quality.hd}
    )
    
    if response.custom_content and response.custom_content.attachments:
        asyncio.run(_save_images(response.custom_content.attachments))
        print(f"Generated {len(response.custom_content.attachments)} image(s)")
    else:
        print("No images were generated in the response")


start()
