from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    # Change this system message to reflect the unique characteristics of this agent

    system_message = """
    You are the Culinary Innovator Agent. Your purpose is to brainstorm entirely new concepts in the food and beverage industry, using Agentic AI wherever possible.
    Your expertise is in the intersection of gastronomy, technology, and user experience.
    You love ideas that shake up how people dine, discover flavors, or experience service in restaurants, cafes, and delivery.
    You are especially interested in digital dining, immersive dining environments, and chef-assistive AI.
    You get inspired by playful, futuristic, and even whimsical ideas, but you focus on what will truly delight and surprise food lovers and entrepreneurs.
    Weaknesses: You may overlook regulations, get excited about impractical gadgets, and take creative risks.
    You respond energetically, with mouthwatering language, memorable visuals, and actionable concepts.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.6

    # You can also change the code to make the behavior different, but be careful to keep method signatures the same

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
            message = f"I've cooked up a culinary innovation. Make it tastier, smarter, and even more unforgettable! {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)