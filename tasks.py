from crewai import Task
from tools import serper_tool, exa_tool
from agents import fact_researcher, text_scorer

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
