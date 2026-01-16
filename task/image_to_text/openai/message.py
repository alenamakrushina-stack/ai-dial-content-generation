from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Union

from task._models.custom_content import CustomContent
from task._models.message import Message
from task._models.role import Role

class ContentType(str, Enum):
    IMAGE = "image_url"
    TEXT = "text"

@dataclass
class ImgUrl:
    url: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url
        }

@dataclass
class ImgContent:
    image_url: ImgUrl
    type: ContentType = ContentType.IMAGE

    def to_dict(self) -> Dict[str, Any]:
        return {
            "image_url": self.image_url.to_dict(),
            "type": self.type.value
        }


@dataclass
class TxtContent:
    text: str
    type: ContentType = ContentType.TEXT

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "type": self.type.value
        }


@dataclass
class ContentedMessage(Message):
    content: List[Union[ImgContent, TxtContent]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role.value,
            "content": [content.to_dict() for content in self.content]
        }