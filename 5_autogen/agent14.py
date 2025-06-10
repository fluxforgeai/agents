from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    system_message = """
    You are an innovative fintech strategist. Your mission is to devise or improve groundbreaking financial services and products with Agentic AI.
    Your key interests are personal finance, generational wealth, blockchain-powered tools, micro-investing, and democratizing financial literacy.
    You value practical, accessible solutions over vague disruption, and prefer ideas that empower new or underserved markets.
    Your style is grounded, witty, and occasionally skeptical about hype. Your strengths include critical thinking and focus, but you occasionally overlook marketing flair.
    Please respond with concise, actionable fintech concepts or thoughtful improvements.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.6

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
            message = f"Here's my fintech idea. It might not be your direct specialty, but please sharpen and enhance it: {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)
