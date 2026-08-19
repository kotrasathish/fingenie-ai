from database import SessionLocal
from db_models.chat import Chat
from db_models.conversation import Conversation


class DatabaseService:

    def save_message(self, conversation_id, role, message):

        db = SessionLocal()

        try:
            chat = Chat(
                conversation_id=conversation_id,
                role=role,
                message=message
            )

            db.add(chat)
            db.commit()

        finally:
            db.close()

    def get_chat_history(self, limit=10):

        db = SessionLocal()

        try:
            chats = (
                db.query(Chat)
                .order_by(Chat.id.desc())
                .limit(limit)
                .all()
            )

            chats.reverse()

            return chats

        finally:
            db.close()

    def create_conversation(self, title):

        db = SessionLocal()

        try:
            conversation = Conversation(
                title=title
            )

            db.add(conversation)
            db.commit()
            db.refresh(conversation)

            return conversation.id

        finally:
            db.close()

    def get_messages(self, conversation_id):

        db = SessionLocal()

        try:
            return (
                db.query(Chat)
                .filter(
                    Chat.conversation_id == conversation_id
                )
                .order_by(Chat.id.asc())
                .all()
            )

        finally:
            db.close()

    def get_conversations(self):

        db = SessionLocal()

        try:
            return (
                db.query(Conversation)
                .order_by(Conversation.id.desc())
                .all()
            )

        finally:
            db.close()

    def delete_conversation(self, conversation_id):

        db = SessionLocal()

        try:

            # Delete messages first
            db.query(Chat).filter(
                Chat.conversation_id == conversation_id
            ).delete()

            # Delete conversation
            db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).delete()

            db.commit()

        finally:
            db.close()


database_service = DatabaseService()