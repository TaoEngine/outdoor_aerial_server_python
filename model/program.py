from dataclasses import dataclass
from datetime import time
from enum import Enum


class ProgramType(Enum):
    """电台节目的类型"""

    INTEGRATE = 0
    """综合节目 包含不止一个分类的节目"""

    NEWS = 1
    """新闻节目 聚焦时事与政治的国际新闻省市新闻或本地新闻"""

    MUSIC = 2
    """音乐节目 对音乐进行点评或者仅持续播放音乐"""

    PODCAST = 3
    """播客节目 邀请嘉宾进行深度访谈或者长时间话题延申"""

    ENTERTAINMENT = 4
    """娱乐节目 交流趣事讨论八卦并且主持人持续与听众进行互动"""

    SPORTS = 5
    """体育节目 报道实况比赛或者分析赛点事件"""

    STORYTELLING = 6
    """广播剧节目 音频小说评书广播剧"""

    EDUCATIONAL = 7
    """教育节目 谈论家庭教育或孩子的心理问题以及教育讲座录播"""

    FINANCE = 8
    """财经节目 解析今日股市或投资建议"""

    HEALTH = 9
    """健康节目 交流健身运动或养生知识"""


class ProgramStatus(Enum):
    """电台节目的播出状态"""

    LIVE = 0
    """开播的节目"""

    REPLAY = 1
    """重播的节目"""

    SUSPENDED = 2
    """暂播的节目"""


class ProgramWeekday(Enum):
    """电台节目的播出日期"""

    MONDAY = 0
    """周一"""

    TUESDAY = 1
    """周二"""

    WEDNESDAY = 2
    """周三"""

    THURSDAY = 3
    """周四"""

    FRIDAY = 4
    """周五"""

    SATURDAY = 5
    """周六"""

    SUNDAY = 6
    """周日"""


@dataclass(frozen=True, slots=True)
class Program:
    """电台节目数据类型"""

    studio: bytes
    """该电台节目隶属广播电台的 uuid 用于反查广播电台"""

    uuid: bytes
    """该电台节目的 uuid"""

    name: str
    """该电台节目的名称 比如心花一路FUN"""

    description: str | None
    """对该电台节目的长文本介绍 接受没有介绍的电台节目"""

    type: ProgramType
    """该电台节目的类型"""

    status: ProgramStatus
    """该电台节目的播出状态"""

    hosts: list[str] | None
    """该电台节目的主持人阵容 比如晏大胖 支持多位主持人 接受无主持人"""

    like: bool
    """用户是否喜欢该电台节目 这是作为录制每期节目的依据"""

    block: bool
    """用户是否屏蔽该电台节目 节目将被拉黑并在应用中消失"""

    date: list[ProgramWeekday]
    """该电台节目的播出日期"""

    start: time
    """该电台节目的播出时间"""

    end: time
    """该电台节目的结束时间"""
