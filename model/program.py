from datetime import time

from msgspec import Struct

from model.enum import ProgramStatus, ProgramType, ProgramWeekday


class Program(Struct, frozen=True):
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
