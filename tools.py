## https://serper.dev/
## https://dashboard.exa.ai/

import os

os.environ['SERPER_API_KEY'] = os.getenv('SERPER_API_KEY')
os.environ['EXA_API_KEY'] = os.getenv('EXA_API_KEY')


from crewai_tools import SerperDevTool, EXASearchTool

# Initialize the tool for internet searching capabilities
serper_tool = SerperDevTool()
exa_tool = EXASearchTool()