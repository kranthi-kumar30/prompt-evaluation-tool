from openai import AzureOpenAI
from config import OPENAI_API_KEY, AZURE_ENDPOINT, DEPLOYMENT_NAME, API_VERSION


def call_llm(prompt: str) -> str:
    """Optional Azure OpenAI preview. Prompt scoring itself does not require an API key."""
    if not OPENAI_API_KEY or not AZURE_ENDPOINT:
        return "LLM preview is disabled. Configure Azure OpenAI values in a local .env file."

    try:
        client = AzureOpenAI(
            api_key=OPENAI_API_KEY,
            api_version=API_VERSION,
            azure_endpoint=AZURE_ENDPOINT,
        )
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        if "content_filter" in str(exc):
            return "BLOCKED_BY_POLICY"
        return f"ERROR: {exc}"
