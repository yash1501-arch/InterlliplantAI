from openai import OpenAI

from app.config import settings


def call_llm(
    system_prompt: str,
    user_message: str,
    model: str | None = None,
    temperature: float = 0.1,
    max_tokens: int = 512,
) -> str:
    if settings.llm_provider == "groq" and settings.groq_api_key:
        return _call_groq(system_prompt, user_message, model, temperature, max_tokens)
    elif settings.llm_provider == "gemini" and settings.gemini_api_key:
        return _call_gemini(system_prompt, user_message, model, temperature, max_tokens)
    elif settings.openai_api_key:
        return _call_openai(system_prompt, user_message, model, temperature, max_tokens)
    raise ValueError("No LLM API key configured. Set GROQ_API_KEY, GEMINI_API_KEY, or OPENAI_API_KEY in .env")


def _call_openai(
    system_prompt: str,
    user_message: str,
    model: str | None = None,
    temperature: float = 0.1,
    max_tokens: int = 512,
) -> str:
    client = OpenAI(api_key=settings.openai_api_key)
    resp = client.chat.completions.create(
        model=model or settings.llm_model or "gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content.strip()


def _call_gemini(
    system_prompt: str,
    user_message: str,
    model: str | None = None,
    temperature: float = 0.1,
    max_tokens: int = 512,
) -> str:
    client = OpenAI(
        api_key=settings.gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    resp = client.chat.completions.create(
        model=model or "gemini-2.0-flash",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content.strip()


def _call_groq(
    system_prompt: str,
    user_message: str,
    model: str | None = None,
    temperature: float = 0.1,
    max_tokens: int = 512,
) -> str:
    client = OpenAI(
        api_key=settings.groq_api_key,
        base_url="https://api.groq.com/openai/v1",
    )
    resp = client.chat.completions.create(
        model=model or "llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content.strip()


def is_llm_available() -> bool:
    return (
        bool(settings.openai_api_key)
        or (settings.llm_provider == "gemini" and bool(settings.gemini_api_key))
        or (settings.llm_provider == "groq" and bool(settings.groq_api_key))
    )
