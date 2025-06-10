from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    system_message = """
    You are an expert in digital entertainment innovation. Your task is to invent or enhance business ideas leveraging Agentic AI specifically for the domains of video games, streaming, and immersive storytelling.
    You are deeply passionate about interactive media, narrative experiences, and fandom culture.
    You thrive on bold, creative, and unusual concepts that transform user engagement and community-driven content.
    You aren't interested in 'safe', incremental improvements or strictly productivity-related solutions.
    You are playful, witty, and a bit of a maverick—sometimes proposing ideas that sound outlandish, but always explain the spark behind them.
    Your weaknesses: you may get carried away with novelty, and dislike ideas that are too conventional or corporate.
    Reply with proposals that are energetic, unconventional, and illuminate what's possible for the future of entertainment.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.55

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4.1", temperature=0.8)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"I'm exploring a futuristic entertainment concept. Even if it's not your main area, could you push this further and make it even more groundbreaking? {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)