class PromptEvaluationResult:
    """
    Industry 5-pillar prompt evaluation (all sub-scores 0–1).
    Each pillar contributes 20% to the final Prompt Quality Score.

    Student-facing labels are exposed via pillars_for_ui().
    Detailed engineering metrics are exposed via technical_metrics_for_ui().
    """

    # One-line pillar questions for students (remember in ~5 minutes)
    PILLAR_QUESTIONS = {
        "clarity": "Can the AI understand what you want?",
        "specificity": "How detailed is your request?",
        "context": "Did you provide enough background?",
        "constraint": "Did you tell the AI how to respond?",
        "ambiguity": "Can the AI misunderstand your request?",
    }

    def __init__(self):
        # Pillar 1 — Clarity (20%)
        self.task_clarity = 0.0
        self.language_clarity = 0.0
        self.instruction_consistency = 0.0

        # Pillar 2 — Specificity (20%)
        self.scope_definition = 0.0
        self.persona_definition = 0.0
        self.detail_level = 0.0

        # Pillar 3 — Context Completeness (20%)
        self.business_context = 0.0
        self.domain_context = 0.0
        self.scenario_completeness = 0.0

        # Pillar 4 — Constraint Quality (internal engineering metrics)
        self.format_guidance = 0.0
        self.quantity_constraint = 0.0
        self.inclusion_rules = 0.0
        self.exclusion_rules = 0.0
        self.length_constraint = 0.0
        self.tone_guidance = 0.0

        # Pillar 5 — Ambiguity & Risk (20%)
        self.ambiguity_score = 0.0
        self.assumption_risk = 0.0
        self.conflicting_instructions = 0.0

        self.reasons: dict[str, str] = {}

        self.strengths: list[str] = []
        self.weakness_items: list[tuple[str, str]] = []
        self.optional_tips: list[tuple[str, str]] = []
        self.weaknesses: list[str] = []
        self.suggested_prompt: str = ""
        self.prompt_type: str = "explain"  # "explain" | "generate"

    def clarity_score(self) -> float:
        return _avg(self.task_clarity, self.language_clarity, self.instruction_consistency)

    def specificity_score(self) -> float:
        return _avg(self.scope_definition, self.persona_definition, self.detail_level)

    def context_score(self) -> float:
        return _avg(self.business_context, self.domain_context, self.scenario_completeness)

    def format_constraints_score(self) -> float:
        return self.format_guidance

    def scope_constraints_score(self) -> float:
        if self.prompt_type == "explain":
            return self.inclusion_rules
        if self.quantity_constraint >= 0.9 and self.exclusion_rules >= 0.9:
            return 1.0
        if self.quantity_constraint >= 0.9 and self.inclusion_rules >= 0.7:
            return _avg(self.quantity_constraint, self.inclusion_rules, self.exclusion_rules)
        return _avg(self.quantity_constraint, self.inclusion_rules, self.exclusion_rules)

    def response_constraints_score(self) -> float:
        return _avg(self.length_constraint, self.tone_guidance)

    def constraint_score(self) -> float:
        """Internal weighted rubric — adapts to prompt type."""
        if self.prompt_type == "explain":
            return (
                0.35 * self.format_guidance
                + 0.25 * self.inclusion_rules
                + 0.20 * self.length_constraint
                + 0.20 * self.tone_guidance
            )
        return (
            0.25 * self.format_guidance
            + 0.20 * self.quantity_constraint
            + 0.20 * self.inclusion_rules
            + 0.15 * self.exclusion_rules
            + 0.10 * self.length_constraint
            + 0.10 * self.tone_guidance
        )

    def ambiguity_risk_score(self) -> float:
        return _avg(self.ambiguity_score, self.assumption_risk, self.conflicting_instructions)

    def final_score(self) -> int:
        pillars = [
            self.clarity_score(),
            self.specificity_score(),
            self.context_score(),
            self.constraint_score(),
            self.ambiguity_risk_score(),
        ]
        return int(round(_avg(*pillars) * 100))

    def pillars_for_ui(self) -> list[tuple[str, float, str, list[tuple[str, float, str]]]]:
        """
        Student-facing pillars: name, score, one-line question, sub-metrics (max 3 each).
        """
        scope_label = "Scope definition" if self.prompt_type == "generate" else "Topic scope"
        return [
            (
                "Clarity",
                self.clarity_score(),
                self.PILLAR_QUESTIONS["clarity"],
                [
                    ("Task clarity", self.task_clarity, self.reasons.get("task_clarity", "")),
                    ("Language clarity", self.language_clarity, self.reasons.get("language_clarity", "")),
                    ("Instruction consistency", self.instruction_consistency, self.reasons.get("instruction_consistency", "")),
                ],
            ),
            (
                "Specificity",
                self.specificity_score(),
                self.PILLAR_QUESTIONS["specificity"],
                [
                    (scope_label, self.scope_definition, self.reasons.get("scope_definition", "")),
                    ("Persona definition", self.persona_definition, self.reasons.get("persona_definition", "")),
                    ("Detail level", self.detail_level, self.reasons.get("detail_level", "")),
                ],
            ),
            (
                "Context completeness",
                self.context_score(),
                self.PILLAR_QUESTIONS["context"],
                [
                    ("Business context", self.business_context, self.reasons.get("business_context", "")),
                    ("Domain context", self.domain_context, self.reasons.get("domain_context", "")),
                    ("Scenario completeness", self.scenario_completeness, self.reasons.get("scenario_completeness", "")),
                ],
            ),
            (
                "Constraint quality",
                self.constraint_score(),
                self.PILLAR_QUESTIONS["constraint"],
                [
                    ("Format constraints", self.format_constraints_score(), self.reasons.get("format_guidance", "")),
                    ("Scope constraints", self.scope_constraints_score(), self._scope_constraints_reason()),
                    ("Response constraints", self.response_constraints_score(), self._response_constraints_reason()),
                ],
            ),
            (
                "Ambiguity & risk",
                self.ambiguity_risk_score(),
                self.PILLAR_QUESTIONS["ambiguity"],
                [
                    ("Ambiguity score", self.ambiguity_score, self.reasons.get("ambiguity_score", "")),
                    ("Assumption risk", self.assumption_risk, self.reasons.get("assumption_risk", "")),
                    ("Conflicting instructions", self.conflicting_instructions, self.reasons.get("conflicting_instructions", "")),
                ],
            ),
        ]

    def technical_metrics_for_ui(self) -> list[tuple[str, list[tuple[str, float, str]]]]:
        """Detailed engineering metrics for instructors (collapsed in UI)."""
        constraint_metrics = [
            ("Output format", self.format_guidance, self.reasons.get("format_guidance", "")),
            ("Quantity constraint", self.quantity_constraint, self.reasons.get("quantity_constraint", "")),
            ("Inclusion rules", self.inclusion_rules, self.reasons.get("inclusion_rules", "")),
            ("Exclusion rules", self.exclusion_rules, self.reasons.get("exclusion_rules", "")),
            ("Length constraint", self.length_constraint, self.reasons.get("length_constraint", "")),
            ("Tone / persona guidance", self.tone_guidance, self.reasons.get("tone_guidance", "")),
        ]
        return [("Constraint quality — technical breakdown", constraint_metrics)]

    def _scope_constraints_reason(self) -> str:
        if self.prompt_type == "explain":
            return self.reasons.get("inclusion_rules", "What content must be covered.")
        parts = [
            self.reasons.get("quantity_constraint", ""),
            self.reasons.get("inclusion_rules", ""),
            self.reasons.get("exclusion_rules", ""),
        ]
        return " · ".join(p for p in parts if p)

    def _response_constraints_reason(self) -> str:
        parts = [
            self.reasons.get("length_constraint", ""),
            self.reasons.get("tone_guidance", ""),
        ]
        return " · ".join(p for p in parts if p)


def _avg(*values: float) -> float:
    return sum(values) / len(values) if values else 0.0
