# Prompt Test: Scenario 5 — Verbose, Well-Structured Inputs

## Overview
Tests the intake agent with articulate, detailed answers to verify it doesn't get lost in length.
Copy and paste each user message in order into the chat UI.

---

## Conversation Flow

### User Message 1: Detailed problem
```
Our marketing team struggles to personalize email campaigns at scale. Currently, they use basic segmentation rules that were built 3 years ago and don't account for behavioral changes, lifecycle stage transitions, or engagement patterns. This results in low open rates (12% vs. industry avg 22%) and wasted budget on irrelevant campaigns that damage brand reputation. We need a data-driven approach that adapts in real-time.
```

### User Message 2: Clear stakeholders
```
Marketing director, email campaign managers, demand gen leads, and the VP of revenue who owns the marketing efficiency metrics
```

### User Message 3: Rich data description
```
We're using Marketo for email, Salesforce for CRM (15 years of customer records), Google Analytics for web behavior, and we've recently implemented Segment to consolidate events. All data flows into a data warehouse. We have roughly 5 million historical email interactions and 50,000 active leads.
```

### User Message 4: Specific success metric
```
We want to increase email open rate to 25% within 6 months, reduce unsubscribe rate below 0.5%, and improve email revenue contribution from $2M to $3M annually through better targeting and timing
```

### User Message 5: Priority level
```
high—it's directly impacting our Q2 targets and the marketing team requested it 3 sprints ago
```

---

## Expected Agent Output

Should produce JSON:
```json
{
  "extraction_complete": true,
  "use_case": {
    "title": "AI-Driven Email Campaign Personalization",
    "problem_statement": "Generic email segmentation causes low engagement (12% open rate) and damages brand reputation",
    "stakeholders": ["Marketing Director", "Campaign Managers", "Demand Gen Leads", "VP of Revenue"],
    "available_data": "Marketo email data (5M interactions), Salesforce CRM (15 years, 50K active leads), Google Analytics web behavior, Segment event stream, unified data warehouse",
    "expected_outcome": "Increase open rate to 25%, reduce unsubscribe rate below 0.5%, grow email revenue from $2M to $3M in 6 months",
    "urgency": "high"
  }
}
```

## Notes

This scenario tests:
- ✅ Agent doesn't get overwhelmed by verbose input
- ✅ Agent extracts core metrics from detailed context
- ✅ Agent properly distills stakeholder roles from longer description
- ✅ Agent maps data sources to a concise summary
- ✅ Agent preserves quantifiable success criteria
