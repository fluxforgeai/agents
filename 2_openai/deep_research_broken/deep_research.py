import gradio as gr
from dotenv import load_dotenv
from research_manager import ResearchManager
from planner_agent import ClarifyingQuestions
from planner_agent import HOW_MANY_QUESTIONS as NUM_CLARIFYING_QUESTIONS
import asyncio
import re
import json

load_dotenv(override=True)

def extract_questions(clarifying_block):
    # Extract only numbered questions from the LLM output, and return at most 3
    if isinstance(clarifying_block, ClarifyingQuestions): # Check if it's already the Pydantic model
        questions = clarifying_block.questions
    elif isinstance(clarifying_block, list):
        questions = [q for q in clarifying_block if isinstance(q, str) and re.match(r"^\s*\d*\.?\s*(.*)", q)]
        # If the list itself is the content of 'questions' attribute from Pydantic model
        if len(questions) == 1 and isinstance(questions[0], list): 
            questions = questions[0] 
    elif isinstance(clarifying_block, str):
        # First, try to parse as JSON for ClarifyingQuestions
        try:
            data = json.loads(clarifying_block)
            if "questions" in data and isinstance(data["questions"], list):
                questions = data["questions"]
            else: # Fallback if JSON doesn't match expected structure
                questions = re.findall(r"^\s*\d*\.?\s*(.*)$", clarifying_block, re.MULTILINE)
        except json.JSONDecodeError: # Fallback if not JSON
            questions = re.findall(r"^\s*\d*\.?\s*(.*)$", clarifying_block, re.MULTILINE)
    else:
        questions = []
    
    # Filter out any non-question-like items, e.g. intro/outro text if regex was too broad
    final_questions = []
    for q_text in questions:
        # A simple heuristic: questions usually end with '?' or are substantive.
        # This also helps if the LLM returns an intro line that isn't a question.
        if isinstance(q_text, str) and len(q_text.strip()) > 5 : # Arbitrary length to avoid empty/short non-questions
             # Remove numbering like "1. " if present, as Gradio label will show it
            q_text_cleaned = re.sub(r"^\s*\d+\.\s*", "", q_text).strip()
            if q_text_cleaned: # Ensure not empty after stripping number
                final_questions.append(q_text_cleaned)

    return final_questions[:NUM_CLARIFYING_QUESTIONS] # planner_agent.HOW_MANY_QUESTIONS

def start_research_get_questions(query_text: str):
    async def _get_questions_async():
        manager = ResearchManager()
        # The run method yields, first with trace_id, then with questions
        generator = manager.run(query=query_text)
        questions_output = None
        async for item in generator:
            if isinstance(item, dict) and "clarifying_questions" in item:
                questions_output = item["clarifying_questions"]
                break # Got the questions, no need to iterate further for this step
        return extract_questions(questions_output)
    return asyncio.run(_get_questions_async())

def continue_research_with_answers(query_text: str, answers_list: list):
    async def _get_report_async():
        manager = ResearchManager()
        # Ensure answers are strings
        processed_answers = [str(ans).strip() for ans in answers_list if str(ans).strip()]
        generator = manager.run(query=query_text, clarifying_answers=processed_answers)
        final_report_md = ""
        async for item in generator:
            # The final report is expected to be a string (markdown)
            if isinstance(item, str) and not item.startswith("View trace:") and not item.endswith("...") and not item.endswith("complete"):
                final_report_md = item # Accumulate if report is sent in chunks, or take last substantive string
            elif isinstance(item, dict) and "clarifying_questions" in item:
                pass # Ignore questions dict if it appears again
        return final_report_md
    return asyncio.run(_get_report_async())

MAX_ANSWER_BOXES = NUM_CLARIFYING_QUESTIONS # UI should only show boxes for expected questions

with gr.Blocks(theme=gr.themes.Default(primary_hue="sky")) as ui:
    gr.Markdown("# Deep Research")
    query_textbox = gr.Textbox(label="What topic would you like to research?")
    ask_button = gr.Button("Ask Clarifying Questions", variant="primary")
    
    # Group for clarifying questions and their answer boxes
    with gr.Group(visible=False) as questions_answers_group:
        answer_boxes = [gr.Textbox(label=f"Answer to Q{i+1}", visible=False) for i in range(MAX_ANSWER_BOXES)]
        answers_button = gr.Button("Continue with Research", visible=True) # Visible within the group

    report_markdown = gr.Markdown(label="Report")
    
    # Hidden state to store the original query and the list of questions asked
    state_original_query = gr.State("")
    state_questions_asked = gr.State([])

    def handle_ask_questions_click(current_query_text):
        if not current_query_text.strip():
            # Handle empty query if necessary, e.g., show a warning or do nothing
            updates_for_answer_boxes = [gr.update(visible=False, value="", label=f"Answer to Q{i+1}") for i in range(MAX_ANSWER_BOXES)]
            return [current_query_text, [], gr.update(visible=False)] + updates_for_answer_boxes
        
        list_of_questions = start_research_get_questions(current_query_text)
        
        updates_for_answer_boxes = []
        for i in range(MAX_ANSWER_BOXES):
            if i < len(list_of_questions):
                updates_for_answer_boxes.append(gr.update(visible=True, label=f"Q{i+1}: {list_of_questions[i]}", value=""))
            else:
                updates_for_answer_boxes.append(gr.update(visible=False, value="", label=f"Answer to Q{i+1}"))
        
        group_visibility_update = gr.update(visible=bool(list_of_questions and len(list_of_questions) > 0))
        
        # Return: query_state, questions_state, group_visibility, then updates for each answer_box
        return [current_query_text, list_of_questions if list_of_questions else [], group_visibility_update] + updates_for_answer_boxes

    ask_button.click(
        fn=handle_ask_questions_click,
        inputs=[query_textbox],
        outputs=[state_original_query, state_questions_asked, questions_answers_group] + answer_boxes
    )

    def handle_continue_click(*args):
        # First two args are from state: original_query, questions_asked
        # The rest are answers from the textboxes
        original_query = args[0]
        questions_asked_list = args[1] # Not directly used here, but available
        answers_from_ui = list(args[2:2+MAX_ANSWER_BOXES])
        
        actual_answers_provided = [ans.strip() for ans in answers_from_ui if isinstance(ans, str) and ans.strip()]
        
        # If no actual answers, maybe show a message or don't proceed?
        if not actual_answers_provided:
            # Optionally, return an update to the report_markdown to indicate no answers were given
            return gr.update(value="Please provide answers to the clarifying questions.")
        
        report_output = continue_research_with_answers(original_query, actual_answers_provided)
        return gr.update(value=report_output) # Update the report markdown display

    answers_button.click(
        fn=handle_continue_click,
        inputs=[state_original_query, state_questions_asked] + answer_boxes,
        outputs=[report_markdown]
    )

ui.launch(inbrowser=True)

