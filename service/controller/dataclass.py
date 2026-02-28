from dataclasses import dataclass
from enum import Enum


class CaptureSampleRate(Enum):
    """广播信号采样率设置"""

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


class CaptureChannel(Enum):
    """广播信号声道设置"""

    Mono = 1
    """设置采集单声道广播"""

    Stereo = 2
    """设置采集立体声广播"""


class CaptureDtype(Enum):
    """广播信号位数设置"""

    Bit16 = "int16"
    """16位深"""

    Bit24 = "int24"
    """24位深"""

    Bit32 = "int32"
    """32位深"""


class CaptureBlockSize(Enum):
    """广播信号数据包大小设置"""

    B1024 = 1024
    """最小1024字节"""

    B2048 = 2048
    """最小2048字节"""

    B4096 = 4096
    """最小4096字节"""

    B8192 = 8192
    """最小8192字节"""


@dataclass
class CaptureConfig:
    """广播信号采集配置"""

    device: int
    """采集源"""

    maxsize: int = 256
    """最大数目"""

    blocksize: CaptureBlockSize = CaptureBlockSize.B2048
    """数据包大小"""

    channel: CaptureChannel = CaptureChannel.Mono
    """声道模式"""

    dtype: CaptureDtype = CaptureDtype.Bit16
    """位数"""

    samplerate: CaptureSampleRate = CaptureSampleRate.R44100
    """采样率"""
