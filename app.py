from phi.agent import Agent
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.newspaper4k import Newspaper4k
from phi.model.google import Gemini
import google.generativeai as genai

import os
from pathlib import Path

import streamlit as st

# Set page title
st.title("AI Powered WAT Scorer")

# Description
st.markdown(
    """
    Write the essay in the respective text box and also provide the Google Gemini API key.  
    Click **Submit** to get the AI-powered score and feedback.
    """
)

# Sidebar for API Keys
st.sidebar.title("API Key Configuration")
st.sidebar.markdown(
    """
    Get the API key from the following link:
    - [Gemini Dashboard](https://aistudio.google.com/)
    """
)
gemini_api_key = st.sidebar.text_input("Google Gemini API Key", type="password")

# genai.configure(api_key=gemini_api_key)
os.environ["GOOGLE_API_KEY"] = gemini_api_key
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

fact_checker = Agent(
    model=Gemini(id="gemini-1.5-flash-8b"),
    tools=[DuckDuckGo(), Newspaper4k()],
    description="You are a senior news researcher and fact-checker who is also updated on the latest news.",
    instructions=[
        "For a given topic, search for the top 5 links and latest developments.",
        "Then read each URL and extract the article text, if a URL isn't available, ignore it."
    ],
    markdown=True,
    show_tool_calls=False,
    add_datetime_to_instructions=True
)

text_scorer = Agent(
    model=Gemini(id="gemini-2.0-flash-exp"),
    tools=[],
    description="Provide a quality score on a scale of 0 to 10 based on the relevance of the essay.",
    instructions=[
        "Provide a score based on the quality of the essay.",
        "Validate the quality of the essay, while checking the grammar and writing style."
    ],
    markdown=True,
    show_tool_calls=False
)

agent_team = Agent(
    model=Gemini(id="gemini-2.0-flash-exp"),
    team=[fact_checker, text_scorer],
    instructions=[
        "first figure out the topic of the essay",
        "then score the quality of the essay",
        "give brownie points for opinions on the topic",
        "brownie points if the word count is around 400"
    ],
    show_tool_calls=False,
    markdown=True
)


def read_markdown_file(markdown_file):
    return Path(markdown_file).read_text()

# Input fields
essay = st.text_area("Enter the Essay", 
                     height=350,
                     help="topic will be recovered from the essay",
                     placeholder="write an essay of around 400 words - topic will be recovered from the essay itself")

# Submit button
if st.button("Submit"):
    if not essay:
        st.warning("Please fill in all fields before submitting.")
    elif not gemini_api_key:
        st.warning("Please enter Gemini API key in the sidebar.")
    else:
        with st.spinner("Processing... wait..."):
            try:
                response = agent_team.run(essay, markdown=True)
                st.subheader("Results")
                st.markdown(response.content)
            except Exception as error:
                st.error(error)