"""
Student demo examples — bad vs good per sub-metric (training table).
Validated by: python main.py
"""

from dataclasses import dataclass


@dataclass
class DemoCase:
    pillar: str
    sub_metric: str
    quality: str  # "bad" | "good"
    prompt: str
    question: str
    min_score: float
    max_score: float
    label: str = ""


ALL_DEMO_CASES = [
    # ── Clarity ──────────────────────────────────────────────────────────
    DemoCase("Clarity", "Task clarity", "bad", "Generate something", "", 0.0, 0.45,
             "Task is vague — no clear deliverable"),
    DemoCase("Clarity", "Task clarity", "good", "Generate functional test cases", "", 0.85, 1.0,
             "Clear action and deliverable"),

    DemoCase("Clarity", "Language clarity", "bad", "Do the needful regarding testing", "", 0.0, 0.45,
             "Unclear, non-specific language"),
    DemoCase("Clarity", "Language clarity", "good", "Generate login test cases", "", 0.75, 1.0,
             "Direct, easy-to-understand language"),

    DemoCase("Clarity", "Instruction consistency", "bad",
             "Generate 20 test cases and only 5 test cases", "", 0.0, 0.45,
             "Conflicting quantity instructions"),
    DemoCase("Clarity", "Instruction consistency", "good", "Generate 20 test cases", "", 0.85, 1.0,
             "Single, consistent instruction"),

    # ── Specificity ──────────────────────────────────────────────────────
    DemoCase("Specificity", "Scope definition", "bad", "Generate test cases", "", 0.0, 0.45,
             "Scope too broad"),
    DemoCase("Specificity", "Scope definition", "good", "Generate login page test cases", "", 0.85, 1.0,
             "Scope narrowed to login page"),

    DemoCase("Specificity", "Persona definition", "bad", "Generate test cases", "", 0.0, 0.45,
             "No persona / role"),
    DemoCase("Specificity", "Persona definition", "good", "Act as a Senior QA Engineer", "", 0.85, 1.0,
             "Persona clearly defined"),

    DemoCase("Specificity", "Detail level", "bad", "Login page", "", 0.0, 0.45,
             "Insufficient detail"),
    DemoCase("Specificity", "Detail level", "good",
             "Username, Password, OTP, Remember Me", "", 0.85, 1.0,
             "Multiple concrete details listed"),

    # ── Context completeness ─────────────────────────────────────────────
    DemoCase("Context completeness", "Business context", "bad",
             "Generate login test cases", "", 0.0, 0.45,
             "No business / application context"),
    DemoCase("Context completeness", "Business context", "good",
             "Generate login test cases for an online banking application", "", 0.85, 1.0,
             "Business application specified"),

    DemoCase("Context completeness", "Domain context", "bad",
             "Analyze this feature", "", 0.0, 0.45,
             "Domain not identified"),
    DemoCase("Context completeness", "Domain context", "good",
             "Analyze this banking feature", "", 0.85, 1.0,
             "Banking domain specified"),

    DemoCase("Context completeness", "Scenario completeness", "bad",
             "Login page", "", 0.0, 0.45,
             "No business rules or feature detail"),
    DemoCase("Context completeness", "Scenario completeness", "good",
             "Login page with OTP and account lock after 3 failures", "", 0.85, 1.0,
             "Features and business rules provided"),

    # ── Constraint quality ───────────────────────────────────────────────
    DemoCase("Constraint quality", "Format constraints", "bad",
             "Generate test cases", "", 0.0, 0.45,
             "No output format"),
    DemoCase("Constraint quality", "Format constraints", "good",
             "Output in a table", "", 0.85, 1.0,
             "Output format defined"),

    DemoCase("Constraint quality", "Scope constraints", "bad",
             "Generate test cases", "", 0.0, 0.45,
             "No quantity / inclusion / exclusion"),
    DemoCase("Constraint quality", "Scope constraints", "good",
             "Generate 20 test cases, exclude performance testing", "", 0.85, 1.0,
             "Quantity and exclusion defined"),

    DemoCase("Constraint quality", "Response constraints", "bad",
             "Explain testing", "", 0.0, 0.45,
             "No length or tone guidance"),
    DemoCase("Constraint quality", "Response constraints", "good",
             "Explain in less than 200 words using professional language", "", 0.85, 1.0,
             "Length and tone defined"),

    # ── Ambiguity & risk ─────────────────────────────────────────────────
    DemoCase("Ambiguity & risk", "Ambiguity score", "bad",
             "Tell me about testing", "", 0.0, 0.45,
             "Broad — multiple interpretations"),
    DemoCase("Ambiguity & risk", "Ambiguity score", "good",
             "Explain AI Testing for healthcare chatbots", "", 0.85, 1.0,
             "Specific topic and domain"),

    DemoCase("Ambiguity & risk", "Assumption risk", "bad",
             "Generate test cases", "", 0.0, 0.55,
             "AI must guess scope, context, and format"),
    DemoCase("Ambiguity & risk", "Assumption risk", "good",
             "Generate login test cases for banking app with OTP", "", 0.85, 1.0,
             "Enough context — low guesswork"),

    DemoCase("Ambiguity & risk", "Conflicting instructions", "bad",
             "Generate detailed summary in 50 words", "", 0.0, 0.45,
             "Detailed vs very short — contradictory"),
    DemoCase("Ambiguity & risk", "Conflicting instructions", "good",
             "Generate detailed summary in 500 words", "", 0.85, 1.0,
             "Detailed request matches word limit"),
]

SUB_METRIC_FIELD = {
    "Task clarity": "task_clarity",
    "Language clarity": "language_clarity",
    "Instruction consistency": "instruction_consistency",
    "Scope definition": "scope_definition",
    "Persona definition": "persona_definition",
    "Detail level": "detail_level",
    "Business context": "business_context",
    "Domain context": "domain_context",
    "Scenario completeness": "scenario_completeness",
    "Format constraints": "format_constraints_score",
    "Scope constraints": "scope_constraints_score",
    "Response constraints": "response_constraints_score",
    "Ambiguity score": "ambiguity_score",
    "Assumption risk": "assumption_risk",
    "Conflicting instructions": "conflicting_instructions",
}
