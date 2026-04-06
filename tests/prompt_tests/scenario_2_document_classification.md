# Prompt Test: Scenario 2 — Document Classification

## Overview
Tests the intake agent with a document processing use case.
Copy and paste each user message in order into the chat UI.

---

## Conversation Flow

### User Message 1: Problem
```
Our legal team spends hours manually sorting and categorizing incoming contracts
```

### User Message 2: Stakeholders
```
Legal department, procurement, and contract managers
```

### User Message 3: Data
```
10,000+ scanned contracts in a shared drive, mostly PDFs from the last 3 years
```

### User Message 4: Success criteria
```
Automatically sort contracts into 12 categories with 95% accuracy so legal can review faster
```

### User Message 5: Timing
```
medium priority—nice to have but not blocking anything
```

---

## Expected Agent Output

Should produce JSON:
```json
{
  "extraction_complete": true,
  "use_case": {
    "title": "Contract Document Classification",
    "problem_statement": "Legal team manually categorizes thousands of contracts, consuming excessive hours",
    "stakeholders": ["Legal Department", "Procurement", "Contract Managers"],
    "available_data": "10,000+ scanned contracts in shared drive as PDFs from last 3 years",
    "expected_outcome": "Automatically classify contracts into 12 categories at 95% accuracy",
    "urgency": "medium"
  }
}
```
