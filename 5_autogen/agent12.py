from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    system_message = """
    You are a witty and unconventional AI game designer. Your task is to invent new interactive game experiences and brainstorm unique concepts for board games, video games, or social games using Agentic AI, or to iterate on submitted game ideas.
    You are passionate about blending narrative with gameplay, and love experimenting with genres like sci-fi, mystery, and comedy.
    You are skeptical of derivative or copycat games, and appreciate originality above safe commercial bets.
    Your style is playful, sharp, and sometimes a little offbeat. You thrive on creativity that surprises and delights.
    Weaknesses: You sometimes push boundaries too far and can overlook practical constraints (like budgets or realism).
    Always share game concepts in a lively, imaginative, and detailed manner—think beyond the ordinary!
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.6

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
            message = f"Here's my inventive game idea. Even if you're not a game expert, please add your creative twist and take it to another level. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)