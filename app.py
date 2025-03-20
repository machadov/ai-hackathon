import os
import json

from chatlas import ChatBedrockAnthropic
from dotenv import load_dotenv
from shiny.express import ui
from simple_salesforce import Salesforce

# Load environment variables from a .env file
success = load_dotenv()

def get_salesforce_data(soql: str):
    """
    Execute a SOQL query against the Salesforce REST API to fetch the desired data. The Salesforce REST API response is returned as a JSON string.
    """
    
    try:
        # Connect to the Salesforce API
        sf = Salesforce(
            username=os.getenv("SALESFORCE_USERNAME"),
            password=os.getenv("SALESFORCE_PASSWORD"),
            security_token=os.getenv("SALESFORCE_SECURITY_TOKEN"),
            version=os.getenv("SALESFORCE_API_VERSION"),
            domain=os.getenv("SALESFORCE_DOMAIN")
        )
        
        # Execute the SOQL query
        result = sf.query_all(soql)
        return json.dumps(result)
    except Exception as e:
        return f"An error occurred: {e}"

# Load the content of the salesforce-prompt.md file
with open('system-prompt.md', 'r') as file:
    system_prompt = file.read()

# Initialize the chat model with OpenAI
chat_model = ChatBedrockAnthropic(
    model="us.anthropic.claude-3-5-sonnet-20241022-v2:0", 
    system_prompt=system_prompt, 
    aws_profile=os.getenv("AWS_PROFILE")
)
chat_model.register_tool(get_salesforce_data)

# Set some Shiny page options
ui.page_opts(title="Sales Assistant Chatbot", layout="centered")

with ui.layout_columns(col_widths=(9, 3)): 
    with ui.card():
        # ui.card_header("Card header")
        # Create and display a Shiny chat component
        chat = ui.Chat(
            id="chat",
            messages=["Hey! Thank you for contacting me. \n\n Ask me any questions about customers, products, opportunity, orders and I am will do my best to help! \n\n I will try my best to make your life easier by connecting and searching for information for you on various platforms so that you don't have to."],
        )
        chat.ui()
    with ui.card():
         ui.card_header("Find below some things you can ask me:")
         ui.markdown('''
                     - Which are the company's most valuable customers?
                     - Create a quarterly business review (QBR) presentation for a customer.
                     - What are the main contacts of the account?
                     - Which opportunities are closing this month?
                     ''')

# Define a callback to run when the user submits a message
@chat.on_user_submit
async def handle_user_input(user_input: str):
    response = chat_model.stream(user_input)
    await chat.append_message_stream(response)