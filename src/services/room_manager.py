"""房间管理服务 - 管理聊天室和消息"""

import json
import os
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import threading


class RoomManager:
    """房间管理器 - 使用文件存储共享房间数据"""
    
    def __init__(self, storage_dir: str = "room_data"):
        """初始化房间管理器
        
        Args:
            storage_dir: 存储目录
        """
        self.storage_dir = storage_dir
        self.lock = threading.Lock()
        
        # 确保存储目录存在
        os.makedirs(storage_dir, exist_ok=True)
    
    def _get_room_file(self, room_id: str) -> str:
        """获取房间文件路径"""
        return os.path.join(self.storage_dir, f"room_{room_id}.json")
    
    def create_room(self, room_id: str, room_language: str = "zh", creator_username: Optional[str] = None, creator_user_language: Optional[str] = None) -> tuple[bool, Optional[str], Optional[str]]:
        """创建房间
        
        Args:
            room_id: 房间ID
            room_language: 房间默认语言
            creator_username: 创建者用户名（会自动加入房间）
            creator_user_language: 创建者选择的语言
            
        Returns:
            (是否创建成功, 状态信息, 错误信息)
            状态信息: "created" - 新创建, "exists" - 已存在, "already_member" - 已是成员
        """
        room_file = self._get_room_file(room_id)
        
        with self.lock:
            if os.path.exists(room_file):
                # 房间已存在，检查用户是否已在参与者列表中
                with open(room_file, 'r', encoding='utf-8') as f:
                    room_data = json.load(f)
                
                # 检查参与者列表（可能是旧格式字符串列表或新格式字典列表）
                participants = room_data.get("participants", [])
                participant_names = [p if isinstance(p, str) else p.get("username", "") for p in participants]
                
                if creator_username and creator_username in participant_names:
                    return False, "already_member", "您已在该房间中"
                else:
                    return False, "exists", "房间已存在"
            
            # 初始化参与者列表（新格式：字典列表）
            participants = []
            if creator_username:
                participants.append({
                    "username": creator_username,
                    "user_language": creator_user_language or room_language
                })
            
            room_data = {
                "room_id": room_id,
                "room_language": room_language,
                "creator": creator_username,  # 创建者（管理员）
                "participants": participants,
                "messages": [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat()  # 最后活动时间
            }
            
            with open(room_file, 'w', encoding='utf-8') as f:
                json.dump(room_data, f, ensure_ascii=False, indent=2)
            
            return True, "created", None
    
    def check_username_available(self, room_id: str, username: str) -> tuple[bool, Optional[str]]:
        """检查用户名在房间中是否可用
        
        Args:
            room_id: 房间ID
            username: 用户名
            
        Returns:
            (是否可用, 错误信息)
        """
        room_file = self._get_room_file(room_id)
        
        with self.lock:
            if not os.path.exists(room_file):
                return True, None  # 房间不存在，用户名可用
            
            with open(room_file, 'r', encoding='utf-8') as f:
                room_data = json.load(f)
            
            participants = room_data.get("participants", [])
            # 兼容旧格式
            if participants and isinstance(participants[0], str):
                participants = [{"username": p, "user_language": room_data.get("room_language", "zh")} for p in participants]
            
            # 检查用户名是否已存在
            participant_names = [p.get("username", "") if isinstance(p, dict) else p for p in participants]
            if username in participant_names:
                return False, f"用户名 '{username}' 已存在于该房间中，请修改用户名后再加入"
            
            return True, None
    
    def join_room(self, room_id: str, username: str, user_language: Optional[str] = None) -> tuple[bool, Optional[str]]:
        """加入房间
        
        Args:
            room_id: 房间ID
            username: 用户名
            user_language: 用户选择的语言
            
        Returns:
            (是否加入成功, 错误信息)
        """
        # 先检查用户名是否可用
        available, error_msg = self.check_username_available(room_id, username)
        if not available:
            return False, error_msg
        
        room_file = self._get_room_file(room_id)
        
        with self.lock:
            if not os.path.exists(room_file):
                return False, "房间不存在"  # 房间不存在
            
            with open(room_file, 'r', encoding='utf-8') as f:
                room_data = json.load(f)
            
            # 兼容旧格式：如果participants是字符串列表，转换为新格式
            participants = room_data.get("participants", [])
            if participants and isinstance(participants[0], str):
                # 旧格式，转换为新格式
                participants = [{"username": p, "user_language": room_data.get("room_language", "zh")} for p in participants]
                room_data["participants"] = participants
            
            # 再次检查（双重保险）
            participant_names = [p.get("username", "") if isinstance(p, dict) else p for p in participants]
            if username in participant_names:
                return False, f"用户名 '{username}' 已存在于房间中，请使用不同的用户名"
            
            # 添加新参与者（新格式）
            participants.append({
                "username": username,
                "user_language": user_language or room_data.get("room_language", "zh")
            })
            room_data["participants"] = participants
            room_data["updated_at"] = datetime.now().isoformat()
            
            # 添加系统消息，通知其他参与者有新成员加入
            join_time = datetime.now()
            time_str = join_time.strftime("%H:%M:%S")  # 格式：几点几分几秒
            system_message = {
                "type": "system",
                "event": "user_joined",
                "username": username,
                "timestamp": join_time.isoformat(),
                "time_str": time_str
            }
            room_data["messages"].append(system_message)
            room_data["last_activity"] = join_time.isoformat()  # 更新最后活动时间
            
            with open(room_file, 'w', encoding='utf-8') as f:
                json.dump(room_data, f, ensure_ascii=False, indent=2)
            
            return True, None
    
    def update_participant_language(self, room_id: str, username: str, user_language: str) -> bool:
        """更新参与者的语言设置
        
        Args:
            room_id: 房间ID
            username: 用户名
            user_language: 用户选择的语言
            
        Returns:
            是否更新成功
        """
        room_file = self._get_room_file(room_id)
        
        with self.lock:
            if not os.path.exists(room_file):
                return False
            
            with open(room_file, 'r', encoding='utf-8') as f:
                room_data = json.load(f)
            
            participants = room_data.get("participants", [])
            # 兼容旧格式
            if participants and isinstance(participants[0], str):
                participants = [{"username": p, "user_language": room_data.get("room_language", "zh")} for p in participants]
            
            # 更新参与者的语言
            for p in participants:
                if isinstance(p, dict) and p.get("username") == username:
                    p["user_language"] = user_language
                    break
            
            room_data["participants"] = participants
            room_data["updated_at"] = datetime.now().isoformat()
            
            with open(room_file, 'w', encoding='utf-8') as f:
                json.dump(room_data, f, ensure_ascii=False, indent=2)
            
            return True
    
    def leave_room(self, room_id: str, username: str) -> bool:
        """离开房间
        
        Args:
            room_id: 房间ID
            username: 用户名
            
        Returns:
            是否离开成功
        """
        room_file = self._get_room_file(room_id)
        
        with self.lock:
            if not os.path.exists(room_file):
                return False  # 房间不存在
            
            with open(room_file, 'r', encoding='utf-8') as f:
                room_data = json.load(f)
            
            participants = room_data.get("participants", [])
            # 兼容旧格式
            if participants and isinstance(participants[0], str):
                participants = [{"username": p, "user_language": room_data.get("room_language", "zh")} for p in participants]
            
            # 移除参与者
            participants = [p for p in participants if (isinstance(p, dict) and p.get("username") != username) or (isinstance(p, str) and p != username)]
            room_data["participants"] = participants
            room_data["updated_at"] = datetime.now().isoformat()
            
            with open(room_file, 'w', encoding='utf-8') as f:
                json.dump(room_data, f, ensure_ascii=False, indent=2)
            
            return True
    
    def get_room(self, room_id: str) -> Optional[Dict]:
        """获取房间信息
        
        Args:
            room_id: 房间ID
            
        Returns:
            房间数据，如果不存在返回None
        """
        room_file = self._get_room_file(room_id)
        
        with self.lock:
            if not os.path.exists(room_file):
                return None
            
            with open(room_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    def add_message(self, room_id: str, user: str, original_text: str, translated_text: Optional[str] = None, original_lang: Optional[str] = None) -> bool:
        """添加消息到房间
        
        Args:
            room_id: 房间ID
            user: 用户名
            original_text: 原始消息内容
            translated_text: 翻译后的消息内容（可选）
            original_lang: 原始语言（可选）
            
        Returns:
            是否添加成功
        """
        room_file = self._get_room_file(room_id)
        
        with self.lock:
            if not os.path.exists(room_file):
                return False
            
            with open(room_file, 'r', encoding='utf-8') as f:
                room_data = json.load(f)
            
            message = {
                "user": user,
                "original_text": original_text,
                "translated_text": translated_text,
                "original_lang": original_lang,
                "timestamp": datetime.now().isoformat()
            }
            
            room_data["messages"].append(message)
            room_data["updated_at"] = datetime.now().isoformat()
            room_data["last_activity"] = datetime.now().isoformat()  # 更新最后活动时间
            
            # 立即写入文件，确保消息及时保存
            with open(room_file, 'w', encoding='utf-8') as f:
                json.dump(room_data, f, ensure_ascii=False, indent=2)
                # 强制刷新文件系统缓存（确保其他进程能立即看到更新）
                try:
                    f.flush()  # 先刷新Python缓冲区
                    os.fsync(f.fileno())  # 再刷新操作系统缓冲区
                except:
                    pass
            
            return True
    
    def get_messages(self, room_id: str, since: Optional[str] = None) -> List[Dict]:
        """获取房间消息
        
        Args:
            room_id: 房间ID
            since: 获取此时间之后的消息（ISO格式）
            
        Returns:
            消息列表
        """
        room_data = self.get_room(room_id)
        if not room_data:
            return []
        
        messages = room_data.get("messages", [])
        
        if since:
            # 过滤时间
            messages = [msg for msg in messages if msg.get("timestamp", "") > since]
        
        return messages
    
    def update_room_language(self, room_id: str, language: str) -> bool:
        """更新房间语言
        
        Args:
            room_id: 房间ID
            language: 新语言
            
        Returns:
            是否更新成功
        """
        room_file = self._get_room_file(room_id)
        
        with self.lock:
            if not os.path.exists(room_file):
                return False
            
            with open(room_file, 'r', encoding='utf-8') as f:
                room_data = json.load(f)
            
            room_data["room_language"] = language
            room_data["updated_at"] = datetime.now().isoformat()
            
            with open(room_file, 'w', encoding='utf-8') as f:
                json.dump(room_data, f, ensure_ascii=False, indent=2)
            
            return True
    
    def is_creator(self, room_id: str, username: str) -> bool:
        """检查用户是否为房间创建者（管理员）
        
        Args:
            room_id: 房间ID
            username: 用户名
            
        Returns:
            是否为创建者
        """
        room_data = self.get_room(room_id)
        if not room_data:
            return False
        
        return room_data.get("creator") == username
    
    def delete_room(self, room_id: str, username: str) -> tuple[bool, Optional[str]]:
        """删除房间（仅创建者可以删除）
        
        Args:
            room_id: 房间ID
            username: 用户名（必须是创建者）
            
        Returns:
            (是否成功, 错误信息)
        """
        if not self.is_creator(room_id, username):
            return False, "只有房间创建者才能删除房间"
        
        room_file = self._get_room_file(room_id)
        
        with self.lock:
            if os.path.exists(room_file):
                os.remove(room_file)
                return True, None
            else:
                return False, "房间不存在"
    
    def remove_participant(self, room_id: str, target_username: str, admin_username: str) -> tuple[bool, Optional[str]]:
        """移除参与者（仅创建者可以移除）
        
        Args:
            room_id: 房间ID
            target_username: 要移除的用户名
            admin_username: 管理员用户名（必须是创建者）
            
        Returns:
            (是否成功, 错误信息)
        """
        if not self.is_creator(room_id, admin_username):
            return False, "只有房间创建者才能移除参与者"
        
        room_file = self._get_room_file(room_id)
        
        with self.lock:
            if not os.path.exists(room_file):
                return False, "房间不存在"
            
            with open(room_file, 'r', encoding='utf-8') as f:
                room_data = json.load(f)
            
            # 不能移除创建者自己
            if target_username == admin_username:
                return False, "不能移除房间创建者"
            
            participants = room_data.get("participants", [])
            # 兼容旧格式
            if participants and isinstance(participants[0], str):
                participants = [{"username": p, "user_language": room_data.get("room_language", "zh")} for p in participants]
            
            # 移除目标用户
            original_count = len(participants)
            participants = [p for p in participants if not (isinstance(p, dict) and p.get("username") == target_username)]
            
            if len(participants) == original_count:
                return False, "用户不在参与者列表中"
            
            room_data["participants"] = participants
            room_data["updated_at"] = datetime.now().isoformat()
            room_data["last_activity"] = datetime.now().isoformat()
            
            with open(room_file, 'w', encoding='utf-8') as f:
                json.dump(room_data, f, ensure_ascii=False, indent=2)
            
            return True, None
    
    def check_and_cleanup_inactive_rooms(self, inactivity_hours: float = 1.0) -> List[str]:
        """检查并清理长时间无活动的房间（默认1小时）
        
        Args:
            inactivity_hours: 无活动小时数
            
        Returns:
            被删除的房间ID列表
        """
        deleted_rooms = []
        threshold_time = datetime.now() - timedelta(hours=inactivity_hours)
        
        with self.lock:
            # 遍历所有房间文件
            if not os.path.exists(self.storage_dir):
                return deleted_rooms
            
            for filename in os.listdir(self.storage_dir):
                if filename.startswith("room_") and filename.endswith(".json"):
                    room_file = os.path.join(self.storage_dir, filename)
                    try:
                        with open(room_file, 'r', encoding='utf-8') as f:
                            room_data = json.load(f)
                        
                        last_activity_str = room_data.get("last_activity")
                        if last_activity_str:
                            last_activity = datetime.fromisoformat(last_activity_str)
                            if last_activity < threshold_time:
                                # 房间长时间无活动，删除
                                room_id = room_data.get("room_id")
                                os.remove(room_file)
                                deleted_rooms.append(room_id)
                    except Exception:
                        # 如果读取文件出错，跳过
                        continue
        
        return deleted_rooms
    
    def update_activity(self, room_id: str):
        """更新房间活动时间（当有消息或其他活动时调用）
        
        Args:
            room_id: 房间ID
        """
        room_file = self._get_room_file(room_id)
        
        with self.lock:
            if os.path.exists(room_file):
                with open(room_file, 'r', encoding='utf-8') as f:
                    room_data = json.load(f)
                
                room_data["last_activity"] = datetime.now().isoformat()
                room_data["updated_at"] = datetime.now().isoformat()
                
                with open(room_file, 'w', encoding='utf-8') as f:
                    json.dump(room_data, f, ensure_ascii=False, indent=2)
    
    def list_rooms(self) -> List[Dict]:
        """获取所有房间列表
        
        Returns:
            房间列表，每个房间包含基本信息（room_id, creator, room_language, participant_count, created_at, last_activity）
        """
        rooms = []
        
        with self.lock:
            if not os.path.exists(self.storage_dir):
                return rooms
            
            for filename in os.listdir(self.storage_dir):
                if filename.startswith("room_") and filename.endswith(".json"):
                    room_file = os.path.join(self.storage_dir, filename)
                    try:
                        with open(room_file, 'r', encoding='utf-8') as f:
                            room_data = json.load(f)
                        
                        # 提取房间基本信息
                        room_id = room_data.get("room_id")
                        if not room_id:
                            # 从文件名提取room_id
                            room_id = filename.replace("room_", "").replace(".json", "")
                        
                        participants = room_data.get("participants", [])
                        # 兼容旧格式
                        if participants and isinstance(participants[0], str):
                            participants = [{"username": p, "user_language": room_data.get("room_language", "zh")} for p in participants]
                        
                        room_info = {
                            "room_id": room_id,
                            "creator": room_data.get("creator", "未知"),
                            "room_language": room_data.get("room_language", "zh"),
                            "participant_count": len(participants),
                            "created_at": room_data.get("created_at", ""),
                            "last_activity": room_data.get("last_activity", room_data.get("updated_at", "")),
                            "message_count": len(room_data.get("messages", []))
                        }
                        rooms.append(room_info)
                    except Exception:
                        # 如果读取文件出错，跳过
                        continue
        
        # 按最后活动时间排序（最新的在前）
        rooms.sort(key=lambda x: x.get("last_activity", ""), reverse=True)
        return rooms


# 全局房间管理器实例
_room_manager: Optional[RoomManager] = None


def get_room_manager() -> RoomManager:
    """获取房间管理器实例（单例）"""
    global _room_manager
    if _room_manager is None:
        _room_manager = RoomManager()
    return _room_manager
