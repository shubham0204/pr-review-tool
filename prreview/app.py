import streamlit as st
import pickle


def main():
    st.set_page_config(page_title="AgentState Viewer", layout="wide")
    st.title("Agent State Viewer")
    with open("state.obj", "rb") as f:
        agent_state = pickle.load(f)
    display_agent_state(agent_state)


def display_agent_state(agent_state):
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Suggestions", "Refactored Files"])
    with tab1:
        display_overview(agent_state)
    with tab2:
        display_suggestions(agent_state)
    with tab3:
        display_refactored_files(agent_state)


def display_overview(agent_state):
    st.header("Pull Request Information")
    pr = agent_state["pr"]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Pull Request")
        st.write(f"**Number:** #{pr.number}")
        st.write(f"**Title:** {pr.title}")
        st.write("**Changed Files:**")
        for i, url in enumerate(pr.changed_files_urls):
            st.write(f"{i + 1}. [{url.split('/')[-1]}]({url})")

    with col2:
        st.subheader("Related Issue")
        issue = pr.issue
        st.write(f"**Number:** #{issue.number}")
        st.write(f"**Title:** {issue.title}")
        st.write(f"**State:** {issue.state}")
        st.write(f"**Created:** {issue.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        st.write(f"**Updated:** {issue.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        st.write(f"**URL:** [{issue.url}]({issue.url})")

    st.markdown("---")

    st.subheader("Current State")
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Current Step:** {agent_state['current_step']}")
    with col2:
        st.info(
            f"**Current File Index:** {agent_state['current_file_idx']} of {len(pr.changed_files_urls)}"
        )

    # Progress bar
    progress_mapping = {
        "get_pr_details": 0.25,
        "find_file": 0.5,
        "analyze_file": 0.75,
        "conclude": 1.0,
    }
    progress = progress_mapping.get(agent_state["current_step"], 0)
    st.progress(progress)


def display_suggestions(agent_state):
    st.header("Improvement Suggestions")

    file_suggestions = agent_state["file_suggestions"]

    if not file_suggestions:
        st.info("No suggestions have been made yet.")
        return

    for file_suggestion in file_suggestions:
        st.subheader(f"File: {file_suggestion['file']}")

        for i, suggestion in enumerate(file_suggestion["suggestions"]):
            with st.expander(f"Suggestion {i + 1}: {suggestion['ref']}"):
                st.markdown(suggestion["suggestion"])

        st.markdown("---")


def display_refactored_files(agent_state):
    st.header("Refactored Files")

    refactored_contents = agent_state["refactored_file_contents"]

    if not refactored_contents:
        st.info("No files have been refactored yet.")
        return

    for i, content in enumerate(refactored_contents):
        file_name = agent_state["pr"].changed_files_urls[i].split("/")[-1]
        with st.expander(f"Refactored: {file_name}"):
            st.code(content, language="python")


if __name__ == "__main__":
    main()
