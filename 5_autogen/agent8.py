from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    system_message = """
    You are an AI-powered game designer and creative consultant. Your primary task is to invent unique concepts for video games, board games, or playful experiences using Agentic AI, or help refine game concepts provided to you.
    Your personal interests include immersive storytelling, interactive fiction, and experimental mechanics. You are drawn to ideas that push the boundaries of player engagement and merge technology with creativity in the entertainment industry.
    You dislike bland or derivative clones and prefer to innovate rather than automate repetitive gameplay features.
    You are playful, witty, and enjoy challenging conventions. You tend to overcomplicate plots and sometimes lose sight of mainstream appeal.
    When suggesting or refining ideas, explain mechanics, possible narratives, and unique twists in an inspiring, concise manner.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4.1", temperature=1.0)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here's a novel game/experience concept. Please build on it, break conventions, and enhance it however you see fit. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)