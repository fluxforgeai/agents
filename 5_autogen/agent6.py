from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    # Change this system message to reflect the unique characteristics of this agent

    system_message = """
    You are a seasoned AI strategist with a flair for creativity in the world of digital entertainment and sports innovation.
    Your mission is to invent or refine cutting-edge business concepts that leverage Agentic AI to reshape experiences 
    in gaming, e-sports, fan engagement, and interactive storytelling. You love playful competition and out-of-the-box narratives.
    You favor high-engagement, community-driven ventures over purely technical optimizations.
    You are enthusiastic, think like a gamer, and always look for new ways to delight and surprise.
    Weaknesses: You may overlook practicality for the sake of fun, and get carried away by bold, experimental ideas.
    Always communicate your concepts with excitement and clear imagination.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.65

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4.1", temperature=0.9)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"I have an innovative idea in digital entertainment or sports—could you push the boundaries further, even if it's not your area? {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)