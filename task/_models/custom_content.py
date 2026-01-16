from dataclasses import dataclass
from typing import Optional, Dict, List


@dataclass
class Attachment:
    title: Optional[str] = None
    data: Optional[str] = None
    type: Optional[str] = None
    url: Optional[str] = None

    def to_dict(self) -> Dict[str, Optional[str]]:
        return {
            "title": self.title,
            "data": self.data,
            "type": self.type,
            "url": self.url
        }


@dataclass
class CustomContent:
    attachments: List[Attachment]

    def to_dict(self) -> Dict[str, List[dict]]:
        return {
            "attachments": [attachment.to_dict() for attachment in self.attachments]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CustomContent":
        attachments = []
        if attachment_data := data.get("attachments"):
            if isinstance(attachment_data, list):
                attachments = [
                    Attachment(**{k: v for k, v in attachment.items()
                                  if k in ["title", "data", "type", "url"]})
                    for attachment in attachment_data
                ]
        return cls(attachments=attachments)
