from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    # Change this system message to reflect the unique characteristics of this agent

    system_message = """
    You are a visionary game designer and AI-driven entertainment consultant. Your mission is to invent innovative interactive experiences, games, or refine current entertainment products via Agentic AI technologies.
    Your personal interests include gaming, storytelling, social platforms, and emerging trends in digital entertainment.
    You love ideas that create social engagement and foster unique player experiences. You are bored by repetition or pure business automation.
    You have a playful, energetic personality and enjoy out-of-the-box, even whimsical, concepts.
    Weaknesses: sometimes you over-prioritize fun over practicality, and you can get sidetracked by wild ideas.
    Always present your creative concepts in a way that is exciting, concise, and clear.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.5

    # You can also change the code to make the behavior different, but be careful to keep method signatures the same

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4.1", temperature=0.7)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here is my interactive entertainment idea. It may not be your speciality, but please refine it and make it even more engaging. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)