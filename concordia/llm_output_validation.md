# LLM Output Validation in Concordia

This guide explains how to implement robust LLM output validation in Concordia projects, using the name generation example from `actor_development.py` as a case study.

## Implementation Steps

### 1. Create Validation Utilities
First, we created reusable validation functions in `concordia/utils/llm_validation.py`:

```python
def parse_llm_list_response(response: str, separator: str = '***', min_items: int = 2) -> list[str]:
    """Parse and validate list-like responses from LLMs."""
    items = [item.strip() for item in response.split(separator) if item.strip()]
    if len(items) < min_items:
        raise ValueError(f"Expected at least {min_items} items, got: {items}")
    return items

def validate_llm_output_format(response: str, required_substrings: list[str] = None) -> bool:
    """Validate LLM response format using required substrings."""
    if not required_substrings:
        return True
    return all(sub in response for sub in required_substrings)
```

### 2. Import Validation Utilities
In your script, add the import:
```python
from concordia.utils import llm_validation
```

### 3. Create Helper Function with Retry Logic
Implement a helper function that:
- Has clear documentation
- Includes retry logic
- Uses validation utilities
- Provides good error messages

Example from the name generation case:
```python
def get_character_names(prompt, num_names):
    """Get character names from LLM with validation and retry logic."""
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            # Make the prompt extremely explicit
            unparsed_names = prompt.open_question(
                f"Generate exactly {num_names} names appropriate for this time and place. "
                "Output ONLY the names with surnames, separated by ' *** '. "
                "Do not include any introductory text or explanation."
            )
            # Validate and parse the response
            names = llm_validation.parse_llm_list_response(
                response=unparsed_names,
                separator='***',
                min_items=2
            )
            print(f"Names generated (attempt {attempt + 1}):", names)
            return names
        except ValueError as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_attempts - 1:
                raise ValueError(f"Failed to generate valid names after {max_attempts} attempts") from e
```

### 4. Use the Helper Function
Replace direct LLM calls with the helper function:
```python
names = get_character_names(prompt, NAMES_TO_GENERATE)
PLAYER_ONE = names[0]
PLAYER_TWO = names[1]
```

## Key Principles

1. **Separation of Concerns**
   - Core validation logic lives in reusable utilities
   - Scenario-specific validation in helper functions
   - Clear error messages and logging

2. **Robust Error Handling**
   - Always validate LLM output
   - Include retry logic for transient failures
   - Provide clear error messages
   - Fail gracefully when retries are exhausted

3. **Clear Prompting**
   - Be extremely explicit in prompts
   - Specify exact output format required
   - Tell the LLM what NOT to include

4. **Progressive Enhancement**
   - Start with basic validation
   - Add retries if needed
   - Add more sophisticated validation as patterns emerge

## Best Practices

1. **Prompt Design**
   - Be explicit about format requirements
   - Specify separators clearly
   - Request only the needed information
   - Tell the LLM to omit explanatory text

2. **Validation**
   - Always validate critical LLM outputs
   - Use standard validation utilities when possible
   - Create specific validators for unique cases
   - Include minimum requirements (e.g., min_items)

3. **Error Handling**
   - Implement retry logic for important operations
   - Log failed attempts for debugging
   - Provide clear error messages
   - Consider fallback options

4. **Code Organization**
   - Keep validation utilities separate from business logic
   - Create helper functions for common patterns
   - Document expected formats and requirements
   - Use type hints for better code clarity

## Example Variations

The same pattern can be used for other types of LLM outputs:

```python
# Validating structured responses
def get_structured_data(prompt, required_fields):
    """Get structured data with field validation."""
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            response = prompt.open_question(...)
            # Add validation logic here
            return validated_data
        except ValueError as e:
            # Handle retry logic
            pass

# Validating numerical responses
def get_validated_number(prompt, min_val, max_val):
    """Get numerical response within bounds."""
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            response = prompt.open_question(...)
            # Add validation logic here
            return validated_number
        except ValueError as e:
            # Handle retry logic
            pass
```

This modular approach to LLM output validation helps create more reliable AI applications while keeping the code maintainable and reusable.