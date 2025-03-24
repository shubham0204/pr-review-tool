from langgraph.graph import StateGraph, START, END
from typing import List, Literal
from models import Suggestion, AgentState
from llm import llm_gemini
from retrieval import get_pr_details, run_pylint_on_string
import requests
from chat_template import file_refactor_template, file_review_template
import pickle
from dotenv import load_dotenv
from langchain_core.output_parsers import JsonOutputParser

# load environment variables from the .env file
# present in the root directory
load_dotenv()

owner = input("Enter the owner of the repository: ")
repo = input("Enter the repository name: ")
pr_number = int(input("Enter the PR number: "))
llm = input("Enter the LLM model name: ")
if llm == "openai":
    model = llm_gemini()
else:
    model = llm_openai()

parser = JsonOutputParser(pydantic_object=List[Suggestion])
analyze_chain = file_review_template | model | parser
refactor_chain = file_refactor_template | llm_gemini()


def print_pr_details(pr):
    print(f"PR number: {pr.number}")
    print(f"PR title: {pr.title}")
    print(f"PR changed files: {len(pr.changed_files_urls)}")
    print(f"Issue title: {pr.issue.title}")
    print(f"Issue state: {pr.issue.state}")
    print(f"Issue created at: {pr.issue.created_at}")
    print(f"Issue updated at: {pr.issue.updated_at}")
    print(f"Issue body: {pr.issue.body}")


def node_get_pr_details(state: AgentState) -> AgentState:
    print("get_pr_details")
    pr = get_pr_details(owner, repo, pr_number)
    print_pr_details(pr)
    # TODO: Remove this
    pr.changed_files_urls = pr.changed_files_urls[0:1]
    state["pr"] = pr
    state["current_step"] = "find_file"
    return state


def router_check_file_idx(state: AgentState) -> Literal["analyze_file", "conclude"]:
    current_file_idx = state["current_file_idx"]
    pr = state["pr"]
    if current_file_idx < len(pr.changed_files_urls) - 1:
        state["current_file_idx"] = current_file_idx + 1
        return "pylint_file"
    else:
        return "conclude"


def node_pylint_file(state: AgentState) -> AgentState:
    print("""
          ===========================================================
          STEP: pylint_file
          """)
    pr = state["pr"]
    current_file_idx = state["current_file_idx"]
    state["current_file"] = {
        "url": pr.changed_files_urls[current_file_idx],
        "contents": requests.get(pr.changed_files_urls[current_file_idx]).text,
    }
    print("File fetched from URL")

    file_contents = state["current_file"]["contents"]
    response = run_pylint_on_string(file_contents)
    state["current_file"]["pylint_analysis"] = response
    print("""
          ==========================================================
          """)
    return state


def node_analyze_file(state: AgentState) -> AgentState:
    pr = state["pr"]
    file_url = state["current_file"]["url"]
    file_contents = state["current_file"]["contents"]

    print(f"""
          ===========================================================
          STEP: analyze_file
          
          Analyzing file: {file_url}
          Number of lines in file: {len(file_contents.splitlines())}
          """)

    response = analyze_chain.invoke(
        {
            "pylint_output": state["current_file"]["pylint_analysis"],
            "issue": pr.issue.body,
            "file_contents": file_contents,
        }
    )
    file_suggestion = {"file": file_url, "suggestions": response}

    print(f"""
          LLM generated suggestions: {len(response)}
          
          ===========================================================
          """)

    state["file_suggestions"].append(file_suggestion)
    return state


def node_refactor_file(state: AgentState) -> AgentState:
    print("""
          ============= REFACTORING FILE =============""")
    refactored_file_contents = refactor_chain.invoke(
        {
            "suggestions": state["file_suggestions"],
            "file_contents": state["current_file"]["contents"],
        }
    )
    refactored_file_contents = refactored_file_contents.content.strip("content=").strip(
        "```"
    )
    state["refactored_file_contents"].append(refactored_file_contents)
    state["current_file_idx"] = state["current_file_idx"] + 1
    return state


def node_conclude(state: AgentState) -> AgentState:
    with open("state.obj", "wb") as f:
        pickle.dump(state, f)
    return state


def build_workflow():
    workflow = StateGraph(AgentState)

    workflow.add_node("get_pr_details", node_get_pr_details)
    workflow.add_node("pylint_file", node_pylint_file)
    workflow.add_node("analyze_file", node_analyze_file)
    workflow.add_node("refactor_file", node_refactor_file)
    workflow.add_node("conclude", node_conclude)

    workflow.add_edge(START, "get_pr_details")
    workflow.add_edge("get_pr_details", "pylint_file")
    workflow.add_edge("pylint_file", "analyze_file")
    workflow.add_edge("analyze_file", "refactor_file")
    workflow.add_conditional_edges("refactor_file", router_check_file_idx)
    workflow.add_edge("conclude", END)

    workflow.set_entry_point("get_pr_details")
    return workflow.compile()


workflow = build_workflow()

state = {
    "pr": None,
    "current_step": "get_pr_details",
    "current_file_idx": 0,
    "current_file": None,
    "file_suggestions": [],
    "refactored_file_contents": [],
}
for step in workflow.stream(state):
    pass
