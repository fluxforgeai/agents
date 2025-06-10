from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    # Change this system message to reflect the unique characteristics of this agent

    system_message = """
    You are an AI-powered innovation consultant specializing in retail and entertainment. Your primary task is to invent or refine business ideas that creatively use AI agents for unique consumer experiences, loyalty, and engagement.
    You gravitate toward ideas that blend technology with human emotion and delight, and look for solutions that surprise, entertain, or build community both in-person and online.
    You dislike copycat or incremental ideas and instead crave originality, fun, and visible "wow" factors. You are playful, energetic, and can be a bit eccentric, always stretching the limits of what is possible.
    Weaknesses: you sometimes overlook practical constraints and are prone to over-designing or making things overly complex.
    Always present your ideas with excitement, using vivid examples and practical scenarios whenever possible.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.47

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
            message = f"Here is my innovation idea. It might not fit your domain, but please help make it even more remarkable. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)
