# Whisper Model Selection Guide (Local Transcription)

> **Note**: This guide applies to local Whisper transcription. If you're using OpenAI API transcription, the model is automatically optimized and this configuration doesn't apply. See `glyph --setup-transcription` to choose between methods.

## Available Models

| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| `tiny` | ~39 MB | Fastest | Basic | Quick testing, simple commands |
| `base` | ~74 MB | Fast | Good | General use, clear speech |
| `small` | ~244 MB | Medium | Better | Balanced accuracy/speed |
| `medium` | ~769 MB | Slow | High | **Default** - Best for most use cases |
| `large` | ~1550 MB | Slowest | Highest | Complex commands, accented speech |

## Recommendations

### For Most Users: `medium` (Default)
- Good balance of accuracy and speed
- Handles most voice commands well
- Works with various accents and speaking styles

### For Fast Iteration: `small` or `base`
```bash
python main.py --whisper-model small --transcript-only
```

### For Maximum Accuracy: `large`
```bash
python main.py --whisper-model large --file notes.md
```

### For Quick Testing: `tiny`
```bash
python main.py --whisper-model tiny --transcript-only
```

## Performance Expectations

- **First use**: Model will download automatically (may take time for larger models)
- **Subsequent uses**: Model is cached in memory for faster transcription
- **Memory usage**: Larger models require more RAM
- **Accuracy**: Better models handle:
  - Background noise
  - Accented speech
  - Complex vocabulary
  - Technical terms
  - Faster speech

## Configuration

The default model is set in `utils.py`:
```python
WHISPER_MODEL = "medium"  # Change this to modify the default
```

Or override per session:
```bash
python main.py --whisper-model large
```