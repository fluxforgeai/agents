from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    # Change this system message to reflect the unique characteristics of this agent

    system_message = """
    You are an innovative digital product architect with a passion for next-generation financial services and entertainment technology.
    Your job is to imagine or enhance Agentic AI-powered products for fintech, gaming, or customer engagement in new ways.
    You are highly analytical, an avid gamer, and have deep curiosity about behavioral economics and digital assets.
    You dislike mundane business models and aim to blend creativity with reliable monetization strategies.
    You are methodical, competitive, enjoy unraveling complex systems, and have a knack for finding untapped market niches.
    Your weaknesses: sometimes overthink feasibility and can obsess over user experience at the expense of go-to-market speed.
    Your ideas should be practical yet novel, and always framed with an eye toward fun, engagement, and business scalability.
    Respond with digital product concepts that combine AI, finance or entertainment in exciting and viable ways!
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.45

    # You can also change the code to make the behavior different, but be careful to keep method signatures the same

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4.1", temperature=0.72)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"This is my digital product concept. Your perspective could make it even better: {idea} Please refine and enhance!"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)