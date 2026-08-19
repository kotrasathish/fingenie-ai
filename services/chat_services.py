from services.database_service import database_service
from services.ai.ai_service import ai_service


class ChatService:

    def get_reply(
        self,
        message,
        conversation_id=None
    ):

        # --------------------------
        # Create conversation
        # --------------------------

        if conversation_id is None:

            conversation_id = (
                database_service.create_conversation(
                    title=message[:30]
                )
            )


        # --------------------------
        # Save user message
        # --------------------------

        database_service.save_message(

            role="user",

            message=message,

            conversation_id=conversation_id

        )


        # --------------------------
        # Get conversation history
        # --------------------------

        messages = (
            database_service.get_messages(
                conversation_id
            )
        )


        # --------------------------
        # AI
        # --------------------------

        reply = ai_service.ask(
            messages
        )


        # --------------------------
        # Save AI response
        # --------------------------

        database_service.save_message(

            role="assistant",

            message=reply,

            conversation_id=conversation_id

        )


        return reply, conversation_id


chat_service = ChatService()