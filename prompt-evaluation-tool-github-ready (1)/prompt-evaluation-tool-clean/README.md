# Prompt Evaluation Tool

A Streamlit-based prompt quality evaluator for analyzing prompts before they are sent to an LLM. The project scores a prompt across five quality pillars and provides actionable feedback, weaknesses, suggestions, and an improved prompt.

## What it evaluates

- **Clarity** — whether the task and instructions are understandable
- **Specificity** — whether scope, persona, and detail are defined
- **Context completeness** — whether enough business/domain context is provided
- **Constraint quality** — whether format, scope, length, and response requirements are defined
- **Ambiguity & risk** — whether the prompt leaves room for conflicting interpretations or assumptions

The five pillar scores are combined into a **Prompt Quality Score out of 100**.

## Features

- Streamlit user interface
- 5-pillar prompt quality scoring
- Per-metric explanations
- Strength and weakness detection
- Prompt-improvement suggestions
- Suggested enhanced prompt
- Optional Azure OpenAI response preview
- Built-in demo validation suite

## Project structure

```text
.
├── app.py
├── main.py
├── run_demo_validation.py
├── config.py
├── requirements.txt
├── evaluator/
│   ├── demo_examples.py
│   ├── prompt_framework.py
│   ├── result.py
│   └── suggestions.py
├── llm/
│   └── azure_client.py
├── models/
│   └── test_case.py
└── runner/
    └── test_runner.py
```

## Run locally

Create a virtual environment, install the dependencies, then launch the Streamlit app:

```bash
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Run the included validation examples with:

```bash
python main.py
```

## Optional Azure OpenAI preview

Prompt scoring works without an API key. The Azure OpenAI integration is only used when the optional LLM preview is enabled.

1. Copy `.env.example` to `.env`.
2. Add your own Azure OpenAI values to `.env`.
3. Never commit `.env` or real credentials.

## Security

This repository intentionally does **not** contain API keys or credentials. Keep secrets in local environment variables or a local `.env` file that is excluded by `.gitignore`.

## Portfolio note

This project demonstrates prompt-quality analysis, prompt engineering, LLM testing concepts, QA-oriented evaluation logic, Python, and Streamlit. If any part of the original material came from coursework, training, or another author, add the appropriate attribution and confirm that you have permission before publishing it publicly.
