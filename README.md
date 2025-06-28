# Process - Dynamic LLM Utilities

A modern, intelligent Python package for LLM-based transcription, summarization, and token counting with **dynamic model selection** and **cost optimization**. Originally conceived as a foundation for building modular, local media automation workflows before modern OpenAI SDKs existed.

## 🎯 Project Vision

**Process** is designed as a **stub/foundation** for building sophisticated media automation workflows. It provides the core building blocks for:

- **Local Media Processing**: Audio transcription, text analysis, and content summarization
- **Modular Architecture**: Clean, extensible design for custom automation pipelines
- **Cost-Efficient Operations**: Smart model selection and resource optimization
- **Future-Proof Design**: No hardcoded dependencies that become obsolete

### Historical Context

This project was originally written **before modern OpenAI SDKs** existed, when developers had to manually manage API calls, model configurations, and token counting. The v2.0 refactor modernized the codebase to leverage current best practices while maintaining the original vision of modular, local media automation.

### Intended Use Cases

- **Content Creators**: Automated transcription and summarization of podcasts, videos, interviews
- **Researchers**: Batch processing of audio/text data with intelligent analysis
- **Developers**: Foundation for building custom media automation tools
- **Automation Engineers**: Modular components for workflow orchestration

## 🚀 Key Features

- **🔄 Dynamic Model Selection**: Automatically fetches available OpenAI models and selects the most cost-efficient option
- **💰 Cost Optimization**: Prioritizes models like `gpt-4o`, `gpt-3.5-turbo` for optimal price/performance
- **🎯 Smart Token Management**: Intelligent chunking and token counting with model-specific optimizations
- **🔧 Unified CLI**: Single command-line interface for all operations
- **📊 Real-time Model Discovery**: `show-models` command to explore available models
- **🛡️ Robust Error Handling**: Comprehensive retry logic and graceful fallbacks
- **🧪 Full Test Coverage**: 100% test coverage with comprehensive unit and integration tests
- **🏗️ Modular Foundation**: Clean architecture designed for extension and customization

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [CLI Commands](#cli-commands)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Examples](#examples)
- [Building Custom Workflows](#building-custom-workflows)
- [Migration Guide](#migration-guide)
- [Contributing](#contributing)

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- OpenAI API key
- AssemblyAI API key (for transcription)

### Install

```bash
# Clone the repository
git clone https://github.com/actuallyrizzn/process.git
cd process

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your API keys
```

### Environment Variables

Create a `.env` file with your API keys:

```env
OPENAI_KEY=your_openai_api_key_here
ASSEMBLYAI_KEY=your_assemblyai_api_key_here
LOG_LEVEL=INFO
```

## 🚀 Quick Start

### 1. Discover Available Models

```bash
python -m process show-models
```

**Output:**
```
Available OpenAI models:
- gpt-4o
- gpt-4o-mini
- gpt-3.5-turbo
- gpt-4-turbo
- gpt-4
```

### 2. Transcribe Audio

```bash
python -m process transcribe audio.mp3 --output both
```

### 3. Summarize Text

```bash
python -m process summarize input.txt --output summary.txt
```

### 4. Count Tokens

```bash
python -m process tokens input.txt
```

## 📖 CLI Commands

### `show-models`

Lists all available OpenAI models with their properties.

```bash
python -m process show-models
```

**Options:**
- `--log-level`: Set logging level (DEBUG, INFO, WARNING, ERROR)
- `--log-file`: Specify log file path

### `transcribe`

Transcribe audio files using AssemblyAI.

```bash
python -m process transcribe <file_path> [options]
```

**Arguments:**
- `file_path`: Path to the audio file

**Options:**
- `--output`: Output format (`console`, `file`, `both`) [default: console]
- `--output-file`: Custom output file path
- `--no-speaker-labels`: Disable speaker diarization
- `--timeout`: Timeout in seconds [default: 300]

**Examples:**
```bash
# Basic transcription
python -m process transcribe audio.mp3

# Save to file with speaker labels
python -m process transcribe audio.mp3 --output file --output-file transcript.txt

# Console output only, no speaker labels
python -m process transcribe audio.mp3 --output console --no-speaker-labels
```

### `summarize`

Summarize text files using OpenAI models with dynamic selection.

```bash
python -m process summarize <input_file> [options]
```

**Arguments:**
- `input_file`: Path to the input text file

**Options:**
- `--output`: Path to output file
- `--engine`: Specific OpenAI model to use (default: most cost-efficient available)
- `--temperature`: Temperature for generation [default: 0.5]
- `--max-tokens`: Maximum tokens for generation [default: 8192]
- `--prompt`: Custom summarization prompt
- `--cleanup`: Delete input file after processing

**Examples:**
```bash
# Auto-select best model
python -m process summarize input.txt --output summary.txt

# Use specific model
python -m process summarize input.txt --engine gpt-4o --temperature 0.3

# Custom prompt
python -m process summarize input.txt --prompt "Summarize the key points in bullet form"
```

### `tokens`

Count tokens in files with dynamic model selection.

```bash
python -m process tokens <filepath> [options]
```

**Arguments:**
- `filepath`: Path to the file to analyze

**Options:**
- `--model`: Specific model to calculate tokens for (default: most cost-efficient available)
- `--json`: Output in JSON format

**Examples:**
```bash
# Auto-select model
python -m process tokens input.txt

# Specific model with JSON output
python -m process tokens input.txt --model gpt-4o --json
```

## 🏗️ Architecture

### Core Components

#### 1. Dynamic Model Management (`process/core.py`)

```python
# Fetch available models from OpenAI API
models = get_available_models(client)

# Select most cost-efficient model
model = get_most_cost_efficient_model(client)

# Smart model selection based on content
selection = select_model_for_content(text)
```

**Key Functions:**
- `get_available_models()`: Fetches available models via OpenAI API
- `get_most_cost_efficient_model()`: Selects optimal model based on cost/performance
- `select_model_for_content()`: Chooses model based on content length and requirements

#### 2. Intelligent Token Management (`process/token_count.py`)

```python
# Dynamic token counting with model selection
result = calculate_tokens(content, model=None)  # Auto-selects model

# File-based token analysis
result = calculate_tokens_from_file(filepath, model=None)
```

**Features:**
- Automatic model selection when none specified
- Support for both text and message-based token counting
- JSON and plain text file parsing
- Model-specific encoding handling

#### 3. Smart Summarization (`process/summarizer.py`)

```python
# Auto-configure summarization with optimal model
config = SummarizationConfig(engine=None)  # Auto-selects model
result = summarize_text(text, config)
```

**Features:**
- Intelligent text chunking based on model context windows
- Dynamic model selection for optimal performance
- Configurable prompts and parameters
- Batch processing for large documents

#### 4. Unified CLI (`process/cli.py`)

```python
# All commands support dynamic model selection
parser.add_argument('--engine', default=None, 
                   help='OpenAI model to use (default: most cost-efficient available)')
```

**Features:**
- Consistent interface across all operations
- Dynamic defaults based on available models
- Comprehensive error handling and logging
- JSON and human-readable output formats

### Configuration (`process/config.py`)

Minimal configuration focused on API keys and logging:

```python
# API Keys
OPENAI_API_KEY = os.getenv('OPENAI_KEY')
ASSEMBLYAI_API_KEY = os.getenv('ASSEMBLYAI_KEY')

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_KEY` | OpenAI API key | Yes |
| `ASSEMBLYAI_KEY` | AssemblyAI API key | Yes (for transcription) |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | No |
| `OPENAI_FALLBACK_MODEL` | Fallback model if API fails | No |

### Model Selection Strategy

The system uses a hierarchical approach to model selection:

1. **User-specified model**: If provided via CLI or API
2. **Cost-efficient selection**: Prefers `gpt-4o` → `gpt-3.5-turbo` → `gpt-4`
3. **Content-based selection**: Considers token count and context requirements
4. **Fallback model**: Uses `gpt-3.5-turbo` if API unavailable

### Logging

Configure logging via environment variables or CLI:

```bash
# Environment variable
export LOG_LEVEL=DEBUG

# CLI option
python -m process summarize input.txt --log-level DEBUG --log-file process.log
```

## 📚 API Reference

### Core Functions

#### `get_available_models(client=None)`

Fetches available OpenAI models.

**Parameters:**
- `client`: Optional OpenAI client instance

**Returns:**
- `List[Dict[str, Any]]`: List of model information dictionaries

#### `get_most_cost_efficient_model(client=None)`

Selects the most cost-efficient available model.

**Returns:**
- `Optional[str]`: Model ID or None if no models available

#### `select_model_for_content(content)`

Selects optimal model based on content analysis.

**Parameters:**
- `content`: Text content to analyze

**Returns:**
- `ModelSelection`: Named tuple with model, max_tokens, prompt_tokens

### Token Counting

#### `calculate_tokens(data, model=None)`

Counts tokens in text or message data.

**Parameters:**
- `data`: String or list of message dictionaries
- `model`: Optional model name (auto-selects if None)

**Returns:**
- `TokenResult`: Named tuple with tokens, model, success, error

### Summarization

#### `summarize_text(text, config=None)`

Summarizes text using OpenAI models.

**Parameters:**
- `text`: Text to summarize
- `config`: Optional SummarizationConfig (auto-configures if None)

**Returns:**
- `SummarizationResult`: Named tuple with success, summaries, error

## 💡 Examples

### Programmatic Usage

```python
from process.core import get_most_cost_efficient_model, select_model_for_content
from process.summarizer import summarize_text
from process.token_count import calculate_tokens

# Get best available model
model = get_most_cost_efficient_model()
print(f"Using model: {model}")

# Smart model selection for content
selection = select_model_for_content("Long text content...")
print(f"Selected {selection.model} with {selection.max_tokens} max tokens")

# Summarize with auto-configuration
result = summarize_text("Text to summarize...")
if result.success:
    for summary in result.summaries:
        print(summary)

# Token counting with dynamic model
token_result = calculate_tokens("Text to count tokens for...")
print(f"Tokens: {token_result.tokens} (model: {token_result.model})")
```

### Advanced Configuration

```python
from process.summarizer import SummarizationConfig, summarize_text

# Custom configuration
config = SummarizationConfig(
    engine="gpt-4o",  # Specific model
    temperature=0.3,  # Lower temperature for more focused output
    max_tokens=4000,  # Custom token limit
    prompt="Summarize the main arguments and counter-arguments presented."
)

result = summarize_text("Content to summarize...", config)
```

### Batch Processing

```python
import os
from process.token_count import calculate_tokens_from_file

# Process multiple files
files = ["file1.txt", "file2.txt", "file3.txt"]
for file in files:
    result = calculate_tokens_from_file(file)
    if result.success:
        print(f"{file}: {result.tokens} tokens")
    else:
        print(f"{file}: Error - {result.error}")
```

## 🔧 Building Custom Workflows

**Process** is designed as a foundation for building custom media automation workflows. Here are some examples of how to extend it:

### Custom Media Pipeline

```python
from process.core import get_most_cost_efficient_model
from process.summarizer import summarize_text
from process.token_count import calculate_tokens
import os

class MediaProcessor:
    def __init__(self):
        self.model = get_most_cost_efficient_model()
    
    def process_podcast(self, audio_file, output_dir):
        """Complete podcast processing pipeline."""
        # 1. Transcribe audio
        transcript = self.transcribe_audio(audio_file)
        
        # 2. Analyze content
        analysis = self.analyze_content(transcript)
        
        # 3. Generate summaries
        summaries = self.generate_summaries(transcript)
        
        # 4. Save results
        self.save_results(output_dir, transcript, analysis, summaries)
    
    def analyze_content(self, text):
        """Custom content analysis."""
        # Use Process components as building blocks
        token_info = calculate_tokens(text, self.model)
        # Add your custom analysis logic here
        return {"tokens": token_info.tokens, "custom_analysis": "..."}
```

### Workflow Orchestration

```python
from process.summarizer import SummarizationConfig
from process.core import select_model_for_content

class WorkflowOrchestrator:
    def __init__(self):
        self.workflows = {}
    
    def register_workflow(self, name, steps):
        """Register a custom workflow."""
        self.workflows[name] = steps
    
    def execute_workflow(self, name, input_data):
        """Execute a registered workflow."""
        if name not in self.workflows:
            raise ValueError(f"Workflow '{name}' not found")
        
        result = input_data
        for step in self.workflows[name]:
            result = step(result)
        return result

# Example usage
orchestrator = WorkflowOrchestrator()

# Define custom workflow
def transcribe_step(data):
    # Use Process transcription
    return transcribe_audio(data['audio_file'])

def summarize_step(data):
    # Use Process summarization with custom config
    config = SummarizationConfig(
        prompt="Extract key insights and action items",
        temperature=0.3
    )
    return summarize_text(data['transcript'], config)

# Register workflow
orchestrator.register_workflow("podcast_analysis", [
    transcribe_step,
    summarize_step
])
```

### Local Media Automation

```python
import os
from pathlib import Path
from process.core import get_most_cost_efficient_model
from process.summarizer import summarize_text

class LocalMediaAutomation:
    def __init__(self, media_dir):
        self.media_dir = Path(media_dir)
        self.model = get_most_cost_efficient_model()
    
    def process_new_files(self):
        """Automatically process new media files."""
        for file_path in self.media_dir.rglob("*.mp3"):
            if self.is_new_file(file_path):
                self.process_audio_file(file_path)
    
    def process_audio_file(self, file_path):
        """Process a single audio file."""
        # Use Process components
        transcript = self.transcribe(file_path)
        summary = self.summarize(transcript)
        self.save_metadata(file_path, transcript, summary)
    
    def summarize(self, text):
        """Custom summarization with Process."""
        return summarize_text(text)
```

## 🔄 Migration Guide

### From Hardcoded Models (v1.x)

The refactor removed all hardcoded model configurations. Here's how to migrate:

#### Old Code (v1.x)
```python
from process.config import DEFAULT_MODEL, get_model_config

# Hardcoded model selection
model = 'gpt-3.5-turbo-0613'
config = get_model_config(model)
```

#### New Code (v2.x)
```python
from process.core import get_most_cost_efficient_model, select_model_for_content

# Dynamic model selection
model = get_most_cost_efficient_model()
selection = select_model_for_content(text)
```

#### CLI Changes

**Old:**
```bash
python -m process summarize input.txt --engine gpt-3.5-turbo-0613
```

**New:**
```bash
# Auto-select best model
python -m process summarize input.txt

# Or specify model (still supported)
python -m process summarize input.txt --engine gpt-4o
```

### Backward Compatibility

- All CLI commands remain the same
- `--engine` and `--model` arguments still work
- API functions maintain similar signatures
- Old standalone scripts moved to `old/` directory

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# With coverage
pytest --cov=process

# Specific test file
pytest tests/test_core.py

# Verbose output
pytest -v
```

### Test Coverage

- **100% test coverage** across all modules
- Unit tests for all functions
- Integration tests for CLI commands
- Mock tests for API interactions
- Error handling and edge case coverage

## 🤝 Contributing

### Development Setup

```bash
# Clone and setup
git clone https://github.com/actuallyrizzn/process.git
cd process
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black process/ tests/

# Lint code
flake8 process/ tests/
```

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings for all functions
- Write tests for new features
- Update documentation

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add/update tests
5. Update documentation
6. Submit a pull request

## 📄 License

This project is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for providing the API and models
- AssemblyAI for transcription services
- The open-source community for inspiration and tools

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/actuallyrizzn/process/issues)
- **Discussions**: [GitHub Discussions](https://github.com/actuallyrizzn/process/discussions)
- **Documentation**: [GitHub Wiki](https://github.com/actuallyrizzn/process/wiki)

---

**Process** - A foundation for building intelligent, modular media automation workflows. 🚀

*Originally conceived before modern OpenAI SDKs, now modernized for the future of AI-powered media processing.*
