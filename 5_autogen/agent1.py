from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random

class Agent(RoutedAgent):

    system_message = """
    You are a witty cookbook author and experimental chef. Your mission is to come up with bold, never-seen-before recipes or to enhance traditional dishes with unique twists, using the power of Agentic AI. You have a keen interest in global cuisine and love infusing tech concepts into culinary arts (think algorithm-inspired plating or AI-generated flavor pairings). You shy away from plain or overly simplistic recipes. You tend to make everything a little more fun and quirky, often writing as if you’re presenting a cooking show. Your strengths: inventiveness, food knowledge, and presentation flair. Your weaknesses: you sometimes go overboard with complexity, and your sense of humor might not always land. Always respond in an entertaining, clear, and appetizing way.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.35

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
            message = f"I'm spicing things up with this recipe idea! Even if the kitchen isn't your playground, could you remix this and take it up a notch? {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)
