# 💬 LangGraph Agent Meeting Room System

An intelligent Agent-based meeting chatroom built with **LangGraph**, integrated with **Alibaba Cloud Bailian Platform** for speech recognition and language model services, enabling speech transcription, intelligent translation, and real-time multi-user collaboration.

## 🌟 Key Highlights

### 🎯 Technical Features

- **🔄 LangGraph Workflow Engine**
  - Built with LangGraph for scalable message processing workflows
  - Supports conditional routing and state management for flexible message handling
  - Modular node design for easy extension and maintenance

- **🎤 Alibaba Bailian Speech Recognition**
  - Integrated with Alibaba Cloud Bailian Platform's `paraformer-realtime-v2` real-time speech recognition model
  - Supports multiple audio formats (WAV, MP3, M4A, etc.)
  - High-precision speech-to-text conversion with Chinese and English support

- **🌐 Intelligent Language Processing**
  - Intelligent translation service based on Alibaba Bailian's Qwen large language model
  - Automatic language detection and context understanding
  - Bidirectional Chinese-English translation with semantic accuracy

- **🌍 Internationalization Support (i18n)**
  - Automatic detection of user's browser language environment
  - Dynamic interface switching between Chinese and English
  - Global dynamic language interface similar to i18n

- **👥 Real-Time Multi-User Collaboration**
  - Support for multiple users chatting simultaneously
  - Real-time message synchronization and state management
  - Room management and participant permission control

## 🏗️ System Architecture

### LangGraph Workflow Design

The system uses LangGraph to build an intelligent message processing workflow, implementing flexible message handling through state graphs and conditional routing:

```
User Input (Voice/Text)
    ↓
[Entry Node (entry)] → Intelligent routing based on input type
    ↓
    ├─→ [Speech Recognition Node (speech_recognition)]
    │       ↓
    │   Call Alibaba Bailian paraformer-realtime-v2 API
    │       ↓
    │   Audio → Text Conversion
    │       ↓
    └─→ [Translation Node (translation)]
            ↓
        Language Detection (based on Qwen LLM)
            ↓
        Intelligent Translation (if needed)
            ↓
    [Message Processing Node (message)]
            ↓
    Format and Save Message
            ↓
    Display in Chatroom
```

### Core Workflow Nodes

1. **Entry Node (entry)**
   - Intelligent routing based on input type (voice/text)
   - Determines whether to enter speech recognition flow

2. **Speech Recognition Node (speech_recognition_node)**
   - Integrated with Alibaba Bailian `paraformer-realtime-v2` real-time speech recognition model
   - Supports base64-encoded audio data input
   - Automatic audio format conversion and API calls
   - Returns recognized text content

3. **Translation Node (translation_node)**
   - Uses Alibaba Bailian Qwen large language model for language detection
   - Intelligently determines if input language matches room language
   - Automatically performs translation tasks with semantic accuracy
   - Supports bidirectional Chinese-English translation

4. **Message Processing Node (message_node)**
   - Formats message content (including original text, translated text, language info)
   - Saves to room message records
   - Updates participant status

### Technology Stack

- **LangGraph**: Workflow management and state graph construction
- **LangChain**: LLM integration and message processing
- **Alibaba Cloud Bailian Platform**:
  - `paraformer-realtime-v2`: Real-time speech recognition model
  - `qwen-plus`: Large language model (for translation and language detection)
- **Streamlit**: Web UI framework
- **Python 3.12+**: Core development language

## 📦 Quick Start

### 1. Requirements

- Python 3.12 or higher
- Alibaba Cloud Bailian Platform API key

### 2. Install Dependencies

```bash
# Clone the project
git clone <repository-url>
cd firstproject

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file (refer to `env.example`):

```env
# Alibaba Cloud Bailian Platform API Key
DASHSCOPE_API_KEY=your_dashscope_api_key_here

# Large Language Model Configuration
MODEL_NAME=qwen-plus
BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

**Get API Key:**
1. Visit [Alibaba Cloud Bailian Platform](https://dashscope.console.aliyun.com/)
2. Register/Login to your account
3. Create an API key
4. Ensure speech recognition and language model service permissions are enabled

### 4. Launch Application

**Windows:**
```bash
run_meeting.bat
```

**Linux/Mac:**
```bash
streamlit run meeting_app.py
```

The application will automatically open in your browser at: `http://localhost:8501`

## 🎮 User Guide

### 1. User Registration and Login

- First-time users need to register an account
- Login status is automatically saved; refreshing the page won't lose login state

### 2. Create or Join a Room

**Create New Room:**
1. Enter a room ID in the sidebar (e.g., `meeting-001`)
2. Select room language (Chinese/English)
3. Click "Create or Join Room"
4. After successful creation, you will become the room administrator

**Join Existing Room:**
1. Select a room from the "Select Room" list
2. Or directly enter the room ID and click "Create or Join Room"
3. The system will automatically detect and join the room

### 3. Send Messages

**Method 1: Text Input**
1. Enter text in the input box
2. Click "Send Text" button
3. The system will automatically detect language and translate if needed

**Method 2: Voice Input**
1. Click "Click to Start Recording" button
2. Speak into the microphone (supports Chinese and English)
3. Click "Send Audio" button
4. The system will:
   - Call Alibaba Bailian speech recognition API to convert audio to text
   - Automatically detect language and translate if needed
   - Display in the chatroom

### 4. Language Settings

- **My Display Language**: Choose your preferred interface language (Chinese/English)
- **Room Language**: Set the primary language for the meeting room; the system will automatically translate messages based on this language
- The system automatically detects your browser language and sets the default language

### 5. Multi-User Collaboration

- All users who join the same room can see each other's messages
- Messages are synchronized in real-time to all participants (auto-refresh feature)
- Room creators have administrator privileges and can remove other participants

## 📁 Project Structure

```
firstproject/
├── src/
│   ├── state/
│   │   └── meeting_state.py          # LangGraph state definition
│   ├── services/
│   │   ├── speech_recognition.py     # Alibaba Bailian speech recognition service
│   │   ├── translation.py            # Qwen-based translation service
│   │   ├── room_manager.py           # Room and message management
│   │   └── auth_service.py           # User authentication service
│   ├── nodes/
│   │   ├── speech_recognition_node.py # LangGraph speech recognition node
│   │   ├── translation_node.py       # LangGraph translation node
│   │   ├── message_node.py           # LangGraph message processing node
│   │   └── meeting_routing.py        # Routing logic (conditional judgment)
│   ├── workflow/
│   │   └── meeting_workflow.py       # LangGraph workflow construction
│   ├── ui/
│   │   ├── meeting_app.py            # Streamlit main application
│   │   ├── auth_ui.py                # Login/Registration UI
│   │   └── state_persistence.py      # State persistence
│   ├── utils/
│   │   └── i18n.py                   # Internationalization support
│   └── config/
│       └── settings.py               # Configuration management
├── room_data/                        # Room data storage (JSON)
├── auth_data/                        # User and session data (JSON)
├── meeting_app.py                    # Application entry point
├── requirements.txt                  # Python dependencies
├── run_meeting.bat                   # Windows startup script
└── README.md                         # Project documentation
```

## 🔧 Core Features Explained

### LangGraph Workflow Implementation

The system uses LangGraph's `StateGraph` to build a stateful message processing workflow:

```python
# Workflow structure
workflow = StateGraph(MeetingState)
workflow.add_node("entry", entry_node)
workflow.add_node("speech_recognition", speech_recognition_node)
workflow.add_node("translation", translation_node)
workflow.add_node("message", message_node)

# Conditional routing
workflow.add_conditional_edges("entry", should_recognize_speech, {...})
workflow.add_conditional_edges("speech_recognition", should_translate, {...})
```

### Alibaba Bailian Speech Recognition Integration

The system encapsulates Alibaba Bailian's speech recognition API through `SpeechRecognitionService`:

- **Model**: `paraformer-realtime-v2` (real-time speech recognition)
- **API Endpoint**: `https://dashscope.aliyuncs.com/api/v1/services/audio/asr/transcription`
- **Supported Formats**: WAV, MP3, M4A, etc.
- **Input Method**: Base64-encoded audio data

### Intelligent Translation Service

Implemented based on Alibaba Bailian's Qwen large language model:

- **Language Detection**: Automatically identifies input text language
- **Intelligent Translation**: Automatically translates messages based on room language
- **Context Understanding**: Maintains semantic accuracy in translation

### Internationalization (i18n) Support

- Automatic detection of browser language environment
- Dynamic interface switching between Chinese and English
- All UI text supports multiple languages

## 📝 Important Notes

1. **API Key Security**
   - Keep your Alibaba Cloud Bailian API key secure
   - Do not commit `.env` file to version control
   - Consider using environment variables or key management services

2. **Network Connection**
   - Speech recognition and translation require stable network connection
   - High-speed network recommended for optimal experience

3. **Browser Permissions**
   - First-time voice input will request microphone permission
   - Please allow browser access to microphone for voice features

4. **Room Management**
   - Room data is stored locally in `room_data/` directory
   - Rooms are automatically deleted after 1 hour of inactivity
   - Room creators have administrator privileges

5. **Auto-Refresh**
   - Recommended to enable auto-refresh for real-time message reception
   - Refresh interval is adjustable (default 2-3 seconds)

## 🐛 Troubleshooting

### Speech Recognition Failure

**Issue**: Speech recognition returns empty result or error

**Solutions**:
1. Check if API key is correctly configured
2. Verify Alibaba Bailian speech recognition service permissions are enabled
3. Check network connection
4. Confirm browser has microphone permission
5. Check browser console and Streamlit logs

### Translation Not Working

**Issue**: Messages are not translated or translation is incorrect

**Solutions**:
1. Check if LLM service is normal (check API call logs)
2. Verify `MODEL_NAME` configuration is correct
3. Check network connection
4. Review Streamlit console error messages

### Messages Not Displaying

**Issue**: Sent messages do not appear in chatroom

**Solutions**:
1. Check workflow execution logs
2. Verify room data file permissions
3. Check JSON files in `room_data/` directory
4. Try refreshing page or rejoining room

### Login Status Lost

**Issue**: Need to login again after page refresh

**Solutions**:
1. Check if URL parameters contain `session_token` and `username`
2. Confirm browser allows saving URL parameters
3. Clear browser cache and retry

## 🚀 Future Plans

- [ ] Support for more languages (Japanese, Korean, etc.)
- [ ] Add text-to-speech (TTS) functionality
- [ ] Support file upload and sharing
- [ ] Add message search functionality
- [ ] Support room encryption and privacy protection
- [ ] Add message recall and edit features
- [ ] Support emoji and image messages
- [ ] Add message notification functionality

## 📄 License

MIT License

## 🙏 Acknowledgments

- [LangGraph](https://github.com/langchain-ai/langgraph) - Workflow management framework
- [LangChain](https://github.com/langchain-ai/langchain) - LLM application development framework
- [Streamlit](https://streamlit.io/) - Web application framework
- [Alibaba Cloud Bailian Platform](https://dashscope.console.aliyun.com/) - Speech recognition and LLM services

---

**Development & Maintenance**: Intelligent meeting chatroom system based on LangGraph and Alibaba Cloud Bailian Platform

**Technical Support**: For issues, please check project Issues or submit a new Issue
