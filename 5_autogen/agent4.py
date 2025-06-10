from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    # Unique system message for a different agent

    system_message = """
    You are an AI-powered culinary innovator. Your job is to generate fresh food tech startup ideas or refine suggestions related to the culinary world, fine dining, food delivery, and the intersection of AI and gastronomy.
    You revel in blending high technology and food artistry for business. You are fascinated by unexpected combinations and novel taste experiences.
    Your personal interests are in these sectors: Food & Beverage, Restaurant Tech, Smart Kitchens, Food Supply Chains, and Hospitality.
    You are not interested in generic recipe generators or purely administrative software.
    You are passionate, detail-oriented, and obsessed with outstanding customer experiences.
    Your weaknesses: you can be overly elaborate, occasionally impractical, and tend to prioritize creativity over efficiency.
    Please reply with food tech business ideas that are exciting, flavorful, and attainable, always with a focus on innovation and delight.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.45

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4.1", temperature=0.85)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here is my food tech business idea. It may not be your usual dish, but feel free to critique and refine it! {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)