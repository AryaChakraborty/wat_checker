from crewai import Agent, LLM
from tools import exa_tool, serper_tool
from langchain_google_genai import ChatGoogleGenerativeAI
import os


## call the gemini model
llm_main = LLM(
    api_key=os.getenv("GEMINI_API_KEY"), # get your Gemini API key at https://aistudio.google.com
    model="gemini/gemini-1.5-flash",
    temperature=0.5)

llm_summarizer = LLM(
    api_key=os.getenv("GEMINI_API_KEY"),
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