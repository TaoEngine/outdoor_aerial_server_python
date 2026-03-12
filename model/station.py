from datetime import time

from msgspec import Struct
from yarl import URL

from model.enum import StationStatus, StationType


class Station(Struct, frozen=True):
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
    """广播电台的播音开始时间"""

    end: time
    """广播电台的播音结束时间"""
