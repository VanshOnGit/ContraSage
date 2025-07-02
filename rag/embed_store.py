from jinja2 import Template

def build_contradiction_prompt(context, question):
    template = Template("""
You are an AI assistant. Your task is to identify contradictions in work policy documents.

Context:
{{ context }}

Question:
{{ question }}

Give a clear and concise explanation of any contradiction you find.
""")
    return template.render(context=context, question=question)
