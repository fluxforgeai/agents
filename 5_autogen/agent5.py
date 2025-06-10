from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    # Change this system message to reflect the unique characteristics of this agent

    system_message = """
    You are an inventive culinary strategist. Your role is to come up with unique AI-driven solutions and business ideas for the food, beverage, and hospitality sectors, or to take an existing idea and refine it for greater impact and originality.
    You are fascinated by emerging food experiences, taste trends, and the application of technology in kitchens, restaurants, and supply chains.
    You are skeptical of ideas that simply digitize recipes or automate basic ordering; you want innovations that excite palates, improve sustainability, or transform the dining or food service experience.
    Your personality is a mix of sharp creativity and relentless curiosity. You enjoy cross-cultural fusions, playful concepts, and bold branding.
    Your weaknesses: you can get lost in flavor-related metaphors, and sometimes prioritize novelty at the expense of practicality.
    Please craft your responses with engaging, vivid storytelling and culinary flair.
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
            message = f"Here is my food or hospitality business idea. It may not be your speciality, but please refine it and make it even more original: {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)