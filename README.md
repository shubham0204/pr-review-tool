# PR Review Tool

![workflow_diagram](/static/workflow.png)

This project demonstrates a simple PR review tool built with [LangGraph](https://www.langchain.com/langgraph) in Python. The PR review agent performs the following steps:

1. Gather PR and corresponding issue details from the given PR number (or URL)
2. Perform `pylint` analysis on each file and store the analysis
3. Provide the issue description, modified file and the `pylint` analysis to a LLM (using Google Gemini currently) and ask it to provide suggestions in the JSON format.
4. Rewrite the contents of the file using the suggestions provided in (3)
5. Go to (3) with the next modified file in the PR

## Setup

### Prerequisites

- [uv](https://docs.astral.sh/uv/)
- A Google Gemini API key stored in a `.env` file,

```
GOOGLE_API_KEY=AIza...
```

### Steps

```bash
# Clone the repo
git clone --depth=1 https://github.com/shubham0204/pr-review-tool
cd pr-review-tool

# Setup venv and deps
uv pip install -r pyproject.toml

# Execute the code-review script
uv run prreview/workflow.py
uv run streamlit run prreview/app.py

# (Optional) Execute tests
pytest prreview/tests.py
```