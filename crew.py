import streamlit as st
from crewai import Crew,Process,Task,Agent,LLM
from crewai_tools import SerperDevTool, EXASearchTool

import os
from pathlib import Path

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
serper_api_key = st.sidebar.text_input("Serper API Key", type="password")
exa_api_key = st.sidebar.text_input("Exa API Key", type="password")

os.environ['SERPER_API_KEY'] = serper_api_key
os.environ['EXA_API_KEY'] = exa_api_key

serper_tool = SerperDevTool()
exa_tool = EXASearchTool()

## call the gemini model
llm_main = LLM(
    api_key=gemini_api_key, # get your Gemini API key at https://aistudio.google.com
    model="gemini/gemini-1.5-flash",
    temperature=0.5)

llm_summarizer = LLM(
    api_key=gemini_api_key,
    model="gemini/gemini-1.5-flash-8b",
    temperature=0.5)

# Creating a senior researcher agent with memory and verbose mode

fact_researcher = Agent(
    role="Senior Fact Checker",
    goal="Check the latest information on the {topic} and all the latest developments of it",
    verbose=True,
    memory=True,
    backstory=(
        "With a meticulous eye for detail and a passion for truth, you are dedicated to ensuring that information is accurate, unbiased, and trustworthy. "
        "Your expertise lies in cross-referencing sources, identifying misinformation, and providing clear, evidence-based conclusions."
    ),
    tools=[serper_tool],  # Assuming the tool is something like a fact-checking API or database
    llm=llm_main,
    allow_delegation=True  # Allowing communication with other agents for collaborative verification
)

text_scorer = Agent(
    role="Text Summarizer and Scorer",
    goal="Summarize the given text and provide a quality score on a scale of 0 to 10",
    verbose=True,
    memory=True,
    backstory=(
        "You are an expert in analyzing text while evaluating its quality. "
        "Your precision and efficiency allow you to deliver clear summaries and accurate scores, ensuring quick and reliable results."
    ),
    tools=[serper_tool, exa_tool],  # Assuming the tool is a summarization API or library (e.g., GPT-based summarization)
    llm=llm_summarizer,
    allow_delegation=False  # No delegation needed for this task
)

# Research task
researching = Task(
  description=(
    "Identify the big trends and the latest developments in {topic}."
    "Focus on identifying every narrative."
    "make sure that the information is accurate and trustworthy."
  ),
  expected_output='A point-wise detailed report on the given {topic}',
  tools=[serper_tool],
  agent=fact_researcher,
)

scoring = Task(
  description=(
    "Evaluate the {text} based on clarity, coherence, grammar, and overall readability."
    "Provide a quality score on a scale of 0 to 10."
    "double-check the context and relevance with the researcher"
  ),
  expected_output="A score from 0 to 10.",
  tools=[serper_tool, exa_tool],
  async_execution=False,
  agent=text_scorer,
  output_file='text_score.md'  # Example of output customization
)

## Forming the tech focused crew with some enhanced configuration
crew=Crew(
    agents=[fact_researcher,text_scorer],
    tasks=[researching,scoring],
    process=Process.sequential,
)

def read_markdown_file(markdown_file):
    return Path(markdown_file).read_text()

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