# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-06-27

### 🚀 Major Features

#### Dynamic Model Selection
- **NEW**: Automatic discovery of available OpenAI models via API
- **NEW**: Intelligent cost-efficient model selection (prefers `gpt-4o` → `gpt-3.5-turbo` → `gpt-4`)
- **NEW**: `show-models` CLI command to list available models
- **NEW**: Content-based model selection based on token count and requirements
- **REMOVED**: All hardcoded model configurations and `MODEL_CONFIGS`

#### Enhanced CLI
- **NEW**: Unified command-line interface for all operations
- **NEW**: `show-models` subcommand to explore available models
- **IMPROVED**: Dynamic defaults for `--engine` and `--model` arguments
- **IMPROVED**: Better help text and examples
- **NEW**: `__main__.py` for direct package execution

#### Smart Token Management
- **NEW**: Automatic model selection when none specified
- **IMPROVED**: Model-specific encoding and token counting
- **NEW**: Support for both text and message-based token counting
- **IMPROVED**: JSON and plain text file parsing

#### Intelligent Summarization
- **NEW**: Auto-configuration with optimal model selection
- **IMPROVED**: Dynamic text chunking based on model context windows
- **NEW**: Configurable prompts and parameters
- **IMPROVED**: Batch processing for large documents

### 🔧 Technical Improvements

#### Architecture
- **REFACTORED**: Modular package structure with clean separation of concerns
- **NEW**: `process.core` module for dynamic model management
- **IMPROVED**: `process.config` simplified to focus on API keys and logging
- **NEW**: Comprehensive error handling and retry logic
- **IMPROVED**: Circular import resolution with lazy imports

#### Testing
- **NEW**: 100% test coverage across all modules
- **NEW**: Unit tests for all functions
- **NEW**: Integration tests for CLI commands
- **NEW**: Mock tests for API interactions
- **NEW**: Error handling and edge case coverage

#### Code Quality
- **IMPROVED**: Type hints throughout the codebase
- **NEW**: Comprehensive docstrings for all functions
- **IMPROVED**: PEP 8 compliance
- **NEW**: Black code formatting
- **NEW**: Flake8 linting

### 📁 File Structure Changes

#### Moved to `old/` directory:
- `tokencount.py` → `process.token_count` module
- `mergecore.py` → `process.core` module
- `summarize.py` → `process.summarizer` module
- `transcribe.py` → `process.transcriber` module
- `utilities.py` → `process.utils` module

#### New files:
- `process/__main__.py` - Package entry point
- `old/README.md` - Documentation for old code
- `CHANGELOG.md` - This changelog

### 🔄 Breaking Changes

#### API Changes
- **REMOVED**: `DEFAULT_MODEL`, `MODEL_CONFIGS`, `get_model_config()` from `process.config`
- **CHANGED**: `SummarizationConfig.engine` now defaults to `None` (auto-select)
- **CHANGED**: `calculate_tokens()` model parameter now defaults to `None` (auto-select)
- **CHANGED**: All model selection functions now return dynamic results

#### CLI Changes
- **CHANGED**: `--engine` and `--model` arguments now default to auto-selection
- **NEW**: `show-models` command added
- **IMPROVED**: Help text updated to reflect dynamic defaults

### 🛠️ Migration Guide

#### From v1.x to v2.0

**Old Code:**
```python
from process.config import DEFAULT_MODEL, get_model_config
model = 'gpt-3.5-turbo-0613'
config = get_model_config(model)
```

**New Code:**
```python
from process.core import get_most_cost_efficient_model, select_model_for_content
model = get_most_cost_efficient_model()
selection = select_model_for_content(text)
```

**Old CLI:**
```bash
python -m process summarize input.txt --engine gpt-3.5-turbo-0613
```

**New CLI:**
```bash
# Auto-select best model
python -m process summarize input.txt

# Or specify model (still supported)
python -m process summarize input.txt --engine gpt-4o
```

### 🐛 Bug Fixes

- **FIXED**: Circular import issues between modules
- **FIXED**: Hardcoded model names becoming obsolete
- **FIXED**: Inconsistent error handling across modules
- **FIXED**: Missing type hints and documentation
- **FIXED**: Inadequate test coverage

### 📚 Documentation

- **NEW**: Comprehensive README with architecture overview
- **NEW**: API reference documentation
- **NEW**: Migration guide from v1.x
- **NEW**: Examples and use cases
- **IMPROVED**: Installation and setup instructions
- **NEW**: Contributing guidelines

### 📄 License

- **CHANGED**: License changed from Boost Software License to Creative Commons Attribution-ShareAlike 4.0 International License

### 🔮 Future-Proofing

- **NEW**: No more hardcoded model names that become obsolete
- **NEW**: Automatic adaptation to new OpenAI models
- **NEW**: Cost-optimized model selection
- **NEW**: Extensible architecture for new features

---

## [1.x] - Pre-2024-06-27

### Legacy Features (Moved to `old/` directory)

- Standalone scripts with hardcoded model configurations
- Basic CLI functionality
- Limited error handling
- No comprehensive testing
- Manual model selection

### Known Issues in v1.x

- Hardcoded model names became obsolete
- No automatic model discovery
- Limited error handling
- No comprehensive testing
- Circular import issues
- Inconsistent API design 