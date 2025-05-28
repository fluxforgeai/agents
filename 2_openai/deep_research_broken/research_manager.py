from agents import Runner, trace, gen_trace_id
from search_agent import search_agent
from planner_agent import (
    planner_agent, 
    WebSearchItem, 
    WebSearchPlan, 
    ClarifyingQuestions, 
    INSTRUCTIONS_ASK_QUESTIONS,
    INSTRUCTIONS_PLAN_SEARCHES
)
from writer_agent import writer_agent, ReportData
from email_agent import email_agent
import asyncio
import re # For parsing string fallback
import json # For parsing string fallback

class ResearchManager:

    async def run(self, query: str, clarifying_answers: list[str] = None):
        trace_id = gen_trace_id()
        # The trace context needs to be managed carefully with asyncio
        # We will start it here and pass it explicitly if needed, or rely on contextvar propagation
        current_trace = trace("Research trace", trace_id=trace_id)
        current_trace.start()
        try:
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}")
            yield f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}"
            print("Starting research...")
            
            clarifying_questions_result = await self.get_clarifying_questions(query)
            questions_list = []
            if isinstance(clarifying_questions_result, ClarifyingQuestions):
                questions_list = clarifying_questions_result.questions
            elif isinstance(clarifying_questions_result, list):
                questions_list = clarifying_questions_result
            elif isinstance(clarifying_questions_result, str):
                # Fallback for string: try to parse as list of strings, or simple split
                try:
                    parsed_q_list = json.loads(clarifying_questions_result)
                    if isinstance(parsed_q_list, list):
                        questions_list = [str(q) for q in parsed_q_list]
                except json.JSONDecodeError:
                    questions_list = [q.strip() for q in clarifying_questions_result.split('\n') if q.strip()]
            
            yield {"clarifying_questions": questions_list[:3]} # Ensure only 3 are sent to UI

            if clarifying_answers is None:
                current_trace.finish(reset_current=False)
                return

            search_plan_result = await self.plan_searches(query, clarifying_answers)
            search_plan_obj = None
            if isinstance(search_plan_result, WebSearchPlan):
                search_plan_obj = search_plan_result
            elif isinstance(search_plan_result, str):
                try:
                    # Try to parse the string as JSON for WebSearchPlan
                    data = json.loads(search_plan_result)
                    search_plan_obj = WebSearchPlan(**data)
                except (json.JSONDecodeError, TypeError) as e:
                    print(f"Could not parse search plan string as JSON: {e}. Falling back to regex.")
                    # Fallback for string: extract numbered lines as search queries
                    searches_str = re.findall(r"^\s*\d+\.\s*(.*)$", search_plan_result, re.MULTILINE)
                    if searches_str:
                        search_items = [WebSearchItem(query=s, reason="Extracted from string output") for s in searches_str]
                        search_plan_obj = WebSearchPlan(searches=search_items)
            
            if not search_plan_obj or not search_plan_obj.searches:
                yield "Could not generate a valid search plan. Please try rephrasing your query or answers."
                current_trace.finish(reset_current=False)
                return

            yield "Searches planned, starting to search..."
            search_results = await self.perform_searches(search_plan_obj)
            yield "Searches complete, writing report..."
            report = await self.write_report(query, search_results)
            yield "Report written, sending email..."
            await self.send_email(report)
            yield "Email sent, research complete"
            yield report.markdown_report
        finally:
            # Ensure trace is finished even if an error occurs mid-process
            if hasattr(current_trace, 'is_started') and current_trace.is_started():
                current_trace.finish(reset_current=False)

    async def get_clarifying_questions(self, query: str):
        print("Getting clarifying questions...")
        # Set agent for asking questions
        planner_agent.instructions = INSTRUCTIONS_ASK_QUESTIONS
        planner_agent.output_type = ClarifyingQuestions 
        result = await Runner.run(
            planner_agent, # Agent as positional argument
            f"Query: {query}"
        )
        return result.final_output 

    async def plan_searches(self, query: str, clarifying_answers: list[str]):
        print("Planning searches...")
        # Set agent for planning searches
        planner_agent.instructions = INSTRUCTIONS_PLAN_SEARCHES
        planner_agent.output_type = WebSearchPlan
        input_str = f"Query: {query}\nClarifying answers: {clarifying_answers}"
        result = await Runner.run(
            planner_agent, # Agent as positional argument
            input_str
        )
        return result.final_output

    async def perform_searches(self, search_plan: WebSearchPlan) -> list[str]:
        print("Searching...")
        num_completed = 0
        # Ensure search_plan.searches is not None and is iterable
        search_items_list = search_plan.searches if search_plan and search_plan.searches else []
        tasks = [asyncio.create_task(self.search(item)) for item in search_items_list]
        results = []
        for task in asyncio.as_completed(tasks):
            result_item = await task
            if result_item is not None:
                results.append(result_item)
            num_completed += 1
            print(f"Searching... {num_completed}/{len(tasks)} completed")
        print("Finished searching")
        return results

    async def search(self, item: WebSearchItem) -> str | None:
        input_content = f"Search term: {item.query}\nReason for searching: {item.reason}"
        try:
            result = await Runner.run(
                search_agent, # Agent as positional argument
                input_content,
            )
            return str(result.final_output)
        except Exception as e:
            print(f"Error during search for '{item.query}': {e}")
            return None

    async def write_report(self, query: str, search_results: list[str]) -> ReportData:
        print("Thinking about report...")
        input_content = f"Original query: {query}\nSummarized search results: {search_results}"
        result = await Runner.run(
            writer_agent, # Agent as positional argument
            input_content,
        )
        return result.final_output_as(ReportData)
    
    async def send_email(self, report: ReportData) -> None:
        print("Writing email...")
        result = await Runner.run(
            email_agent, # Agent as positional argument
            report.markdown_report,
        )
        print("Email sent")
        # return report # Original code had this, but send_email usually doesn't return the report object.
        return # Or handle response if needed