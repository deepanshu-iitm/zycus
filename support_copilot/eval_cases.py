from __future__ import annotations

TRIAGE_CASES = [
    {
        "id": "t1_connection_timeout",
        "ticket": {
            "subject": "DataBridge Pro pipeline down",
            "body": "Production pipeline failed with ERR_CONNECTION_TIMEOUT after 30s. 47 users blocked.",
        },
        "expect_product": "DataBridge Pro",
        "expect_category": "Bug",
        "kb_contains": "databridge-pro",
    },
    {
        "id": "t2_insufficient_scope",
        "ticket": {
            "subject": "Cannot access Error Handling",
            "body": "All users get 403 Forbidden: insufficient_scope in WorkflowEngine after the latest update.",
        },
        "expect_product": "WorkflowEngine",
        "kb_contains": "authentication-sso",
    },
    {
        "id": "t3_billing_seats",
        "ticket": {
            "subject": "Charged for more seats than we use",
            "body": "Invoice shows 80 seats but we only have 50 active users. Please explain seat billing and overage.",
        },
        "expect_category": "Billing",
        "kb_contains": "billing",
    },
    {
        "id": "t4_onboarding_how_to",
        "ticket": {
            "subject": "How do we invite new users?",
            "body": "We just signed up and need the checklist for bulk CSV user import and SSO setup.",
        },
        "expect_categories": ["Onboarding", "How-To"],
        "kb_contains": "onboarding",
    },
    {
        "id": "t5_adversarial_ambiguous",
        "ticket": {
            "subject": "Something is broken",
            "body": "CloudSync files are not updating and DataBridge Pro connectors also failed. We don't know which product to file this under.",
        },
        "allowed_products": ["CloudSync", "DataBridge Pro", "Unknown"],
        "adversarial": True,
    },
]

BRIEF_CASES = [
    {
        "id": "b1_churning",
        "account_id": "ACC-2944",
        "expect_company": "Pinnacle Systems",
        "summary_must_include": "churn",
        "flag_quote_must_include": "competing vendor",
    },
    {
        "id": "b2_healthy",
        "account_id": "ACC-3033",
        "expect_company": "Polaris Group",
        "summary_must_not_include": "churning",
    },
    {
        "id": "b3_new_account",
        "account_id": "ACC-7893",
        "summary_must_include": "new",
    },
    {
        "id": "b4_at_risk",
        "account_id": "ACC-3336",
        "flag_quote_must_include": "competing vendor",
    },
    {
        "id": "b5_adversarial_unknown_id",
        "account_id": "ACC-0000",
        "expect_error": True,
        "adversarial": True,
    },
]
