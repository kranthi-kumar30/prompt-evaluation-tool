from evaluator.prompt_framework import evaluate_prompt
from evaluator.result import PromptEvaluationResult
from llm.azure_client import call_llm


def run_prompt_evaluation(prompt: str, question: str = "", preview_llm: bool = False) -> tuple[PromptEvaluationResult, str | None]:
    """
    Evaluate prompt quality using the 5-pillar framework.
    Optionally preview what the LLM would answer (not used for scoring).
    """
    result = evaluate_prompt(prompt, question)

    llm_preview = None
    if preview_llm and prompt.strip() and question.strip():
        full_prompt = f"{prompt.strip()}\nUser: {question.strip()}"
        llm_preview = call_llm(full_prompt)

    return result, llm_preview
