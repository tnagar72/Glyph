# Glyph Architecture Documentation

## Overview

Glyph implements a sophisticated dual-mode architecture that demonstrates advanced software engineering principles including clean architecture, dependency injection, event-driven design, and comprehensive testing strategies.

---

## Core Architecture Principles

### 1. **Separation of Concerns**
Each module has a single, well-defined responsibility:
- Audio processing is isolated in `recording.py` and `audio_config.py`
- Transcription logic is encapsulated in service classes
- Agent functionality is modular with pluggable tools
- UI logic is separated from business logic

### 2. **Dependency Injection**
Services are injected rather than hard-coded:
```python
# Example: Transcription service injection
class AgentSession:
    def __init__(self, transcription_service=None):
        self.transcription_service = transcription_service or get_transcription_service()
```

### 3. **Strategy Pattern**
Multiple implementations of the same interface:
- Local Whisper vs OpenAI API transcription
- Different audio recording modes
- Pluggable agent tools

### 4. **Event-Driven Architecture**
Loose coupling through events and callbacks:
- Session logging captures all events
- Agent memory learns from successful interactions
- UI updates respond to system events

---

## System Architecture

### High-Level Flow

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│                 │    │                  │    │                 │
│   Audio Input   │───▶│   Transcription  │───▶│   AI Processing │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│                 │    │                  │    │                 │
│ Device Manager  │    │ Method Selection │    │  Mode Router    │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Mode-Specific Architectures

#### Direct Mode Architecture
```
User Voice Input
       │
       ▼
┌─────────────────┐
│ Audio Capture   │ ◄── audio_config.py
│ & Validation    │     recording.py
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Transcription  │ ◄── transcription.py
│    Service      │     transcription_config.py
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  GPT-4 Edit     │ ◄── llm.py
│  Processing     │     prompts.py
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Diff & User    │ ◄── diff.py
│    Approval     │     ui_helpers.py
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  File Update    │ ◄── md_file.py
│  & Backup      │     backup_manager.py
└─────────────────┘
```

#### Agent Mode Architecture
```
User Voice Input
       │
       ▼
┌─────────────────┐
│ Audio Capture   │ ◄── Same as Direct Mode
│ & Validation    │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Transcription  │ ◄── Same as Direct Mode
│    Service      │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Context Builder │ ◄── agent_context.py
│ & Memory Lookup │     agent_memory.py
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Agent LLM       │ ◄── agent_llm.py
│ Processing      │     agent_prompts.py
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Tool Selection  │ ◄── agent_tools.py
│ & Execution     │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Memory Update   │ ◄── agent_memory.py
│ & Learning      │     agent_context.py
└─────────────────┘
```

---

## Component Deep Dive

### Audio System

#### Recording Module (`recording.py`)
```python
class AudioCapture:
    """Handles dual-mode audio recording with validation."""
    
    def __init__(self, device_manager):
        self.device_manager = device_manager
        self.validation_rules = [
            MinimumDurationRule(),
            SilenceDetectionRule(),
            NoiseFilterRule()
        ]
    
    def capture_audio(self, mode: RecordingMode) -> AudioData:
        """Capture audio using specified mode."""
        # Strategy pattern for recording modes
        recorder = self._get_recorder(mode)
        return recorder.record()
```

#### Device Management (`audio_config.py`)
```python
class AudioDeviceManager:
    """Smart audio device detection and configuration."""
    
    def get_suitable_devices(self) -> List[DeviceInfo]:
        """Get ranked list of suitable input devices."""
        devices = sd.query_devices()
        suitable = [d for d in devices if d['max_input_channels'] > 0]
        return sorted(suitable, key=self._score_device, reverse=True)
    
    def _score_device(self, device: DeviceInfo) -> int:
        """Score device suitability using heuristics."""
        score = 0
        name = device['name'].lower()
        
        # Scoring algorithm
        if 'macbook' in name and 'microphone' in name:
            score += 100
        elif 'microphone' in name or 'mic' in name:
            score += 50
        # ... additional scoring rules
        
        return score
```

### Transcription Engine

#### Service Architecture (`transcription.py`)
```python
class TranscriptionService:
    """Unified interface for multiple transcription methods."""
    
    def __init__(self):
        self.providers = {
            'local': LocalWhisperProvider(),
            'openai_api': OpenAIAPIProvider()
        }
        self.config = get_transcription_config()
    
    def transcribe(self, audio_data, method=None, language="auto"):
        """Transcribe with automatic fallback."""
        method = method or self.config.get_transcription_method()
        
        try:
            provider = self.providers[method]
            return provider.transcribe(audio_data, language)
        except Exception as e:
            # Automatic fallback to local processing
            if method == 'openai_api':
                logger.warning(f"API transcription failed: {e}, falling back to local")
                return self.providers['local'].transcribe(audio_data, language)
            raise
```

#### Provider Pattern
```python
class TranscriptionProvider(ABC):
    """Abstract base for transcription providers."""
    
    @abstractmethod
    def transcribe(self, audio_data, language: str) -> str:
        pass
    
    @abstractmethod
    def test_connection(self) -> Tuple[bool, str]:
        pass

class LocalWhisperProvider(TranscriptionProvider):
    """Local Whisper model provider."""
    
    def __init__(self):
        self._model_cache = {}
        self._current_model = None
    
    def transcribe(self, audio_data, language: str) -> str:
        model = self._get_model()
        with self._create_temp_file(audio_data) as temp_path:
            result = model.transcribe(temp_path, language=language)
            return result["text"].strip()
```

### Agent System

#### Conversational Interface (`agent_cli.py`)
```python
class AgentSession:
    """Manages conversational agent sessions."""
    
    def __init__(self, enter_stop=True, transcription_method=None, text_only=False):
        self.tools = AgentTools()
        self.context = get_conversation_context()
        self.memory = get_agent_memory()
        self.llm = AgentLLM()
        
        # Dependency injection
        self.transcription_service = get_transcription_service()
        self.config = get_agent_config()
        
        # Session state
        self.commands_processed = 0
        self.successful_operations = 0
        self.session_start = time.time()
    
    def process_command(self, user_input: str) -> bool:
        """Process a user command through the agent pipeline."""
        try:
            # 1. Build context for LLM
            context = self._build_context()
            
            # 2. Get LLM response with tool calls
            response = self.llm.process_command(user_input, context)
            
            # 3. Execute tool calls
            results = self._execute_tool_calls(response.get('tool_calls', []))
            
            # 4. Update memory and context
            self._update_context(user_input, results)
            
            # 5. Learn from successful interactions
            self._learn_from_interaction(user_input, results)
            
            return True
            
        except Exception as e:
            logger.error(f"Command processing failed: {e}")
            return False
```

#### Memory System (`agent_memory.py`)
```python
class AgentMemory:
    """Persistent learning and reference system."""
    
    def __init__(self):
        self.note_references = {}  # reference -> note_path mapping
        self.entities = {}         # entity -> related_notes mapping
        self.interaction_history = []
        
        self._load_memory()
        
    def register_note_reference(self, reference: str, note_path: str, source: str):
        """Learn a new way to refer to a note."""
        reference_key = reference.lower().strip()
        
        if reference_key not in self.note_references:
            self.note_references[reference_key] = {
                'path': note_path,
                'variations': [],
                'confidence': 1.0,
                'sources': []
            }
        
        # Update reference data
        ref_data = self.note_references[reference_key]
        ref_data['sources'].append(source)
        ref_data['confidence'] = min(ref_data['confidence'] + 0.1, 1.0)
        
        self._save_memory()
    
    def resolve_note_reference(self, reference: str) -> Optional[str]:
        """Resolve a reference to a note path with fuzzy matching."""
        reference_key = reference.lower().strip()
        
        # Exact match
        if reference_key in self.note_references:
            return self.note_references[reference_key]['path']
        
        # Fuzzy matching
        best_match = None
        best_score = 0.0
        
        for stored_ref, data in self.note_references.items():
            score = self._calculate_similarity(reference_key, stored_ref)
            if score > 0.8 and score > best_score:  # High confidence threshold
                best_match = data['path']
                best_score = score
        
        return best_match
    
    def _calculate_similarity(self, ref1: str, ref2: str) -> float:
        """Calculate similarity between references using multiple algorithms."""
        # Combine multiple similarity metrics
        levenshtein_sim = self._levenshtein_similarity(ref1, ref2)
        token_sim = self._token_similarity(ref1, ref2)
        
        # Weighted combination
        return 0.6 * levenshtein_sim + 0.4 * token_sim
```

#### Tool System (`agent_tools.py`)
```python
class AgentTools:
    """Extensible tool system for agent operations."""
    
    def __init__(self):
        self.config = get_agent_config()
        self.memory = get_agent_memory()
        self.tool_call_count = 0
        
        # Register all available tools
        self.tools = {
            'create_note': self._tool_create_note,
            'read_note': self._tool_read_note,
            'list_notes': self._tool_list_notes,
            'insert_section': self._tool_insert_section,
            # ... 15+ tools
        }
    
    def execute_tool_call(self, tool_call: dict) -> ToolCallResult:
        """Execute a tool call with error handling."""
        tool_name = tool_call.get('tool_call')
        arguments = tool_call.get('arguments', {})
        
        if tool_name not in self.tools:
            return ToolCallResult(
                success=False,
                message=f"Unknown tool: {tool_name}"
            )
        
        try:
            self.tool_call_count += 1
            tool_func = self.tools[tool_name]
            return tool_func(**arguments)
            
        except Exception as e:
            logger.error(f"Tool execution failed: {tool_name}({arguments}) - {e}")
            return ToolCallResult(
                success=False,
                message=f"Tool execution failed: {e}"
            )
    
    def _tool_create_note(self, name: str, folder: str = None, content: str = None) -> ToolCallResult:
        """Create a new note with optional content."""
        # Implementation with validation, backup, and error handling
        # ...
```

---

## Data Flow Architecture

### Configuration Management

All configuration is centralized and persistent:

```python
# Configuration hierarchy
~/.glyph/
├── agent_config.json       # Agent preferences and vault settings
├── audio_config.json       # Audio device configuration
├── model_config.json       # Whisper model selection
├── transcription_config.json # Transcription method preferences
└── memory/                  # Agent learning data
    ├── note_references.json # Reference → note mappings
    ├── entities.json        # Entity tracking
    └── conversation_history.json # Session context
```

### Session State Management

```python
class SessionState:
    """Manages session-wide state and context."""
    
    def __init__(self):
        self.current_focus = None      # Currently active note
        self.recent_operations = []    # Last N operations for undo
        self.session_entities = {}     # Temporary entities for this session
        self.working_context = {}      # Context for reference resolution
        
    def update_focus(self, note_path: str):
        """Update current focus and context."""
        self.current_focus = note_path
        self.working_context['last_mentioned'] = note_path
        
    def add_operation(self, operation: dict):
        """Track operation for undo and reference."""
        self.recent_operations.append(operation)
        if len(self.recent_operations) > 10:
            self.recent_operations.pop(0)  # Keep last 10
```

---

## Error Handling Strategy

### Hierarchical Error Recovery

1. **Local Error Handling**: Each component handles its own errors
2. **Graceful Degradation**: Fallback to simpler methods when advanced features fail
3. **User Notification**: Clear, actionable error messages
4. **System Recovery**: Automatic recovery where possible

```python
class ErrorRecoveryStrategy:
    """Implements hierarchical error recovery."""
    
    def handle_transcription_error(self, error, method):
        if method == 'openai_api':
            # Fallback to local processing
            return self.fallback_to_local()
        else:
            # Try smaller model or different settings
            return self.fallback_to_basic_model()
    
    def handle_agent_error(self, error, context):
        # Save context for recovery
        self.save_recovery_context(context)
        
        # Provide user guidance
        return self.generate_recovery_guidance(error)
```

---

## Performance Architecture

### Caching Strategy

```python
class ModelCache:
    """Efficient model caching with memory management."""
    
    def __init__(self, max_memory_gb=8):
        self.cache = {}
        self.max_memory = max_memory_gb * 1024 * 1024 * 1024
        self.current_memory = 0
        
    def get_model(self, model_name):
        if model_name not in self.cache:
            if self._would_exceed_memory(model_name):
                self._evict_lru_model()
            
            self.cache[model_name] = self._load_model(model_name)
        
        return self.cache[model_name]
```

### Async Operations

```python
async def process_audio_pipeline(audio_data):
    """Async pipeline for better responsiveness."""
    # Run transcription and LLM processing concurrently where possible
    transcription_task = asyncio.create_task(transcribe_audio(audio_data))
    context_task = asyncio.create_task(build_context())
    
    transcription = await transcription_task
    context = await context_task
    
    # Process with LLM
    return await process_llm_request(transcription, context)
```

---

## Security Architecture

### Input Validation

```python
class InputValidator:
    """Comprehensive input validation."""
    
    def validate_file_path(self, path: str) -> str:
        """Validate and sanitize file paths."""
        # Prevent directory traversal
        if '..' in path or path.startswith('/'):
            raise SecurityError("Invalid path detected")
        
        # Ensure markdown extension
        if not path.endswith(('.md', '.markdown')):
            path += '.md'
        
        return path
    
    def validate_voice_command(self, command: str) -> str:
        """Sanitize voice commands."""
        # Remove potentially dangerous content
        dangerous_patterns = ['rm -rf', 'del *', 'format', 'sudo']
        for pattern in dangerous_patterns:
            if pattern in command.lower():
                raise SecurityError(f"Potentially dangerous command: {pattern}")
        
        return command
```

### API Security

```python
class SecureAPIClient:
    """Secure wrapper for external API calls."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = True  # Always verify SSL
        self.rate_limiter = RateLimiter(max_calls=60, window=60)
        
    def make_request(self, url, data):
        # Rate limiting
        self.rate_limiter.acquire()
        
        # Request validation
        if not url.startswith('https://'):
            raise SecurityError("Only HTTPS requests allowed")
        
        # Make secure request
        return self.session.post(url, json=data, timeout=30)
```

---

## Testing Architecture

### Test Strategy

1. **Unit Tests**: Each component tested in isolation
2. **Integration Tests**: Component interaction testing
3. **End-to-End Tests**: Complete workflow validation
4. **Performance Tests**: Latency and resource usage
5. **Security Tests**: Input validation and error handling

### Mock Strategy

```python
class AudioMockProvider:
    """Provides consistent audio data for testing."""
    
    def __init__(self):
        self.test_audio = self._generate_test_audio()
        
    def get_test_audio(self, duration=1.0, noise_level=0.1):
        """Generate consistent test audio data."""
        # Generate sine wave with controlled noise
        return np.random.normal(0, noise_level, int(16000 * duration))

class APITestMock:
    """Mock external API calls for reliable testing."""
    
    def __init__(self):
        self.responses = {
            'transcribe': "This is a test transcription.",
            'gpt4': {"choices": [{"message": {"content": "Mock response"}}]}
        }
    
    def mock_openai_call(self, endpoint, data):
        return self.responses.get(endpoint, "Mock response")
```

---

## Deployment Architecture

### Environment Management

```python
class EnvironmentManager:
    """Manages different deployment environments."""
    
    def __init__(self):
        self.env = os.getenv('GLYPH_ENV', 'development')
        self.config = self._load_env_config()
        
    def _load_env_config(self):
        configs = {
            'development': {
                'log_level': 'DEBUG',
                'model_cache': True,
                'api_timeout': 30
            },
            'production': {
                'log_level': 'INFO',
                'model_cache': True,
                'api_timeout': 10
            },
            'testing': {
                'log_level': 'ERROR',
                'model_cache': False,
                'api_timeout': 5
            }
        }
        return configs.get(self.env, configs['development'])
```

### Container Architecture

```dockerfile
# Multi-stage build for optimized deployment
FROM python:3.9-slim as base
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

FROM base as test
COPY . .
RUN python run_all_tests.py

FROM base as production
COPY --from=test /app .
EXPOSE 8080
CMD ["python", "main.py", "--server-mode"]
```

---

## Monitoring & Observability

### Metrics Collection

```python
class MetricsCollector:
    """Collects performance and usage metrics."""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.timers = {}
        
    def time_operation(self, operation_name):
        """Context manager for timing operations."""
        return Timer(operation_name, self._record_timing)
    
    def record_event(self, event_name, metadata=None):
        """Record application events."""
        event = {
            'timestamp': time.time(),
            'event': event_name,
            'metadata': metadata or {}
        }
        self.metrics[event_name].append(event)
```

### Health Checks

```python
class HealthChecker:
    """System health monitoring."""
    
    def check_system_health(self):
        """Comprehensive system health check."""
        checks = {
            'audio_system': self._check_audio(),
            'transcription': self._check_transcription(),
            'file_system': self._check_file_access(),
            'memory_usage': self._check_memory(),
            'api_connectivity': self._check_apis()
        }
        
        overall_health = all(checks.values())
        return {
            'healthy': overall_health,
            'checks': checks,
            'timestamp': time.time()
        }
```

---
