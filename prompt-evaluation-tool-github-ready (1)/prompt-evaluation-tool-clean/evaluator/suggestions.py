"""Weakness detection, strengths, and full enhanced-prompt generation."""

import re

from evaluator.result import PromptEvaluationResult

MAJOR_WEAKNESS = {
    "scope": ("Scope Too Broad", "Narrow scope: specify feature, module, or deliverable"),
    "format": ("No Output Format Defined", "Specify output format: Table / List / JSON with columns"),
    "persona": ("No Persona Defined", "Add a persona — e.g. Act as a Senior QA Engineer"),
    "business": ("Insufficient Business Context", "Specify application, page, or target audience"),
    "scenario": ("Incomplete Scenario", "Add Features, Requirements, or scenario details"),
    "domain": ("No Domain Context", "Specify domain: QA / banking / technology"),
    "objective": ("Objective Not Clear", "Start with: Generate / Explain / Create / List"),
    "wording": ("Vague Wording", "Replace vague phrases with specific deliverables"),
    "ambiguity": ("High Ambiguity", "Clarify intended meaning when terms are ambiguous"),
    "conflict": ("Contradictory Instructions", "Remove conflicting rules from the prompt"),
}

MINOR_WEAKNESS = {
    "length": ("No Response Length Guidance", "Limit response to 1000 words"),
    "audience": ("No Target Audience", "Specify audience if content level matters (beginner vs expert)"),
}

# Optional enhancements — never treated as weaknesses or appended at 100% score
OPTIONAL_TIPS = {
    "priority": (
        "Optional: Priority / Severity columns",
        "You may add Priority (High/Medium/Low) and Severity columns for richer test management.",
    ),
    "test_data": (
        "Optional: Test data guidance",
        "You may specify test data variations (valid, invalid, boundary) for more thorough cases.",
    ),
}


def build_strengths(prompt: str, result: PromptEvaluationResult) -> list[str]:
    strengths = []
    p = prompt.lower()

    if result.persona_definition >= 0.8:
        strengths.append("Clear persona definition")
    if result.domain_context >= 0.7:
        strengths.append("Strong domain context")
    if result.task_clarity >= 0.8:
        strengths.append("Specific task definition")
    if result.format_guidance >= 0.8:
        strengths.append("Structured output format")
    if result.prompt_type == "generate":
        if result.quantity_constraint >= 0.8:
            strengths.append("Quantity constraint defined")
        if result.exclusion_rules >= 0.8:
            strengths.append("Exclusion rules defined")
    if result.inclusion_rules >= 0.8:
        label = "Content scope defined" if result.prompt_type == "explain" else "Inclusion rules defined"
        strengths.append(label)
    if result.ambiguity_score >= 0.85:
        strengths.append("Low ambiguity")
    if result.business_context >= 0.8:
        strengths.append("Strong business context")
    if result.scenario_completeness >= 0.8:
        strengths.append("Complete scenario detail")
    if "boundary" in p or "edge" in p or "negative" in p:
        strengths.append("Scenario coverage (functional/negative/edge)")
    if "columns:" in p or "column:" in p:
        strengths.append("Output columns specified")

    return strengths


def build_suggestions(
    prompt: str,
    question: str,
    result: PromptEvaluationResult,
) -> tuple[list[tuple[str, str]], list[tuple[str, str]], str]:
    items: list[tuple[str, str]] = []
    tips: list[tuple[str, str]] = []
    score = result.final_score()
    p = prompt.lower()

    # ── Real weaknesses (type-aware, aligned with pillar scores) ──
    if result.scope_definition < 0.6:
        items.append(MAJOR_WEAKNESS["scope"])
    if result.format_guidance < 0.5:
        items.append(MAJOR_WEAKNESS["format"])
    if result.prompt_type == "generate" and result.business_context < 0.5:
        items.append(MAJOR_WEAKNESS["business"])
    elif result.prompt_type == "explain" and result.business_context < 0.6 and score < 80:
        items.append(MAJOR_WEAKNESS["business"])
    if result.prompt_type == "generate" and result.scenario_completeness < 0.5:
        items.append(MAJOR_WEAKNESS["scenario"])
    elif result.prompt_type == "explain" and result.scenario_completeness < 0.6 and score < 80:
        items.append(MAJOR_WEAKNESS["scenario"])
    if result.prompt_type == "generate" and result.domain_context < 0.5:
        items.append(MAJOR_WEAKNESS["domain"])
    elif result.prompt_type == "explain" and result.domain_context < 0.6 and score < 70:
        items.append(MAJOR_WEAKNESS["domain"])
    if result.task_clarity < 0.5:
        items.append(MAJOR_WEAKNESS["objective"])
    if result.language_clarity < 0.5:
        items.append(MAJOR_WEAKNESS["wording"])
    if result.ambiguity_score < 0.5:
        items.append(MAJOR_WEAKNESS["ambiguity"])
    if result.instruction_consistency < 0.7:
        items.append(MAJOR_WEAKNESS["conflict"])

    if result.length_constraint < 0.5 and score < 95:
        items.append(MINOR_WEAKNESS["length"])
    if result.persona_definition < 0.5 and score < 75:
        items.append(MAJOR_WEAKNESS["persona"])

    # ── Optional tips only (never shown as weaknesses at high scores) ──
    if score >= 90 and "test case" in p:
        if "priority" not in p and "severity" not in p:
            tips.append(OPTIONAL_TIPS["priority"])
        if "test data" not in p and result.quantity_constraint >= 0.8:
            tips.append(OPTIONAL_TIPS["test_data"])

    suggested = _improve_prompt(prompt, question, items, result)
    return items, tips, suggested


def _improve_prompt(
    prompt: str,
    question: str,
    weakness_items: list[tuple[str, str]],
    result: PromptEvaluationResult,
) -> str:
    original = prompt.strip()
    if not weakness_items:
        return original

    # Score 95+: prompt is excellent — do not append anything
    if result.final_score() >= 95:
        return original

    # Strong prompts with real gaps: append only actual weaknesses
    if result.final_score() >= 75:
        return _append_requirements(original, weakness_items)

    # Weak / medium prompts: generate a complete enhanced prompt
    return _build_full_enhanced_prompt(original, question, weakness_items, result)


def _append_requirements(original: str, weakness_items: list[tuple[str, str]]) -> str:
    additions = []
    seen: set[str] = set()
    for _, suggestion in weakness_items:
        if suggestion not in seen:
            additions.append(suggestion)
            seen.add(suggestion)

    lines = [original, "", "Additional Requirements:"]
    for item in additions:
        lines.append(f"- {item}")
    return "\n".join(lines).strip()


def _detect_intent(prompt: str, question: str) -> str:
    text = f"{prompt} {question}".lower()
    if any(term in text for term in ["apple", "python", "java", "mercury"]):
        if any(x in text for x in ["what is", "what are", "explain", "tell me", "describe"]):
            return "ambiguous_explain"
    if any(x in text for x in ["test case", "test cases", "write test", "create test", "generate test"]):
        return "test_cases"
    if any(x in text for x in ["explain", "describe", "what is", "how to"]):
        if "test" in text or "qa" in text or "selenium" in text:
            return "explain_testing"
        if "ai" in text:
            return "explain_ai"
        return "explain_general"
    if any(x in text for x in ["list", "generate", "create", "write"]):
        return "generate"
    return "explain_general"


def _extract_task(prompt: str, question: str) -> str:
    """Use the clearest task line — prefer question when prompt is vague."""
    p = prompt.strip()
    q = question.strip()
    if q and (len(p.split()) < 8 or _is_vague_prompt(p)):
        return q.rstrip("?.")
    return p.rstrip("?.")


def _is_vague_prompt(prompt: str) -> bool:
    lower = prompt.lower().strip()
    vague_starts = ["explain testing", "write about", "help me", "answer this", "do this"]
    return any(lower.startswith(v) or lower == v.rstrip(".") for v in vague_starts) or len(lower.split()) <= 4


def _build_full_enhanced_prompt(
    original: str,
    question: str,
    weakness_items: list[tuple[str, str]],
    result: PromptEvaluationResult,
) -> str:
    intent = _detect_intent(original, question)
    include_priority = any("priority" in w.lower() or "severity" in w.lower() for w, _ in weakness_items)
    include_length = any("length" in w.lower() or "1000" in s for w, s in weakness_items)

    if intent == "test_cases":
        return _template_test_cases(original, include_priority, include_length)

    if intent == "ambiguous_explain":
        return _template_ambiguous_explain(original, question, include_length)

    if intent == "explain_testing":
        return _template_explain_stlc(include_length)

    if intent == "explain_ai":
        return _template_explain_ai(include_length)

    return _template_general(original, question, weakness_items, include_length)


def _template_ambiguous_explain(original: str, question: str, include_length: bool) -> str:
    task = _extract_task(original, question)

    lines = [
        "Act as a subject-matter expert.",
        "",
        f"Task: {task}.",
        "",
        "Clarification: This term may have multiple meanings. "
        "If ambiguous (e.g. Apple = technology company vs fruit), "
        "state which meaning you are answering OR ask the user to clarify.",
        "",
        "Provide:",
        "1. Clear definition",
        "2. Key facts or characteristics",
        "3. A practical example",
        "",
        "Output Format:",
        "Table or numbered sections",
        "",
        "Columns / Sections:",
        "- Topic",
        "- Explanation",
        "- Example",
    ]
    if include_length:
        lines.append("")
        lines.append("Limit response to 1000 words.")
    return "\n".join(lines)


def _template_test_cases(original: str, include_priority: bool, include_length: bool) -> str:
    columns = [
        "- Test Case ID",
        "- Scenario",
        "- Steps",
        "- Test Data",
        "- Expected Result",
    ]
    if include_priority:
        columns.extend(["- Priority (High/Medium/Low)", "- Severity"])

    lines = [
        "Act as a Senior QA Architect with expertise in AI Testing.",
        "",
        "Generate functional, negative, and edge test cases for the Login Page "
        "of an online banking application.",
        "",
        "Features:",
        "- Username",
        "- Password",
        "- OTP Authentication",
        "- Remember Me",
        "- Forgot Password",
        "- Account Lock after 3 failed attempts",
        "",
        "Requirements:",
        "- Include boundary scenarios",
        "- Include validation scenarios",
        "- Exclude performance testing",
        "",
        "Output Format:",
        "Table",
        "",
        "Columns:",
        *columns,
        "",
        "Generate 25 test cases.",
    ]
    if include_length:
        lines.append("Limit response to 1000 words.")
    return "\n".join(lines)


def _template_explain_stlc(include_length: bool) -> str:
    lines = [
        "Act as a Senior QA Engineer.",
        "",
        "Explain Software Testing Life Cycle (STLC) to a beginner manual tester.",
        "",
        "Provide:",
        "1. Definition of STLC",
        "2. Each STLC phase with purpose and activities",
        "3. A real-world banking application example",
        "",
        "Output Format:",
        "Numbered list with brief explanations",
        "",
        "Requirements:",
        "- Use simple, professional language",
        "- Include practical examples",
        "- Exclude automation tool deep-dives",
    ]
    if include_length:
        lines.append("- Limit response to 1000 words")
    return "\n".join(lines)


def _template_explain_ai(include_length: bool) -> str:
    lines = [
        "Act as an AI Testing Expert.",
        "",
        "Explain AI Testing for manual testers with real-world examples.",
        "",
        "Provide:",
        "1. What AI Testing means",
        "2. How it differs from traditional testing",
        "3. Tools and techniques used in industry",
        "4. A practical example scenario",
        "",
        "Output Format:",
        "Structured sections with bullet points",
        "",
        "Requirements:",
        "- Target audience: beginner manual testers",
        "- Use clear, non-technical language where possible",
        "- Include at least one real-world example",
    ]
    if include_length:
        lines.append("- Limit response to 1000 words")
    return "\n".join(lines)


def _template_general(
    original: str,
    question: str,
    weakness_items: list[tuple[str, str]],
    include_length: bool,
) -> str:
    task = _extract_task(original, question)

    lines = [
        "Act as a subject-matter expert in the relevant domain.",
        "",
        f"Task: {task}.",
        "",
        "Provide clear, accurate, and structured output for a beginner-level audience.",
        "",
        "Provide:",
        "1. Definition or overview",
        "2. Key points or components",
        "3. A practical example",
        "",
        "Output Format:",
        "Table or numbered list with defined sections",
        "",
        "Columns / Sections:",
        "- Topic",
        "- Explanation",
        "- Example",
        "- Key Takeaway",
    ]
    if include_length:
        lines.append("")
        lines.append("Limit response to 1000 words.")
    return "\n".join(lines)
