def parse_refusal(reply: str):
    """Return the reason if the LLM refused, else None."""
    text = reply.strip()
    if text.upper().startswith("REFUSE:"):
        return text.split(":", 1)[1].strip() or "No reason given"
    return None