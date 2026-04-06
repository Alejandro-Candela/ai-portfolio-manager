# Intake Agent Prompt Tests

This directory contains test scenarios for the intake agent. Each scenario is a complete conversational flow that you can use to validate the agent's behavior.

## How to Use

1. Open the intake form at `http://localhost:3000/intake`
2. Open a test file (e.g., `scenario_1_customer_churn.md`)
3. Copy and paste each **User Message** one at a time into the chat UI
4. After the last message, the agent should output the JSON completion block
5. Verify the JSON matches the **Expected Agent Output** section

## Test Scenarios

### Scenario 1: Customer Churn Prediction
- **File**: `scenario_1_customer_churn.md`
- **Focus**: Realistic SaaS use case with clear metrics
- **Data**: Salesforce CRM data
- **Urgency**: High

### Scenario 2: Document Classification
- **File**: `scenario_2_document_classification.md`
- **Focus**: Document processing with medium priority
- **Data**: Unstructured PDFs
- **Urgency**: Medium

### Scenario 3: Real-time Fraud Detection
- **File**: `scenario_3_fraud_detection.md`
- **Focus**: Critical business impact with structured data
- **Data**: Transaction database
- **Urgency**: Critical

## What to Check

✅ Agent asks one question at a time  
✅ Agent accepts short answers without demanding elaboration  
✅ Agent doesn't repeat context or use excessive emojis  
✅ Final JSON is valid and complete  
✅ JSON matches the expected output format  
✅ Conversation feels natural and concise  

## Adding New Scenarios

Create a new markdown file following this template:

```markdown
# Prompt Test: Scenario N — [Use Case Name]

## Overview
[2–3 sentence description]

## Conversation Flow

### User Message 1: [Context]
\`\`\`
[User input]
\`\`\`

### User Message 2: [Context]
\`\`\`
[User input]
\`\`\`

[... continue for 5 messages ...]

## Expected Agent Output

Should produce JSON:
\`\`\`json
{...}
\`\`\`
```

## Notes

- Each scenario is designed to take 5 user turns (one per field: problem, stakeholders, data, outcome, urgency)
- Answers are deliberately short to test the agent's ability to accept incomplete information and ask clarifying questions
- If the agent loops or asks the same question twice, that's a bug to report
