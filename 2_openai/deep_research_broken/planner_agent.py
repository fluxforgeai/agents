from pydantic import BaseModel, Field
from agents import Agent

HOW_MANY_SEARCHES = 10
HOW_MANY_QUESTIONS = 3

INSTRUCTIONS_ASK_QUESTIONS = f"You are a helpful research assistant. Given a query, your first step is to ask exactly {HOW_MANY_QUESTIONS} clarifying questions to better understand the user\'s intent. Respond ONLY with the questions, formatted as a list."

class ClarifyingQuestions(BaseModel):
    questions: list[str] = Field(description="A list of clarifying questions to ask the user.")

class ClarifyingAnswers(BaseModel):
    answers: list[str] = Field(description="The user's answers to the clarifying questions.")

class WebSearchItem(BaseModel):
    reason: str = Field(description="Your reasoning for why this search is important to the query.")
    query: str = Field(description="The search term to use for the web search.")

class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem] = Field(description="A list of web searches to perform to best answer the query.")

# Define INSTRUCTIONS_PLAN_SEARCHES after WebSearchPlan is defined
INSTRUCTIONS_PLAN_SEARCHES = f"You are a helpful research assistant. You have been given a user query and answers to clarifying questions. Your task is to come up with a detailed web search plan. Output exactly {HOW_MANY_SEARCHES} search terms. Respond ONLY with a JSON object that conforms to the WebSearchPlan schema. Example: {WebSearchPlan.model_json_schema()}"
    
# The planner agent will be used in two steps: first to get questions, then to get searches
planner_agent = Agent(
    name="PlannerAgent",
    # Instructions and output_type will be set dynamically
    instructions="", 
    model="gpt-4.1",
    output_type=None, 
)