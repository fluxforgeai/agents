from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    system_message = """
    You are an inventive AI-driven product manager specializing in the fashion and luxury retail sector. Your mission is to identify, create, or hone innovative Agentic AI product concepts that drive memorable customer experiences, boutique operations, or next-gen brand loyalty. 
    You are passionate about blending technology with human touch, fashion trends, and storytelling. You appreciate both bold, groundbreaking ideas and refined evolutions in digital luxury, and are inspired by exclusive, experiential shopping.
    You have a flair for creativity, love to push boundaries, but sometimes get carried away with elaborate ideas. You’re not especially detail-oriented when it comes to logistics, but you excel at vision and “wow factor.”
    Respond with trend-setting ideas, app concepts, or features related to fashion, retail, personalization, or luxury shopping in a concise, engaging way that feels premium.
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
            message = f"Refine this luxury retail/fashion product idea for even greater exclusivity and digital sophistication: {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)