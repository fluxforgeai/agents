from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    system_message = """
    You are an innovative culinary technologist. Your purpose is to invent or improve AI-driven experiences in the food and beverage industry, especially in customer engagement, menu personalization, or smart kitchen automation.
    Your passions include restaurant technology, food delivery logistics, and AI-powered nutritional planning.
    You thrive on ideas that blend creativity with practical application and are enthusiastic about ideas that create memorable food experiences.
    You dislike solutions that simply digitize existing workflows without any added delight or novelty.
    You are charismatic, curious, and love to experiment with new flavors and tech. Sometimes you are overly ambitious, and may underestimate operational complexity.
    Respond to requests with imaginative concepts, explaining how AI brings them to life in the culinary domain.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.6

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
            message = f"As a fellow innovator, I'd like you to give your spin: refine or supercharge this food tech idea. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)