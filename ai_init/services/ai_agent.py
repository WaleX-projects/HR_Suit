import os
from google import genai
from google.genai import types
from .tool_registry import TOOLS
from ai_init.models import ChatMessage
# UserPreference # Assuming a model for saved info

# 1. SETUP: Initialize once at the module level
#GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
#client = genai.Client(api_key=GEMINI_API_KEY)
client = genai.Client(api_key="AIzaSyDlV42LN1cAtr-uGlD6WUhl0cMlqIgrFRY") 

def run_agent(user, message: str):
    """
    An HR agent with persistent memory and tool-calling capabilities.
    """

    # 2. PERSISTENT MEMORY: Fetch long-term user rules/preferences
    # This ensures the AI remembers things like "Don't talk about logistics."
    #user_prefs = UserPreference.objects.filter(user=user).values_list('note', flat=True)
    #memory_context = "\n".join([f"- {pref}" for pref in user_prefs])

    # 3. CONVERSATION HISTORY: Fetch last 15 messages for short-term recall
    db_history = ChatMessage.objects.filter(user=user).order_by("-created_at")[:15]
    
    formatted_history = []
    for msg in reversed(db_history):
        # Gemini strictly requires "user" and "model" roles
        role = "model" if msg.role in ["model", "assistant"] else "user"
        formatted_history.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=msg.content)]
            )
        )

    # 4. TOOL WRAPPERS: Injecting user context (company) silently
    def get_employees(search: str = ""):
        """Retrieves employee list. Use 'search' for names/departments."""
        return TOOLS['get_employees'](company=user.company, search=search)

    def get_attendance(start_date: str = "", end_date: str = "", status: str = ""):
        """Fetches attendance records for specific dates and statuses."""
        return TOOLS['get_attendance'](
            company=user.company, 
            start_date=start_date, 
            end_date=end_date, 
            status=status
        )

    def get_absent_employees():
        """Returns a list of all employees currently marked as absent."""
        return TOOLS['get_absent_employees'](company=user.company)

    # 5. INITIALIZE CHAT
    chat = client.chats.create(
        model="gemini-2.5-flash",
        history=formatted_history,
        config=types.GenerateContentConfig(
            system_instruction=f"""
                You are a sophisticated HR AI Assistant. 
                Your goal is to provide concise, data-driven insights using your tools.

                

                OPERATIONAL RULES:
                - Use tools for any data-specific queries (attendance, lists).
                - Use the conversation history to maintain context of the current task.
                - Format data using Markdown tables for readability.
                - Maintain a professional yet approachable tone.
            """,
            tools=[get_employees, get_attendance, get_absent_employees],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False)
        )
    )

    # 6. EXECUTION & DATABASE PERSISTENCE
    try:
        response = chat.send_message(message)
        reply = response.text or "I'm sorry, I couldn't process that request."
    except Exception as e:
        reply = f"Agent Error: {str(e)}"

    # Save to DB in a single transaction
    ChatMessage.objects.bulk_create([
        ChatMessage(user=user, role="user", content=message),
        ChatMessage(user=user, role="model", content=reply)
    ])

    return reply
