# Language Model Module Documentation

## Overview
The `language_model` module provides the core abstraction layer for interacting with various language model providers in Concordia. This system enables seamless switching between different models and providers while maintaining consistent interfaces for text generation and choice selection.

## Core Architecture

### Abstract Base Class
- **`LanguageModel`** (`language_model.py`): Defines the fundamental interface for all language models
  - `sample_text()`: Generates free-form text responses from prompts
  - `sample_choice()`: Selects from predefined response options
  - Standard defaults: temperature (0.0), max tokens (3000), timeout (60s)
  - Built-in terminator support for controlled text generation

### Model Providers Supported
- **OpenRouter** (primary focus): Custom implementation with extensive logging and monitoring
- **OpenAI**: GPT models through standard API
- **Google**: AI Studio and Cloud Custom models
- **Ollama**: Local model execution with Langchain integration
- **Amazon Bedrock**: Enterprise cloud models
- **Mistral**: Direct API integration
- **Together AI**: Gemma2 models
- **PyTorch Gemma**: Local PyTorch execution

## OpenRouter Implementation Deep Dive

### BaseOpenRouterLanguageModel
Your custom implementation (`base_openrouter_model.py`) provides sophisticated features:

**Key Features:**
- **Entity Context Extraction**: Automatically identifies which agent/entity is making LLM calls
- **Verbose Logging**: Comprehensive call tracking with caller information and entity context
- **Built-in Rate Limiting**: Automatic 429 error handling with 61-second backoff
- **Usage Measurements**: Token consumption tracking through measurements system
- **Robust Error Handling**: Retry logic for rate limits with fallback mechanisms

**Core Methods:**
```python
sample_text(prompt, max_tokens, terminators, temperature, timeout, seed)
sample_choice(prompt, responses, seed)
```

**Logging Capabilities:**
- Caller file and line number tracking
- Entity context identification from stack frames
- Prompt truncation for readability
- Model name and parameters logging

### OpenRouterLanguageModel
The concrete implementation (`openrouter_model.py`) provides:

**Environment Integration:**
- Automatic `.env` loading for API keys and model selection
- Configurable model defaults (fallback: `mistralai/mistral-small-3.1-24b-instruct:free`)
- Environment variable support for `OPENROUTER_API_KEY` and `OPENROUTER_MODEL`

**Wrapper Integration:**
- `with_wrappers()` class method for automatic wrapper application
- Configurable retry parameters and call limits
- Production-ready defaults (3 retries, 1200 call limit)

## Wrapper Classes

### RetryLanguageModel
Advanced retry mechanism (`retry_wrapper.py`):
- **Configurable Exceptions**: Specify which exceptions trigger retries
- **Exponential Backoff**: Configurable delay with jitter
- **Transparent Interface**: Maintains full LanguageModel API
- **Flexible Configuration**: Customizable retry attempts and timing

### CallLimitLanguageModel
Production safety mechanism (`call_limit_wrapper.py`):
- **Hard Limits**: Prevents runaway API costs (default: 1200 calls)
- **Graceful Degradation**: Returns empty strings/first choices when limit reached
- **Clear Warnings**: Console notifications when limits are exceeded
- **Call Tracking**: Automatic counting across all model interactions

## Utility Functions

### Language Model Factory
The `utils.py` module provides a unified factory function:

**`language_model_setup()`**:
- **Multi-Provider Support**: Single interface for all supported providers
- **Environment Integration**: Automatic configuration from environment variables
- **Disable Mode**: Complete language model bypass for testing
- **Wrapper Automation**: Automatic retry and limit wrapper application for OpenRouter

**Special OpenRouter Handling:**
```python
if api_type == 'openrouter':
    return openrouter_model.OpenRouterLanguageModel.with_wrappers(
        model_name=model_name,
        api_key=api_key,
    )
```

## Integration with Concordia Architecture

### InteractiveDocument Integration
- Language models serve as the "thinking engine" for InteractiveDocument conversations
- Text generation drives narrative progression and decision-making
- Choice selection enables structured decision trees and option evaluation

### Thought Chains Integration
- Models power complex reasoning patterns through thought chain composition
- Each reasoning step uses language model calls to process and transform information
- Multi-step workflows orchestrate sequences of model interactions

### Entity-Specific Model Assignment
Your architecture supports future enhancements for per-entity model assignment:
- Entity context extraction already identifies which agent is making calls
- Logging system tracks model usage by entity
- Foundation exists for routing different entities to different models

## Extension Points for Future Development

### Local Model Integration
Your current architecture provides excellent foundation for local models:
- Abstract `LanguageModel` interface supports any implementation
- Wrapper system (retry, limits) works with any underlying model
- Measurements and logging systems are provider-agnostic

### Per-Entity Model Assignment
Entity context extraction enables sophisticated routing:
- Current system identifies calling entity from stack frames
- Could be extended to route different entities to different models
- Logging system already tracks usage patterns by entity

### Custom Model Implementations
The modular design supports custom model providers:
- Implement `LanguageModel` interface
- Add to `utils.py` factory function
- Automatic wrapper and measurement integration

## Performance and Monitoring

### Token Usage Tracking
- Automatic measurement publication for all API calls
- Prompt and completion token separate tracking
- Model-specific usage attribution
- Integration with Concordia's measurement system

### Debugging Capabilities
- Verbose logging shows exact prompts and entity context
- Caller information helps trace execution flow
- Rate limit handling provides operational visibility
- Call counting prevents cost overruns

## Best Practices

### Production Deployment
1. **Use Wrapper Classes**: Always apply retry and call limit wrappers
2. **Monitor Token Usage**: Enable measurements for cost tracking
3. **Configure Rate Limits**: Set appropriate backoff for your API tier
4. **Enable Verbose Logging**: Track model usage patterns and debug issues

### Development Workflow
1. **Environment Configuration**: Use `.env` files for API keys and model selection
2. **Testing Mode**: Use `DISABLE_LANGUAGE_MODEL=true` for model-free testing
3. **Wrapper Configuration**: Adjust retry and limit parameters for development vs production
4. **Entity Tracking**: Leverage entity context for debugging complex simulations

## Summary

The language_model module represents a sophisticated abstraction layer that enables Concordia's advanced AI reasoning capabilities. Your OpenRouter implementation demonstrates production-ready engineering with comprehensive logging, monitoring, rate limiting, and error handling. The modular design with wrapper classes and factory functions provides an excellent foundation for future extensions including local model integration and per-entity model assignment.

The system successfully balances flexibility (supporting multiple providers) with robustness (comprehensive error handling and monitoring), making it suitable for both research experimentation and production deployment of AI agent simulations.
