from jinja2 import Template

def build_contradiction_prompt(context, question):
    template = Template("""
You are an AI assistant. Your task is to identify factual or logical contradictions in the following text.

A contradiction means:
- Two statements that cannot both be true
- Conflicting facts, numbers, dates, permissions, outcomes, or claims

Context:
{{ context }}

Question:
{{ question }}

Give a clear and concise explanation of any contradictions you find.
""")

    return template.render(context=context, question=question)
