# Prompt Test: Scenario 4 — Edge Case: Vague Inputs

## Overview
Tests the intake agent's ability to handle incomplete or vague answers and ask clarifying questions.
Copy and paste each user message in order into the chat UI.

---

## Conversation Flow

### User Message 1: Vague problem statement
```
I dunno, just want to use AI somehow
```

### User Message 2: Unclear stakeholders
```
people
```

### User Message 3: Uncertain data
```
maybe we have some data somewhere
```

### User Message 4: Loose success criteria
```
make things better
```

### User Message 5: Ambiguous urgency
```
kind of soon
```

---

## Expected Behavior

The agent should:
- ✅ Not accept "I dunno" at face value—ask for clarification on the actual problem
- ✅ Ask which specific people or roles are involved when "people" is the answer
- ✅ Probe for concrete data sources instead of "maybe we have some data"
- ✅ Ask for measurable success criteria instead of "make things better"
- ✅ Map "kind of soon" to a priority level (low/medium/high/critical)

The agent may still output the completion JSON, but it should contain more specific inferred values rather than echoing vague user input.

## Notes

This scenario tests whether the agent appropriately challenges vague responses. If the agent accepts "I dunno" and outputs a completion, that indicates the system prompt needs tightening to require validation of user answers.
