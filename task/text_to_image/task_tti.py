import asyncio
from datetime import datetime

from task._models.custom_content import Attachment
from task._utils.constants import API_KEY, DIAL_URL, DIAL_CHAT_COMPLETIONS_ENDPOINT
from task._utils.bucket_client import DialBucketClient
from task._utils.model_client import DialModelClient
from task._models.message import Message
from task._models.role import Role

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

async def _save_images(attachments: list[Attachment]):
    # TODO:
    #  1. Create DIAL bucket client
    #  2. Iterate through Images from attachments, download them and then save here
    #  3. Print confirmation that image has been saved locally
    dial_bucket_client = DialBucketClient(API_KEY, DIAL_URL)
    for attachment in attachments:
        image_bytes = dial_bucket_client.get_file(attachment.url)
        with open(attachment.title, "wb") as image_file:
            image_file.write(image_bytes)
    print(f"Images have been saved locally")


def start() -> None:
    # TODO:
    #  1. Create DialModelClient
    #  2. Generate image for "Sunny day on Bali"
    #  3. Get attachments from response and save generated message (use method `_save_images`)
    #  4. Try to configure the picture for output via `custom_fields` parameter.
    #    - Documentation: See `custom_fields`. https://dialx.ai/dial_api#operation/sendChatCompletionRequest
    #  5. Test it with the 'imagegeneration@005' (Google image generation model)
    dial_model_client = DialModelClient(API_KEY, DIAL_URL)
    response = dial_model_client.images.generate(
        model="imagegeneration@005",
        prompt="Sunny day on Bali",
        custom_fields={"size": Size.square, "style": Style.natural, "quality": Quality.hd},
    )
    attachments = response.data
    _save_images(attachments)


start()
