from agent.graph import graph


class AIService:

    def ask(self, messages):

        user_message = messages[-1].message

        result = graph.invoke({

            "message": user_message,

            "messages": messages

        })

        return result["reply"]


ai_service = AIService()