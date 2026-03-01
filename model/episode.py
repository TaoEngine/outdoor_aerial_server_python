from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Episode:
    """单期电台节目数据类型"""

    program: bytes
    """本期节目隶属电台节目的 uuid 用于反查电台节目"""

    uuid: bytes
    """本期节目的 uuid"""

    cover: bytes
    """本期节目的配图 通过 AI 结合这期节目的主题生成的配图 用于主页卡片的展示"""

    title: str
    """本期节目的主题 利用 AI 分析节目音频片段给出的本期节目主题"""

    abstract: str
    """本期节目的摘要 利用 AI 分析节目音频片段给出的本期节目摘要"""

    favorite: bool
    """用户是否收藏本期节目"""

    time: datetime
    """本期节目的具体播出时间"""
