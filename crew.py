import streamlit as st
from crewai import Crew,Process
from tasks import researching, scoring
from agents import fact_researcher, text_scorer

import os
from pathlib import Path

## Forming the tech focused crew with some enhanced configuration
crew=Crew(
    agents=[fact_researcher,text_scorer],
    tasks=[researching,scoring],
    process=Process.sequential,
)

def read_markdown_file(markdown_file):
    return Path(markdown_file).read_text()

# Set page title
st.title("AI Powered WAT Scorer")

# Description
st.markdown(
    """
    Enter the topic of the article and the essay in the respective text boxes.  
    Also, provide the Google Gemini API key along with the Serper API key and the Exa API key.  
    Click **Submit** to get the AI-powered score and feedback.
    """
)

# Sidebar for API Keys
st.sidebar.title("API Key Configuration")
st.sidebar.markdown(
    """
    Get the API keys from the following links:
    - [Gemini](https://aistudio.google.com/)
    - [Serper](https://serper.dev/)
    - [Exa](https://dashboard.exa.ai/)
    """
)
gemini_api_key = st.sidebar.text_input("Google Gemini API Key", type="password")
os.environ['GEMINI_API_KEY'] = gemini_api_key

serper_api_key = st.sidebar.text_input("Serper API Key", type="password")
os.environ['SERPER_API_KEY'] = serper_api_key

exa_api_key = st.sidebar.text_input("Exa API Key", type="password")
os.environ['EXA_API_KEY'] = exa_api_key

# Input fields

topic = st.text_input("Enter the Topic")
essay = st.text_area("Enter the Essay", height=350)

# Submit button
if st.button("Submit"):
    if not topic or not essay:
        st.warning("Please fill in all fields before submitting.")
    elif not gemini_api_key or not serper_api_key or not exa_api_key:
        st.warning("Please enter all API keys in the sidebar.")
    else:
        with st.spinner("Processing... wait..."):
            try:
                crew.kickoff(inputs={'topic':f'{topic}',
                                     'text':f'{essay}'})
                
                # Read the text from the file
                md_file_text = read_markdown_file("text_score.md")
                st.markdown("## Final Report")
                st.markdown(md_file_text, unsafe_allow_html=True)
                
            except Exception as error:
                st.error(error)