# Prompt Test: Scenario 1 — Customer Churn Prediction

## Overview
Tests the intake agent with a realistic AI use case about predicting customer churn.
Copy and paste each user message in order into the chat UI.

---

## Conversation Flow

### User Message 1: Initial interest
```
We're losing too many customers each month and don't know why or who's at risk
```

### User Message 2: Stakeholders
```
The customer success team, account managers, and the CFO who cares about retention
```

### User Message 3: Available data
```
We have 18 months of customer data in Salesforce—subscription tier, support tickets, usage metrics, payment history
```

### User Message 4: Expected outcome
```
We want to identify at-risk customers 30 days before they cancel so we can intervene
```

### User Message 5: Urgency
```
high—we're hemorrhaging revenue
```

---

## Expected Agent Output

Should produce JSON:
```json
{
  "extraction_complete": true,
  "use_case": {
    "title": "Customer Churn Prediction",
    "problem_statement": "Losing significant revenue due to unidentified at-risk customers",
    "stakeholders": ["Customer Success Team", "Account Managers", "CFO"],
    "available_data": "18 months of customer data in Salesforce: subscription tier, support tickets, usage metrics, payment history",
    "expected_outcome": "Identify at-risk customers 30 days before cancellation to enable intervention",
    "urgency": "high"
  }
}
```
