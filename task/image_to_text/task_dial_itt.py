import asyncio
import base64
from io import BytesIO
from pathlib import Path

import os
import dotenv
from task._models.custom_content import Attachment, CustomContent
from task._utils.constants import API_KEY, DIAL_URL, DIAL_CHAT_COMPLETIONS_ENDPOINT
from task._utils.bucket_client import DialBucketClient
from task._utils.model_client import DialModelClient
from task._models.message import Message
from task._models.role import Role

dotenv.load_dotenv()
API_KEY = os.getenv("DIAL_API_KEY")

async def _put_image() -> Attachment:
    file_name = 'dialx-banner.png'
    image_path = Path(__file__).parent.parent.parent / file_name
    mime_type_png = 'image/png'
    # TODO:
    #  1. Create DialBucketClient
    #  2. Open image file
    #  3. Use BytesIO to load bytes of image
    #  4. Upload file with client
    #  5. Return Attachment object with title (file name), url and type (mime type)
    async with DialBucketClient(API_KEY, DIAL_URL) as dial_bucket_client:
        with open(image_path, "rb") as image_file:
            image_bytes = image_file.read()
        response = await dial_bucket_client.put_file(file_name, mime_type_png, BytesIO(image_bytes))
        attachment = Attachment(title=file_name, url=response.get("url"), type=mime_type_png)
        return attachment


def start() -> None:
    if not API_KEY or API_KEY.strip() == "":
        print("❌ ERROR: DIAL_API_KEY not found!")
        print("Please ensure:")
        print("  1. You have a .env file in the project root")
        print("  2. It contains: DIAL_API_KEY=your_actual_key")
        print("  3. You're connected to EPAM VPN")
        return
        print(f"✅ API Key loaded: {API_KEY[:8]}...{API_KEY[-4:]}")
    
    # TODO:
    #  1. Create DialModelClient
    #  2. Upload image (use `_put_image` method )
    #  3. Print attachment to see result
    #  4. Call chat completion via client with list containing one Message:
    #    - role: Role.USER
    #    - content: "What do you see on this picture?"
    #    - custom_content: CustomContent(attachments=[attachment])
    #  ---------------------------------------------------------------------------------------------------------------
    #  Note: This approach uploads the image to DIAL bucket and references it via attachment. The key benefit of this
    #        approach that we can use Models from different vendors (OpenAI, Google, Anthropic). The DIAL Core
    #        adapts this attachment to Message content in appropriate format for Model.
    #  TRY THIS APPROACH WITH DIFFERENT MODELS!
    #  Optional: Try upload 2+ pictures for analysis
    dial_model_client = DialModelClient(DIAL_CHAT_COMPLETIONS_ENDPOINT, "gpt-4o", API_KEY)
    attachment = asyncio.run(_put_image())
    print(f"Attachment: {attachment}")
    message = Message(role=Role.USER, content="What do you see on this picture?", custom_content=CustomContent(attachments=[attachment]))
    response = dial_model_client.get_completion(messages=[message])
    print(response.content)


start()
