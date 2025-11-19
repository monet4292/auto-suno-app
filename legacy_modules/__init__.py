"""
Legacy Modules - Core modules từ v1.0 vẫn đang được sử dụng
"""
from .suno_auto_create import SunoMusicCreator, SunoCreateConfig
from .suno_batch_download import SunoBatchDownloader

__all__ = [
    'SunoMusicCreator',
    'SunoCreateConfig', 
    'SunoBatchDownloader'
]
