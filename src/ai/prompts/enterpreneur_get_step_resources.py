async def get_resources_for_step_prompt(step, sources_data):
    """
    Calls LLM to select most relevant resources from given data sources for this roadmap step.
    """
    sources_text = "\n\n".join([s["text"] for s in sources_data])
    prompt = f"""
    You are a startup resource recommendation expert.

    Given the following roadmap step:
    Title: {step['title']}
    Description: {step['description']}
    Objectives: {', '.join(step.get('objectives', []))}

    Below is a list of available data sources (with their details):

    ---
    {sources_text}
    ---

    Task:
    - Select the 3–5 most relevant data sources that would directly help with this step.
    - For each, return: title, short reason (why it's relevant), and URL if available.
    - Return only a valid JSON array of objects, no extra text.

    Example:
    [
      {{
        "title": "Yahoo Finance APIs",
        "reason": "Provides financial data needed for market analysis",
        "url": "https://finance.yahoo.com"
      }},
      ...
    ]
    """
    return prompt
