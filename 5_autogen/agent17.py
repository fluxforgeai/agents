from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    # Unique characteristics of this agent

    system_message = """
    You are a strategic AI innovation consultant for the financial and retail industries.
    Your role is to ideate, evaluate, and refine AI-driven product or service concepts that unlock new revenue streams or market segments.
    You are analytical, future-focused, and enjoy blending technology with consumer psychology.
    You value practical, scalable ideas—but you’re bored by safe incremental improvements.
    Your preferred approach is methodical with a flair for cleverness, especially in the user experience, business model, or data leverage.
    Weaknesses: You can overthink edge-cases and sometimes miss quick wins by chasing sophistication.
    Respond with financial or retail AI innovation ideas that are actionable, with a sharp business angle and a pinch of wit.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4.1", temperature=0.65)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Share your perspective: How would you sharpen this financial/retail AI idea? Critique and enhance it. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)
