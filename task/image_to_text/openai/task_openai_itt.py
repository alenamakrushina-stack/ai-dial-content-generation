import base64
from pathlib import Path

import os
import dotenv

from task._utils.constants import DIAL_CHAT_COMPLETIONS_ENDPOINT
from task._utils.model_client import DialModelClient
from task._models.role import Role
from task._models.message import Message
from task.image_to_text.openai.message import ContentedMessage, TxtContent, ImgContent, ImgUrl

dotenv.load_dotenv()
API_KEY = os.getenv("DIAL_API_KEY")

def start() -> None:
    # Debug: Check if API key is loaded
    if not API_KEY or API_KEY.strip() == "":
        print("❌ ERROR: DIAL_API_KEY not found!")
        print("Please ensure:")
        print("  1. You have a .env file in the project root")
        print("  2. It contains: DIAL_API_KEY=your_actual_key")
        print("  3. You're connected to EPAM VPN")
        return
    print(f"✅ API Key loaded: {API_KEY[:8]}...{API_KEY[-4:]}")
    
    project_root = Path(__file__).parent.parent.parent.parent
    image_path = project_root / "dialx-banner.png"

    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()
    base64_image = base64.b64encode(image_bytes).decode('utf-8')

    client = DialModelClient(
        endpoint=DIAL_CHAT_COMPLETIONS_ENDPOINT,
        deployment_name="gpt-4o",
        api_key=API_KEY
    )
    
    # Create system message
    system_message = Message(role=Role.SYSTEM, content="You are a helpful assistant.")
    
    # ============================================================
    # Try 1: Using URL to analyze an external image
    # ============================================================
    print("\n" + "="*60)
    print("🌐 TRY 1: Analyzing image from URL")
    print("="*60)
    
    user_message_url = ContentedMessage(
        role=Role.USER,
        content=[
            TxtContent(text="What do you see in this image? Describe it in detail."),
            ImgContent(image_url=ImgUrl(url="https://a-z-animals.com/media/2019/11/Elephant-male-1024x535.jpg"))
        ]
    )
    
    response_url = client.get_completion(messages=[system_message, user_message_url])
    print("\n📄 Response:")
    print(response_url.content)
    
    # ============================================================
    # Try 2: Using base64 encoded local image
    # ============================================================
    print("\n" + "="*60)
    print("🖼️  TRY 2: Analyzing base64 encoded local image (dialx-banner.png)")
    print("="*60)
    
    base64_data_url = f"data:image/png;base64,{base64_image}"
    user_message_base64 = ContentedMessage(
        role=Role.USER,
        content=[
            TxtContent(text="What do you see in this image? Describe it in detail."),
            ImgContent(image_url=ImgUrl(url=base64_data_url))
        ]
    )
    
    response_base64 = client.get_completion(messages=[system_message, user_message_base64])
    print("\n📄 Response:")
    print(response_base64.content)


    # TODO:
    #  1. Create DialModelClient
    #  2. Call client to analise image:
    #    - try with base64 encoded format
    #    - try with URL: https://a-z-animals.com/media/2019/11/Elephant-male-1024x535.jpg
    #  ----------------------------------------------------------------------------------------------------------------
    #  Note: This approach embeds the image directly in the message as base64 data URL! Here we follow the OpenAI
    #        Specification but since requests are going to the DIAL Core, we can use different models and DIAL Core
    #        will adapt them to format Gemini or Anthropic is using. In case if we go directly to
    #        the https://api.anthropic.com/v1/complete we need to follow Anthropic request Specification (the same for gemini)
    


start()