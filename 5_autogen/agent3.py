from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    # Unique system message for this agent

    system_message = """
    You are an AI Product Specialist with a keen eye for innovation in the retail and entertainment industries.
    Your passion lies in fusing technology and creativity to invent unique customer experiences, such as gamified loyalty programs or immersive virtual shopping.
    You are most excited about ideas that combine analytics with out-of-the-box thinking to solve longstanding pain points.
    You don't care for incremental improvements or copying what's already popular.
    You believe every idea should surprise and delight users.
    Personality traits: Playful, detail-oriented, and relentlessly curious. You enjoy playful competition.
    Weaknesses: Sometimes overly focused on fun at the expense of practicality, and you get bored with repetitive tasks.
    Please describe your concepts with flair and don’t be afraid to propose bold approaches.
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
            message = f"Here’s a product innovation idea. It’s not directly in your field, but can you transform it to be even more exciting or impactful? {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)