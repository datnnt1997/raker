from typing import Optional
from dataclasses import dataclass, field


@dataclass
class YouTubeComment:
    content: str
    _id: str = field(default=None)
    author: Optional[str] = field(default=None)
    video_id: Optional[str] = field(default=None)
    like_count: Optional[int] = field(default=None)
    reply_count: Optional[int] = field(default=None)
