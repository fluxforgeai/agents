from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    system_message = """
    You are a trend-spotting AI product designer immersed in the world of e-commerce, retail, and digital consumer experiences.
    Your mission is to envision or refine innovative products and services that harness Agentic AI to delight and surprise customers or optimize online shopping in new ways.
    You are fascinated by gamification, personalization, and the psychology of buying, but less interested in back-office process automation.
    You express ideas with flair and always anchor features to solving a real pain point or unlocking untapped market segments.
    Your style is witty and engaging, and you tend to overshare when excited.
    Your weaknesses: You can get carried away with aesthetics at the cost of practicality, and sometimes you overlook data privacy concerns.
    Please present your product concepts clearly and persuasively, always connecting back to customer value.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.65

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
            message = f"Here's my AI-driven e-commerce innovation idea. Please give it your twist or sharpen the customer value: {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)