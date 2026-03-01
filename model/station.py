from dataclasses import dataclass
from datetime import time
from enum import Enum

from yarl import URL


class StationType(Enum):
    """广播电台的类型"""

    INTEGRATE = 0
    """综合台"""

    TRAFFIC = 1
    """交通台"""

    MUSIC = 2
    """音乐台"""

    NEWS = 3
    """新闻台"""

    ECONOMY = 4
    """经济台"""

    SPORTS = 5
    """体育台"""

    EDUCATIONAL = 6
    """科教台"""

    SCIENCE = 7
    """科学台"""

    INTERNATIONAL = 8
    """国际台"""

    AGRICULTURAL = 9
    """农业台"""

    CHILDREN = 10
    """少儿台"""

    HEALTH = 11
    """健康台"""


class StationStatus(Enum):
    """广播电台的播出状态"""

    BROADCASTING = 0
    """广播中"""

    MAINTENANCE = 1
    """停机检修"""

    OFFAIR = 2
    """电台停播 哭了"""


@dataclass(frozen=True, slots=True)
class RadioStation:
    """广播电台数据模型"""

    uuid: bytes
    """该广播电台的 uuid"""

    logo: bytes
    """该广播电台的 logo 用于显示在播放器专辑封面和首页中 和广播电台官方的宣发图一致 需要透明背景"""

    banner: bytes
    """该广播电台的横幅 用于标识节目卡片归属 内容从 logo 中选取非文字部分 需要透明背景"""

    frequency: float
    """该广播电台的频率 单位为兆赫兹 比如 90.8 指 90.8MHz"""

    name: str
    """该广播电台的名称 比如安徽交通广播"""

    description: str | None
    """对该广播电台的长文本介绍 接受没有介绍的广播电台"""

    type: StationType
    """该广播电台的类型"""

    status: StationStatus
    """该广播电台的播出状态"""

    institution: str
    """该广播电台所属单位 比如安徽广播电视台"""

    language: tuple[str, str]
    """该广播电台的播出语言 指定存储 ISO 标准地区代码方便解析 比如 zh_CN"""

    social: URL | None
    """该广播电台拥有的社媒账号URL 接受没有社媒的广播电台"""

    like: bool
    """用户是否喜爱该广播电台 这是作为推荐旗下节目的依据"""

    block: bool
    """用户是否屏幕该广播电台 电台将被拉黑并在应用中消失"""

    start: time
    """广播电台的开台时间"""

    end: time
    """广播电台的再见时间"""
