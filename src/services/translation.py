"""翻译服务"""

from typing import Literal, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from ..config.settings import get_model


class TranslationService:
    """翻译服务 - 使用LLM进行翻译"""
    
    def __init__(self):
        """初始化翻译服务"""
        self.model = get_model()
    
    def translate(
        self, 
        text: str, 
        source_lang: Literal["zh", "en"], 
        target_lang: Literal["zh", "en"]
    ) -> Optional[str]:
        """
        翻译文本
        
        Args:
            text: 要翻译的文本
            source_lang: 源语言 ('zh' 或 'en')
            target_lang: 目标语言 ('zh' 或 'en')
            
        Returns:
            翻译后的文本，如果源语言和目标语言相同则返回原文
        """
        if source_lang == target_lang:
            return text
        
        try:
            lang_map = {
                "zh": "中文",
                "en": "English"
            }
            
            source_lang_name = lang_map.get(source_lang, source_lang)
            target_lang_name = lang_map.get(target_lang, target_lang)
            
            system_prompt = f"""你是一个专业的翻译助手。请将用户输入的文本从{source_lang_name}翻译成{target_lang_name}。

要求：
1. 保持原文的语气和风格
2. 确保翻译准确、自然
3. 只返回翻译结果，不要添加任何解释或说明
4. 如果输入已经是目标语言，直接返回原文"""

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=text)
            ]
            
            response = self.model.invoke(messages)
            translated_text = response.content.strip()
            
            return translated_text
            
        except Exception as e:
            print(f"翻译出错: {str(e)}")
            return text  # 翻译失败时返回原文
    
    def detect_language(self, text: str) -> Literal["zh", "en"]:
        """
        检测文本语言
        
        Args:
            text: 要检测的文本
            
        Returns:
            检测到的语言 ('zh' 或 'en')
        """
        try:
            # 简单的中文检测：如果包含中文字符，认为是中文
            has_chinese = any('\u4e00' <= char <= '\u9fff' for char in text)
            return "zh" if has_chinese else "en"
        except Exception:
            return "en"  # 默认返回英文
