"""
Industry-standard 5-pillar PROMPT evaluation (prompt + question text only).
"""

import re

from evaluator.result import PromptEvaluationResult

ACTION_VERBS = [
    "explain", "describe", "create", "write", "list", "compare", "summarize",
    "generate", "design", "analyze", "evaluate", "teach", "help", "answer",
]

ROLE_PATTERNS = [
    "act as", "you are", "role:", "as a", "as an", "senior", "architect",
    "expert", "specialist", "engineer", "analyst",
]

AUDIENCE_PATTERNS = [
    "beginner", "expert", "student", "tester", "developer", "manager",
    "freshers", "fresher", "manual tester", "for beginners", "for experts",
]

SCOPE_PATTERNS = [
    "lifecycle", "stlc", "framework", "login", "authentication", "mfa", "otp",
    "selenium", "api", "test case", "test plan", "functional", "negative",
    "edge case", "boundary", "validation", "banking", "application",
]

FORMAT_PATTERNS = [
    "table", "bullet", "bullets", "numbered", "json", "markdown", "columns:",
    "output format", "format:", "comparison table", "output in a table", "in a table",
]

QUANTITY_PATTERNS = [
    r"generate\s+\d+",
    r"\d+\s+test\s+cases?",
    r"return\s+\d+",
    r"provide\s+\d+",
    r"exactly\s+\d+",
    r"at least\s+\d+",
    r"list\s+\d+",
]

INCLUSION_PATTERNS = [
    "include boundary", "include validation", "must include", "edge case",
    "negative", "functional", "scenario", "requirements:", "features:",
]

EXPLAIN_INCLUSION_PATTERNS = [
    "provide:", "cover", "sections", "include practical", "include examples",
    "comprehensively", "requirements:", "explain", "describe",
]

EXCLUSION_PATTERNS = [
    "exclude", "do not include", "don't include", "without", "avoid",
    "not include", "skip",
]

LENGTH_PATTERNS = [
    r"\b\d+\s*words?\b", r"less than \d+", r"maximum \d+", r"limit.*\d+",
    r"brief", r"concise", r"under \d+\s*words?",
]

TONE_PATTERNS = [
    "formal", "professional", "friendly", "neutral", "technical",
    "conversational", "respectful",
]

DOMAIN_PATTERNS = [
    "qa", "testing", "banking", "finance", "healthcare", "chemistry",
    "software", "selenium", "automation", "api", "technology", "ai testing",
    "chatbot", "chatbots",
]

SPECIFIC_DELIVERABLES = [
    "test case", "test cases", "functional test", "login test", "summary",
    "table", "report", "test plan", "scenarios",
]

FEATURE_KEYWORDS = [
    "username", "password", "otp", "remember", "mfa", "forgot", "lock",
    "failure", "failures", "authentication", "account",
]

UNCLEAR_LANGUAGE = [
    "do the needful", "needful", "kindly do", "kindly", "regarding testing",
    "something", "stuff", "things", "etc",
]

AMBIGUOUS_TERMS = {
    "apple": ["fruit", "company", "technology"],
    "python": ["programming language", "snake"],
    "java": ["programming language", "island", "coffee"],
    "mercury": ["planet", "chemical element"],
}

VAGUE_PHRASES = [
    "explain testing", "write about", "tell me about", "tell me about testing",
    "answer this", "help me", "do this", "explain it",
]

VAGUE_SCOPE_TOPICS = [
    "explain testing", "testing", "write about", "help me", "answer this",
    "do this", "explain it", "tell me about",
]


def _has_vague_deliverable(lower: str) -> bool:
    return bool(re.search(r"\b(something|anything|stuff|things)\b", lower))


def _has_specific_deliverable(lower: str) -> bool:
    return any(d in lower for d in SPECIFIC_DELIVERABLES)


def _count_feature_details(prompt: str, lower: str) -> int:
    keyword_hits = sum(1 for k in FEATURE_KEYWORDS if k in lower)
    comma_parts = len([p for p in prompt.split(",") if p.strip()])
    return keyword_hits + (comma_parts if comma_parts >= 2 else 0)


def _has_conflicting_quantities(lower: str) -> bool:
    nums = [int(n) for n in re.findall(r"(\d+)\s*test\s*cases?", lower)]
    nums += [int(n) for n in re.findall(r"generate\s+(\d+)", lower)]
    only_match = re.search(r"\bonly\s+(\d+)", lower)
    if only_match:
        nums.append(int(only_match.group(1)))
    return len(set(nums)) > 1


def _has_detailed_vs_short_limit(lower: str) -> bool:
    if not any(x in lower for x in ["detailed", "comprehensive", "in depth", "thorough"]):
        return False
    word_match = re.search(r"(\d+)\s*words?", lower)
    return bool(word_match and int(word_match.group(1)) <= 100)


def _is_generic_generate_scope(lower: str) -> bool:
    return bool(re.match(
        r"^(generate|create|write)\s+test\s+cases?\.?$",
        lower.strip().rstrip("."),
    ))


def _is_vague_scope(combined: str, lower: str) -> bool:
    if _has_any(combined, VAGUE_PHRASES):
        return True
    if _word_count(combined) <= 4 and any(t in lower for t in ["testing", "help", "stuff", "thing"]):
        return True
    return any(lower.strip().rstrip(".") == t for t in VAGUE_SCOPE_TOPICS)


CONFLICT_PAIRS = [
    (["brief", "concise", "short"], ["detailed", "comprehensive", "in depth", "thorough"]),
    (["only use provided", "only based on"], ["use your knowledge", "use external"]),
]


def _normalize(text: str) -> str:
    return text.strip().lower().replace("'", "'")


def _combined_text(prompt: str, question: str) -> str:
    return f"{prompt.strip()}\n{question.strip()}".strip()


def _word_count(text: str) -> int:
    return len(text.split())


def _has_any(text: str, patterns: list[str]) -> bool:
    return any(p in _normalize(text) for p in patterns)


def _has_regex(text: str, patterns: list[str]) -> bool:
    t = _normalize(text)
    return any(re.search(p, t) for p in patterns)


def _count_signals(text: str, patterns: list[str]) -> int:
    t = _normalize(text)
    return sum(1 for p in patterns if p in t)


def _find_ambiguous_in_question(question: str) -> list[str]:
    tokens = re.findall(r"[a-z]+", _normalize(question))
    return [t for t in tokens if t in AMBIGUOUS_TERMS]


def _find_ambiguous_in_text(text: str) -> list[str]:
    tokens = re.findall(r"[a-z]+", _normalize(text))
    return [t for t in tokens if t in AMBIGUOUS_TERMS]


def _prompt_disambiguates(prompt: str, term: str) -> bool:
    p = _normalize(prompt)
    meanings = AMBIGUOUS_TERMS.get(term, [])
    return any(any(w in p for w in m.split()) for m in meanings)


def _detect_prompt_type(prompt: str, question: str) -> str:
    """Classify prompt as generate (artifacts) vs explain (Q&A)."""
    text = _normalize(_combined_text(prompt, question))
    if any(x in text for x in ["test case", "test cases", "write test", "create test", "generate test"]):
        return "generate"
    if _has_regex(text, QUANTITY_PATTERNS) and "test" in text:
        return "generate"
    if any(x in text for x in ["generate", "create", "list"]) and any(
        x in text for x in ["test", "cases", "scenarios"]
    ):
        return "generate"
    return "explain"


def _score_format(prompt: str) -> tuple[float, str]:
    p = _normalize(prompt)
    has_format = _has_any(prompt, FORMAT_PATTERNS)
    has_columns = "columns:" in p or "column:" in p
    has_structure = bool(re.search(r"[-*•]\s+\w+", prompt))

    if has_format and has_columns:
        return 1.0, "Structured output format with defined columns."
    if has_format:
        return 0.9, "Output format specified (table, list, etc.)."
    if has_structure:
        return 0.6, "Some structure present but no explicit output format."
    return 0.1, "No output format specified."


def _score_inclusion(prompt: str, prompt_type: str) -> tuple[float, str]:
    if prompt_type == "explain":
        hits = _count_signals(prompt, EXPLAIN_INCLUSION_PATTERNS)
        if hits >= 2:
            return 1.0, "Content scope defined (sections, examples, coverage)."
        if hits >= 1:
            return 0.8, "Some content scope guidance present."
        return 0.3, "Specify what sections or topics must be covered."
    hits = _count_signals(prompt, INCLUSION_PATTERNS)
    if hits >= 2:
        return 1.0, "Strong inclusion rules (scenarios, boundaries, validation, etc.)."
    if hits >= 1:
        return 0.7, "Some inclusion rules present."
    return 0.1, "No inclusion rules (what must be covered)."


def _score_exclusion(prompt: str, prompt_type: str) -> tuple[float, str]:
    if prompt_type == "explain":
        if _has_any(prompt, EXCLUSION_PATTERNS):
            return 1.0, "Scope boundaries defined (what to exclude)."
        return 1.0, "N/A — exclusion rules are optional for explanatory prompts."
    if _has_any(prompt, EXCLUSION_PATTERNS):
        return 1.0, "Exclusion rules defined (what to leave out)."
    return 0.0, "No exclusion rules (e.g. 'Exclude performance testing')."


def _score_quantity(prompt: str, prompt_type: str) -> tuple[float, str]:
    if prompt_type == "explain":
        return 1.0, "N/A — quantity constraints apply to generation tasks, not Q&A."
    if _has_regex(prompt, QUANTITY_PATTERNS):
        return 1.0, "Quantity constraint defined (e.g. number of test cases)."
    return 0.0, "No quantity constraint (e.g. 'Generate 25 test cases')."


def _score_length(prompt: str, question: str) -> tuple[float, str]:
    combined = _combined_text(prompt, question)
    if _has_regex(combined, LENGTH_PATTERNS):
        return 1.0, "Response length constraint is defined."
    # Explicit quantity (e.g. "Generate 25 test cases") strongly bounds output size
    if _has_regex(prompt, QUANTITY_PATTERNS):
        return 1.0, "Quantity constraint bounds response size (e.g. fixed number of test cases)."
    return 0.0, "No response length or quantity guidance."


def _has_clear_topic(combined: str, lower: str) -> bool:
    return any([
        "task:" in lower,
        bool(re.search(r"\bwhat is\b", lower)),
        bool(re.search(r"\bwhat are\b", lower)),
        bool(re.search(r"\bexplain\b", lower)),
        bool(re.search(r"\bdescribe\b", lower)),
        bool(re.search(r"\bhow (does|do|to)\b", lower)),
        bool(re.search(r"\btell me about\b", lower)),
    ])


def _has_structured_sections(prompt: str, lower: str) -> bool:
    return any([
        "sections:" in lower or "columns:" in lower or "column:" in lower,
        "provide:" in lower,
        "requirements:" in lower,
        bool(re.search(r"[-*•]\s+\w+", prompt)),
        bool(re.search(r"\d+\.\s+\w+", prompt)),
    ])


def _score_scope(
    prompt: str,
    question: str,
    combined: str,
    lower: str,
    prompt_type: str,
    is_structured: bool,
) -> tuple[float, str]:
    if prompt_type == "explain":
        topic_clear = _has_clear_topic(combined, lower)
        has_sections = _has_structured_sections(prompt, lower)
        if _is_vague_scope(combined, lower) and not has_sections:
            return 0.35, "Scope is too broad — narrow the topic (e.g. STLC, Selenium, API testing)."
        if topic_clear and (has_sections or is_structured):
            return 1.0, "Topic and scope clearly defined for Q&A."
        if topic_clear and _word_count(combined) >= 12:
            return 0.9, "Topic stated; structured sections strengthen scope."
        if topic_clear:
            return 0.6, "Topic hinted but too vague — add a specific Task line."
        if question.strip() and _word_count(question) >= 3:
            return 0.75, "Scope inferred from question; add an explicit Task line."
        return 0.3, "Define the topic or question explicitly (e.g. Task: What is X)."

    scope_hits = _count_signals(combined, SCOPE_PATTERNS)
    if _is_generic_generate_scope(lower):
        return 0.25, "Scope is too broad — specify feature or page (e.g. login page)."
    has_narrow_scope = any(x in lower for x in [
        "login page", "login", "registration", "checkout", "payment", "api", "module",
    ])
    if has_narrow_scope and "test case" in lower:
        return 1.0, "Scope is specific (feature, page, or deliverable)."
    if scope_hits >= 2 and has_narrow_scope:
        return 1.0, "Scope is specific (feature, domain, deliverable)."
    if scope_hits >= 1 and has_narrow_scope:
        return 0.9, "Scope is specific (feature, domain, deliverable)."
    if scope_hits >= 1:
        return 0.45, "Scope is too broad — narrow to a page or feature."
    return 0.2, "Scope is too broad — specify feature, module, or deliverable."


def _score_detail_level(prompt: str, lower: str, prompt_type: str) -> tuple[float, str]:
    feature_score = _count_feature_details(prompt, lower)
    if feature_score >= 4:
        return 1.0, "Rich detail — multiple features or fields listed."
    if feature_score >= 2:
        return 0.9, "Good detail — specific items provided."

    detail_signals = sum([
        "features:" in lower or "requirements:" in lower,
        _has_structured_sections(prompt, lower),
        _word_count(prompt) >= 50,
        bool(re.search(r"\d+\.", prompt)),
    ])
    score = min(1.0, 0.25 + detail_signals * 0.25)
    if _word_count(prompt) <= 3 and feature_score < 2:
        score = min(score, 0.25)
    if prompt_type == "explain" and score >= 0.75:
        return score, "Rich structural detail (sections, requirements, output format)."
    if score >= 0.8:
        return score, "Rich structural detail (features, requirements, sections)."
    return score, "Add more explicit sections, features, or requirements."


def _score_persona(prompt: str) -> tuple[float, str]:
    """Persona = who the AI should act as (e.g. Senior QA Engineer). Not the audience."""
    if _has_any(prompt, ROLE_PATTERNS):
        return 1.0, "Persona defined (e.g. Act as Senior QA Engineer)."
    return 0.3, "Add a persona — e.g. Act as a Senior QA Engineer."


def _score_business_context(
    prompt: str,
    question: str,
    combined: str,
    lower: str,
    prompt_type: str,
) -> tuple[float, str]:
    """Business / system / audience background — not scenario detail."""
    if prompt_type == "explain":
        signals = sum([
            "task:" in lower or bool(question.strip()),
            "context:" in lower,
            _has_any(combined, AUDIENCE_PATTERNS),
            "beginner" in lower or "expert" in lower or "audience" in lower,
            any(t in lower for t in ["application", "system", "feature", "scenario"]),
        ])
        if signals >= 3:
            return 1.0, "Business or audience background provided."
        if signals >= 2:
            return 0.85, "Some background context for the topic."
        if signals >= 1:
            return 0.65, "Minimal background — add audience or system context."
        return 0.3, "Add business or audience context (who this is for, what system)."

    has_business_system = bool(re.search(
        r"\b(online banking|banking application|banking app|application|portal|platform|system|module)\b",
        lower,
    ))
    has_login = "login" in lower

    if has_login and not has_business_system:
        return 0.35, "Login mentioned but business/application system is missing."

    signals = sum([
        has_business_system,
        "banking" in lower,
        "features:" in lower,
    ])
    if signals >= 2:
        return 1.0, "Clear business context (application, page, or system)."
    if signals >= 1:
        return 0.65, "Partial business context — name the full application or system."
    return 0.2, "Business context missing — specify application, page, or system."


def _score_scenario_completeness(
    prompt: str,
    question: str,
    combined: str,
    lower: str,
    prompt_type: str,
    amb_terms: list[str],
) -> tuple[float, str]:
    """Whether the scenario has enough detail to execute the task."""
    gaps = _detect_missing_context(question, prompt, prompt_type, amb_terms)
    gap_score = max(0.0, 1.0 - len(gaps) * 0.25)

    if prompt_type == "explain":
        richness = sum([
            _has_structured_sections(prompt, lower),
            _count_signals(prompt, EXPLAIN_INCLUSION_PATTERNS) >= 2,
            "example" in lower,
            "requirements:" in lower,
            _count_feature_details(prompt, lower) >= 2,
            "otp" in lower or "account lock" in lower or "failure" in lower,
        ])
        detail = min(1.0, 0.35 + richness * 0.15)
        if any(x in lower for x in ["otp", "account lock", "lock after", "failure", "failures"]):
            detail = 1.0
        if _word_count(prompt) <= 4 and _count_feature_details(prompt, lower) < 2:
            detail = min(detail, 0.3)
        score = _avg_local(gap_score, detail)
        if _word_count(prompt) <= 4 and _count_feature_details(prompt, lower) < 2:
            score = min(score, 0.35)
    else:
        richness = sum([
            "features:" in lower,
            "requirements:" in lower,
            _count_signals(prompt, INCLUSION_PATTERNS) >= 2,
            "boundary" in lower or "validation" in lower or "edge" in lower,
        ])
        detail = min(1.0, 0.3 + richness * 0.2)
        if "features:" not in lower and "requirements:" not in lower:
            score = min(gap_score, 0.45)
            if gaps:
                return score, f"Scenario gaps: {', '.join(gaps)}."
            return score, "Add Features and Requirements to complete the scenario."
        score = _avg_local(gap_score, detail)

    if score >= 0.85 and not gaps:
        return score, "Scenario is complete with required details."
    if gaps:
        return score, f"Scenario gaps: {', '.join(gaps)}."
    return score, "Add features, requirements, or coverage details to complete the scenario."


def _score_domain_context(combined: str, lower: str, prompt_type: str) -> tuple[float, str]:
    domain_hits = _count_signals(combined, DOMAIN_PATTERNS)
    if "this feature" in lower and domain_hits == 0:
        return 0.2, "Specify the business or technical domain."
    if prompt_type == "explain":
        if domain_hits >= 1:
            return 1.0, "Domain context specified (QA, banking, technology, etc.)."
        if any(t in lower for t in ["apple", "microsoft", "google", "amazon", "stlc", "selenium", "banking"]):
            return 0.9, "Domain inferable from the topic."
        if "as applicable" in lower or "relevant domain" in lower:
            return 0.85, "Domain guidance allows contextual adaptation."
        return 0.25, "Specify the business or technical domain."
    if domain_hits >= 1:
        return min(1.0, 0.5 + domain_hits * 0.25), "Clear domain context (QA, banking, tech, etc.)."
    return 0.2, "Specify the business or technical domain."


def _avg_local(*values: float) -> float:
    return sum(values) / len(values) if values else 0.0


def _score_ambiguity(
    prompt: str,
    question: str,
    combined: str,
    prompt_type: str,
    is_structured: bool,
    vague: bool,
    amb_terms: list[str],
) -> tuple[float, str]:
    lower = _normalize(combined)
    if _has_any(combined, ["tell me about testing", "tell me about"]):
        return 0.3, "Prompt is broad — multiple interpretations possible."
    if amb_terms and not any(_prompt_disambiguates(prompt, t) for t in amb_terms):
        if prompt_type == "explain" and is_structured and (
            "clarification" in _normalize(prompt) or "disambiguat" in _normalize(prompt)
        ):
            return 0.85, (
                f"Term(s) may be ambiguous ({', '.join(amb_terms)}) — "
                "clarification guidance included."
            )
        return 0.2, f"Ambiguous term(s): {', '.join(amb_terms)} — specify intended meaning."
    if _count_signals(combined, DOMAIN_PATTERNS) >= 2 and _word_count(combined) >= 6:
        return 1.0, "Specific topic with clear domain — low ambiguity."
    if is_structured and not vague:
        return 1.0, "Low ambiguity — prompt is specific and structured."
    if not vague and _has_specific_deliverable(lower):
        return 0.9, "Low ambiguity."
    if vague:
        return 0.35, "Prompt may be interpreted in multiple ways."
    return 0.85, "Low ambiguity."


def _score_assumption_risk(
    prompt_type: str,
    scope: float,
    business_context: float,
    persona: float,
    ambiguity: float,
    amb_terms: list[str],
) -> tuple[float, str]:
    risk = 0.0
    if scope < 0.6:
        risk += 0.3
    if prompt_type == "generate" and business_context < 0.5:
        risk += 0.25
    elif prompt_type == "explain" and business_context < 0.5:
        risk += 0.15
    if persona < 0.5:
        if not (prompt_type == "generate" and business_context >= 0.8 and scope >= 0.8):
            risk += 0.2
    if amb_terms and ambiguity < 0.5:
        risk += 0.2
    score = max(0.0, 1.0 - risk)
    if score >= 0.8:
        return score, "Low assumption risk — prompt defines role, scope, and context."
    return score, "Model may need to guess missing details."


def _score_tone(prompt: str) -> tuple[float, str]:
    if _has_any(prompt, ROLE_PATTERNS):
        return 1.0, "Role/persona clearly defines tone and perspective."
    if _has_any(prompt, TONE_PATTERNS) or "professional language" in _normalize(prompt):
        return 0.9, "Tone guidance present."
    return 0.3, "No tone or role guidance."


def evaluate_prompt(prompt: str, question: str = "") -> PromptEvaluationResult:
    result = PromptEvaluationResult()
    p = prompt.strip()
    q = question.strip()
    combined = _combined_text(p, q)
    lower = _normalize(combined)

    if not p:
        result.weaknesses = ["Prompt is empty."]
        return result

    prompt_type = _detect_prompt_type(p, q)
    result.prompt_type = prompt_type

    is_structured = _word_count(p) >= 60 or "requirements:" in lower or "features:" in lower

    # ── Pillar 1: Clarity ──────────────────────────────────────────────
    has_action = _has_any(p, ACTION_VERBS)
    vague = _has_any(combined, VAGUE_PHRASES) or _has_any(combined, UNCLEAR_LANGUAGE)

    if has_action and _has_specific_deliverable(lower) and not _has_vague_deliverable(lower) and not vague:
        result.task_clarity = 1.0
    elif has_action and not _has_vague_deliverable(lower):
        result.task_clarity = 0.55
    else:
        result.task_clarity = 0.2
    result.reasons["task_clarity"] = (
        "Clear task and deliverable defined."
        if result.task_clarity >= 0.8
        else "Specify a clear action and expected deliverable."
    )

    unclear_hits = sum(1 for phrase in UNCLEAR_LANGUAGE if phrase in lower)
    filler = len(re.findall(r"\b(thing|stuff|something|etc|maybe)\b", lower))
    result.language_clarity = max(0.2, 1.0 - unclear_hits * 0.35 - filler * 0.15 - (0.35 if vague else 0))
    result.reasons["language_clarity"] = (
        "Language is direct and professional."
        if result.language_clarity >= 0.7
        else "Wording is vague — use specific task language."
    )

    conflicts = _detect_conflicts(p)
    result.instruction_consistency, result.reasons["instruction_consistency"] = _score_instruction_consistency(p, conflicts)

    # ── Pillar 2: Specificity (type-aware) ───────────────────────────────
    result.scope_definition, result.reasons["scope_definition"] = _score_scope(
        p, q, combined, lower, prompt_type, is_structured
    )

    result.persona_definition, result.reasons["persona_definition"] = _score_persona(p)

    result.detail_level, result.reasons["detail_level"] = _score_detail_level(p, lower, prompt_type)

    # ── Pillar 3: Context Completeness (type-aware) ─────────────────────
    result.business_context, result.reasons["business_context"] = _score_business_context(
        p, q, combined, lower, prompt_type
    )

    amb_terms_early = _find_ambiguous_in_question(q) or _find_ambiguous_in_text(p)

    result.domain_context, result.reasons["domain_context"] = _score_domain_context(
        combined, lower, prompt_type
    )

    result.scenario_completeness, result.reasons["scenario_completeness"] = _score_scenario_completeness(
        p, q, combined, lower, prompt_type, amb_terms_early
    )

    # ── Pillar 4: Constraint Quality (type-aware weighted) ───────────────
    result.format_guidance, result.reasons["format_guidance"] = _score_format(p)
    result.quantity_constraint, result.reasons["quantity_constraint"] = _score_quantity(p, prompt_type)
    result.inclusion_rules, result.reasons["inclusion_rules"] = _score_inclusion(p, prompt_type)
    result.exclusion_rules, result.reasons["exclusion_rules"] = _score_exclusion(p, prompt_type)
    result.length_constraint, result.reasons["length_constraint"] = _score_length(p, q)
    result.tone_guidance, result.reasons["tone_guidance"] = _score_tone(p)

    # ── Pillar 5: Ambiguity & Risk (type-aware) ────────────────────────
    amb_terms = amb_terms_early
    result.ambiguity_score, result.reasons["ambiguity_score"] = _score_ambiguity(
        p, q, combined, prompt_type, is_structured, vague, amb_terms
    )
    result.assumption_risk, result.reasons["assumption_risk"] = _score_assumption_risk(
        prompt_type,
        result.scope_definition,
        result.business_context,
        result.persona_definition,
        result.ambiguity_score,
        amb_terms,
    )

    result.conflicting_instructions = result.instruction_consistency
    result.reasons["conflicting_instructions"] = result.reasons["instruction_consistency"]

    from evaluator.suggestions import build_suggestions, build_strengths

    result.strengths = build_strengths(prompt, result)
    result.weakness_items, result.optional_tips, result.suggested_prompt = build_suggestions(
        prompt, question, result
    )
    result.weaknesses = [w for w, _ in result.weakness_items]

    return result


def _score_instruction_consistency(prompt: str, conflicts: list[str]) -> tuple[float, str]:
    lower = _normalize(prompt)
    if _has_conflicting_quantities(lower):
        return 0.3, "Conflicting quantities — e.g. 20 test cases and only 5."
    if _has_detailed_vs_short_limit(lower):
        return 0.35, "Conflicting instructions — detailed vs very short word limit."
    if conflicts:
        score = max(0.0, 1.0 - len(conflicts) * 0.4)
        return score, f"Conflicts detected: {'; '.join(conflicts)}."
    return 1.0, "No contradictory instructions."


def _detect_conflicts(prompt: str) -> list[str]:
    lower = _normalize(prompt)
    found = []
    for group_a, group_b in CONFLICT_PAIRS:
        if any(x in lower for x in group_a) and any(x in lower for x in group_b):
            found.append(f"'{group_a[0]}' vs '{group_b[0]}'")
    if _has_conflicting_quantities(lower):
        found.append("conflicting quantities (e.g. 20 vs 5 test cases)")
    if _has_detailed_vs_short_limit(lower):
        found.append("'detailed' vs short word limit")
    return found


def _detect_missing_context(
    question: str,
    prompt: str,
    prompt_type: str,
    amb_terms: list[str],
) -> list[str]:
    q, p = _normalize(question), _normalize(prompt)
    gaps = []
    if prompt_type == "generate":
        if "test case" in q and "test case" not in p and "generate" not in p:
            gaps.append("test scenario details")
        if "features:" not in p and _word_count(prompt) < 80:
            if any(x in q for x in ["login", "banking", "page", "module"]):
                gaps.append("feature or system context")
    if amb_terms and not any(_prompt_disambiguates(prompt, t) for t in amb_terms):
        if prompt_type == "explain":
            if "clarification" not in p and "disambiguat" not in p:
                gaps.append("disambiguation for ambiguous term")
        else:
            gaps.append("disambiguation for ambiguous question")
    return gaps
