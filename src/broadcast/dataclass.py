from dataclasses import dataclass
from enum import Enum


class BroadcastSampleRate(Enum):
    """广播采集采样率设置"""

    R16000 = 16000
    """16000Hz"""

    R22050 = 22050
    """22050Hz"""

    R44100 = 44100
    """44100Hz"""

    R48000 = 48000
    """48000Hz"""

    R88200 = 88200
    """88200Hz"""

    R96000 = 96000
    """96000Hz"""

    R176400 = 176400
    """176400Hz"""

    R192000 = 192000
    """192000Hz"""


class BroadcastChannel(Enum):
    """广播采集声道设置"""

    Mono = 1
    """设置采集单声道广播"""

    Stereo = 2
    """设置采集立体声广播"""


class BroadcastDtype(Enum):
    """广播采集位数设置"""

    Bit16 = "int16"
    """16位深"""

    # Bit24 = "int24"
    # """24位深"""

    Bit32 = "int32"
    """32位深"""


class BroadcastBlockSize(Enum):
    """广播采集数据包大小设置"""

    B1024 = 1024
    """最小1024字节"""

    B2048 = 2048
    """最小2048字节"""

    B4096 = 4096
    """最小4096字节"""

    B8192 = 8192
    """最小8192字节"""


@dataclass
class BroadcastConfig:
    """广播采集配置"""

    device: int
    """广播采集源"""

    blocksize: BroadcastBlockSize = BroadcastBlockSize.B2048
    """广播采集数据包大小"""

    channel: BroadcastChannel = BroadcastChannel.Mono
    """广播采集声道"""

    dtype: BroadcastDtype = BroadcastDtype.Bit16
    """广播采集位数"""

    maxsize: int = 256
    """广播采集队列最大数目"""

    samplerate: BroadcastSampleRate = BroadcastSampleRate.R44100
    """广播采集采样率"""
