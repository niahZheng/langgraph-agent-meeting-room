"""服务模块"""

from .speech_recognition import SpeechRecognitionService
from .translation import TranslationService
from .room_manager import RoomManager, get_room_manager

__all__ = ["SpeechRecognitionService", "TranslationService", "RoomManager", "get_room_manager"]
