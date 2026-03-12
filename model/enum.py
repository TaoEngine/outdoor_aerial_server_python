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
