# Old Code Archive

This directory contains the original standalone scripts and hardcoded implementations that were refactored in the v2.0 release.

## Files

### `tokencount.py`
- **Original**: Standalone token counting script with hardcoded model configurations
- **Replaced by**: `process.token_count` module with dynamic model selection
- **Key Changes**: 
  - Removed hardcoded `model_behavior` dictionary
  - Now uses OpenAI API to discover available models
  - Integrated with unified CLI

### `mergecore.py`
- **Original**: Standalone script for merging and processing content
- **Replaced by**: `process.core` module with enhanced functionality
- **Key Changes**:
  - Removed hardcoded `TOKEN_LIMITS` dictionary
  - Now uses dynamic model selection
  - Integrated retry logic and error handling

### `summarize.py`
- **Original**: Standalone summarization script
- **Replaced by**: `process.summarizer` module
- **Key Changes**:
  - Removed hardcoded model configurations
  - Added intelligent text chunking
  - Integrated with dynamic model selection

### `transcribe.py`
- **Original**: Standalone transcription script
- **Replaced by**: `process.transcriber` module
- **Key Changes**:
  - Enhanced error handling
  - Better integration with CLI
  - Improved output formatting

### `utilities.py`
- **Original**: Standalone utility functions
- **Replaced by**: `process.utils` module
- **Key Changes**:
  - Better organization and modularity
  - Enhanced error handling
  - Integration with logging system

## Migration Notes

### Why These Files Were Moved

1. **Hardcoded Models**: All original scripts used hardcoded model names and configurations that became outdated
2. **Standalone Nature**: Original scripts were independent and didn't share common functionality
3. **Limited Error Handling**: Original scripts had basic error handling
4. **No Testing**: Original scripts lacked comprehensive testing

### What Changed in v2.0

1. **Dynamic Model Selection**: All operations now automatically discover and select the most cost-efficient available models
2. **Unified CLI**: Single command-line interface for all operations
3. **Modular Architecture**: Clean separation of concerns with reusable components
4. **Comprehensive Testing**: 100% test coverage across all modules
5. **Better Error Handling**: Robust retry logic and graceful fallbacks
6. **Future-Proof**: No more hardcoded model names that become obsolete

### Using Old Code

If you need to use the old standalone scripts:

```bash
# Old way (deprecated)
python old/tokencount.py input.txt --model gpt-3.5-turbo-0613

# New way (recommended)
python -m process tokens input.txt
```

### Backward Compatibility

The new system maintains backward compatibility:
- All CLI commands work the same way
- API functions have similar signatures
- Old scripts can still be run from the `old/` directory if needed

## Version History

- **v1.x**: Original standalone scripts with hardcoded configurations
- **v2.0**: Complete refactor with dynamic model selection and unified architecture

For the latest documentation and usage, see the main [README.md](../README.md). 