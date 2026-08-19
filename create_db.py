from database import Base, engine
from db_models.chat import Chat
from db_models.conversation import Conversation

Base.metadata.create_all(bind=engine)

print("Database created successfully!")