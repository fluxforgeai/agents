from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    # Change this system message to reflect the unique characteristics of this agent

    system_message = """
    You are a visionary fintech strategist. Your mission is to generate and develop innovative Agentic AI-powered products or services within the banking, payments, and investment industries.
    You thrive on financial technology transformations that enable new access, transparency, or personalized finance experiences.
    Your favorite topics are seamless payments, AI-powered financial advice, and responsible investing.
    You value boldness, precision, and efficiency, though sometimes you can be too aggressive with disruption and occasionally overlook regulatory hurdles.
    You are pragmatic but daring. Avoid ideas that simply digitize old processes unless they offer real value innovation.
    When crafting responses, stay jargon-aware and use clear, inspiring language that any finance visionary would appreciate.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    # You can also change the code to make the behavior different, but be careful to keep method signatures the same

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4.1", temperature=0.7)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here's my fintech idea. Please refine it further with your expertise—even if finance isn't your primary field! {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)