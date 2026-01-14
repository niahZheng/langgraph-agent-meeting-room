# 💬 LangGraph Agent 会议聊天室系统

基于 **LangGraph** 构建的智能 Agent 会议聊天室，集成 **阿里云百炼平台** 的语音识别和语言模型服务，实现语音转录、智能翻译和多人实时协作。

## 🌟 核心亮点

### 🎯 技术特色

- **🔄 LangGraph 工作流引擎**
  - 采用 LangGraph 构建可扩展的消息处理工作流
  - 支持条件路由和状态管理，实现灵活的消息处理流程
  - 模块化节点设计，易于扩展和维护

- **🎤 阿里百炼语音识别**
  - 集成阿里云百炼平台的 `paraformer-realtime-v2` 实时语音识别模型
  - 支持多种音频格式（WAV、MP3、M4A等）
  - 高精度语音转文字，支持中英文识别

- **🌐 智能语言处理**
  - 基于阿里百炼大语言模型（Qwen）的智能翻译服务
  - 自动语言检测和上下文理解
  - 支持中英文双向翻译，保持语义准确性

- **🌍 国际化支持 (i18n)**
  - 自动检测用户浏览器语言环境
  - 支持中文和英文界面动态切换
  - 类似 i18n 的全球动态语言界面

- **👥 多人实时协作**
  - 支持多用户同时在线聊天
  - 实时消息同步和状态管理
  - 房间管理和参与者权限控制

## 🏗️ 系统架构

### LangGraph 工作流设计

系统采用 LangGraph 构建了一个智能消息处理工作流，通过状态图和条件路由实现灵活的消息处理：

```
用户输入（语音/文字）
    ↓
[入口节点 (entry)] → 智能路由判断输入类型
    ↓
    ├─→ [语音识别节点 (speech_recognition)]
    │       ↓
    │   调用阿里百炼 paraformer-realtime-v2 API
    │       ↓
    │   音频 → 文字转换
    │       ↓
    └─→ [翻译节点 (translation)]
            ↓
        语言检测（基于 Qwen 大模型）
            ↓
        智能翻译（如需要）
            ↓
    [消息处理节点 (message)]
            ↓
    格式化并保存消息
            ↓
    显示在聊天室
```

### 核心工作流节点

1. **入口节点 (entry)**
   - 根据输入类型（语音/文字）进行智能路由
   - 判断是否需要进入语音识别流程

2. **语音识别节点 (speech_recognition_node)**
   - 集成阿里百炼 `paraformer-realtime-v2` 实时语音识别模型
   - 支持 base64 编码的音频数据输入
   - 自动处理音频格式转换和 API 调用
   - 返回识别出的文字内容

3. **翻译节点 (translation_node)**
   - 使用阿里百炼 Qwen 大语言模型进行语言检测
   - 智能判断输入语言与会议室语言是否匹配
   - 自动执行翻译任务，保持语义准确性
   - 支持中英文双向翻译

4. **消息处理节点 (message_node)**
   - 格式化消息内容（包含原始文本、翻译文本、语言信息）
   - 保存到房间消息记录
   - 更新参与者状态

### 技术栈

- **LangGraph**: 工作流管理和状态图构建
- **LangChain**: LLM 集成和消息处理
- **阿里云百炼平台**:
  - `paraformer-realtime-v2`: 实时语音识别模型
  - `qwen-plus`: 大语言模型（用于翻译和语言检测）
- **Streamlit**: Web UI 框架
- **Python 3.12+**: 核心开发语言

## 📦 快速开始

### 1. 环境要求

- Python 3.12 或更高版本
- 阿里云百炼平台 API 密钥

### 2. 安装依赖

```bash
# 克隆项目
git clone <repository-url>
cd firstproject

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

创建 `.env` 文件（参考 `env.example`）：

```env
# 阿里云百炼平台 API 密钥
DASHSCOPE_API_KEY=your_dashscope_api_key_here

# 大语言模型配置
MODEL_NAME=qwen-plus
BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

**获取 API 密钥：**
1. 访问 [阿里云百炼平台](https://dashscope.console.aliyun.com/)
2. 注册/登录账号
3. 创建 API 密钥
4. 确保开通语音识别和语言模型服务权限

### 4. 启动应用

**Windows:**
```bash
run_meeting.bat
```

**Linux/Mac:**
```bash
streamlit run meeting_app.py
```

应用将在浏览器中自动打开，默认地址：`http://localhost:8501`

## 🎮 使用指南

### 1. 用户注册与登录

- 首次使用需要注册账号
- 登录后会话状态会自动保存，刷新页面不会丢失登录状态

### 2. 创建或加入房间

**创建新房间：**
1. 在侧边栏输入房间ID（例如：`meeting-001`）
2. 选择房间语言（中文/English）
3. 点击"创建或加入房间"
4. 房间创建成功后，您将成为该房间的管理员

**加入已有房间：**
1. 在"选择房间"列表中选择要加入的房间
2. 或直接输入房间ID并点击"创建或加入房间"
3. 系统会自动检测并加入房间

### 3. 发送消息

**方式一：文字输入**
1. 在输入框输入文字
2. 点击"发送文字"按钮
3. 系统会自动检测语言并进行翻译（如需要）

**方式二：语音输入**
1. 点击"点击开始录音"按钮
2. 对着麦克风说话（支持中英文）
3. 点击"发送语音"按钮
4. 系统会：
   - 调用阿里百炼语音识别 API 将音频转换为文字
   - 自动检测语言并进行翻译（如需要）
   - 显示在聊天室中

### 4. 语言设置

- **我的显示语言**：选择您希望看到的界面语言（中文/English）
- **房间语言**：设置会议室的主要语言，系统会根据此语言自动翻译消息
- 系统会自动检测您的浏览器语言并设置默认语言

### 5. 多人协作

- 所有加入同一房间的用户都可以看到彼此的消息
- 消息会实时同步到所有参与者（自动刷新功能）
- 房间创建者拥有管理员权限，可以移除其他参与者

## 📁 项目结构

```
firstproject/
├── src/
│   ├── state/
│   │   └── meeting_state.py          # LangGraph 状态定义
│   ├── services/
│   │   ├── speech_recognition.py     # 阿里百炼语音识别服务
│   │   ├── translation.py            # 基于 Qwen 的翻译服务
│   │   ├── room_manager.py           # 房间和消息管理
│   │   └── auth_service.py           # 用户认证服务
│   ├── nodes/
│   │   ├── speech_recognition_node.py # LangGraph 语音识别节点
│   │   ├── translation_node.py       # LangGraph 翻译节点
│   │   ├── message_node.py           # LangGraph 消息处理节点
│   │   └── meeting_routing.py        # 路由逻辑（条件判断）
│   ├── workflow/
│   │   └── meeting_workflow.py       # LangGraph 工作流构建
│   ├── ui/
│   │   ├── meeting_app.py            # Streamlit 主应用
│   │   ├── auth_ui.py                # 登录/注册 UI
│   │   └── state_persistence.py      # 状态持久化
│   ├── utils/
│   │   └── i18n.py                   # 国际化支持
│   └── config/
│       └── settings.py               # 配置管理
├── room_data/                        # 房间数据存储（JSON）
├── auth_data/                        # 用户和会话数据（JSON）
├── meeting_app.py                    # 应用入口
├── requirements.txt                  # Python 依赖
├── run_meeting.bat                   # Windows 启动脚本
└── README.md                         # 项目文档
```

## 🔧 核心功能详解

### LangGraph 工作流实现

系统使用 LangGraph 的 `StateGraph` 构建了一个有状态的消息处理工作流：

```python
# 工作流结构
workflow = StateGraph(MeetingState)
workflow.add_node("entry", entry_node)
workflow.add_node("speech_recognition", speech_recognition_node)
workflow.add_node("translation", translation_node)
workflow.add_node("message", message_node)

# 条件路由
workflow.add_conditional_edges("entry", should_recognize_speech, {...})
workflow.add_conditional_edges("speech_recognition", should_translate, {...})
```

### 阿里百炼语音识别集成

系统通过 `SpeechRecognitionService` 封装了阿里百炼的语音识别 API：

- **模型**: `paraformer-realtime-v2`（实时语音识别）
- **API 端点**: `https://dashscope.aliyuncs.com/api/v1/services/audio/asr/transcription`
- **支持格式**: WAV、MP3、M4A 等
- **输入方式**: Base64 编码的音频数据

### 智能翻译服务

基于阿里百炼 Qwen 大语言模型实现：

- **语言检测**: 自动识别输入文本的语言
- **智能翻译**: 根据会议室语言自动翻译消息
- **上下文理解**: 保持翻译的语义准确性

### 国际化 (i18n) 支持

- 自动检测浏览器语言环境
- 支持中文和英文界面动态切换
- 所有 UI 文本都支持多语言

## 📝 注意事项

1. **API 密钥安全**
   - 请妥善保管您的阿里云百炼 API 密钥
   - 不要将 `.env` 文件提交到版本控制系统
   - 建议使用环境变量或密钥管理服务

2. **网络连接**
   - 语音识别和翻译需要稳定的网络连接
   - 建议使用高速网络以获得最佳体验

3. **浏览器权限**
   - 首次使用语音输入时，浏览器会请求麦克风权限
   - 请允许浏览器访问麦克风以使用语音功能

4. **房间管理**
   - 房间数据存储在本地 `room_data/` 目录
   - 房间在 1 小时无活动后会自动删除
   - 房间创建者拥有管理员权限

5. **自动刷新**
   - 建议开启自动刷新功能以实时接收消息
   - 刷新间隔可调整（默认 2-3 秒）

## 🐛 故障排除

### 语音识别失败

**问题**: 语音识别返回空结果或报错

**解决方案**:
1. 检查 API 密钥是否正确配置
2. 确认已开通阿里百炼语音识别服务权限
3. 检查网络连接是否正常
4. 确认浏览器已允许麦克风权限
5. 查看浏览器控制台和 Streamlit 日志

### 翻译不工作

**问题**: 消息没有被翻译或翻译错误

**解决方案**:
1. 检查 LLM 服务是否正常（查看 API 调用日志）
2. 确认 `MODEL_NAME` 配置正确
3. 检查网络连接
4. 查看 Streamlit 控制台错误信息

### 消息不显示

**问题**: 发送的消息没有出现在聊天室

**解决方案**:
1. 检查工作流执行日志
2. 确认房间数据文件权限
3. 查看 `room_data/` 目录中的 JSON 文件
4. 尝试刷新页面或重新加入房间

### 登录状态丢失

**问题**: 刷新页面后需要重新登录

**解决方案**:
1. 检查 URL 参数是否包含 `session_token` 和 `username`
2. 确认浏览器允许保存 URL 参数
3. 清除浏览器缓存后重试

## 🚀 未来规划

- [ ] 支持更多语言（日语、韩语等）
- [ ] 添加语音合成（TTS）功能
- [ ] 支持文件上传和分享
- [ ] 添加消息搜索功能
- [ ] 支持房间加密和隐私保护
- [ ] 添加消息撤回和编辑功能
- [ ] 支持表情和图片消息
- [ ] 添加消息通知功能

## 📄 许可证

MIT License

## 🙏 致谢

- [LangGraph](https://github.com/langchain-ai/langgraph) - 工作流管理框架
- [LangChain](https://github.com/langchain-ai/langchain) - LLM 应用开发框架
- [Streamlit](https://streamlit.io/) - Web 应用框架
- [阿里云百炼平台](https://dashscope.console.aliyun.com/) - 语音识别和 LLM 服务

---

**开发维护**: 基于 LangGraph 和阿里云百炼平台的智能会议聊天室系统

**技术支持**: 如有问题，请查看项目 Issues 或提交新的 Issue
