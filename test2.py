import pandas as pd
from langchain_ollama.llms import OllamaLLM
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, CallbackContext, filters

# Load your cleaned CSV data
df = pd.read_csv("cleaneddata - cleaneddata.csv")

# Set up LLaMA model
llm = OllamaLLM(model="llama3.1")

# Function to create the prompt based on user input
def create_prompt(choice, sender_name=None, task_name=None, team_name=None, task_date=None):
    filtered_messages = df.copy()

    if sender_name:
        filtered_messages = filtered_messages[filtered_messages['sender'].str.contains(sender_name, case=False, na=False)]

    if task_name:
        filtered_messages = filtered_messages[filtered_messages['message'].str.contains(task_name, case=False, na=False)]

    if team_name:
        filtered_messages = filtered_messages[filtered_messages['chat_title'].str.contains(team_name, case=False, na=False)]

    if task_date:
        filtered_messages = filtered_messages[filtered_messages['date'].str.contains(task_date, case=False, na=False)]

    if filtered_messages.empty:
        return f"No data found for the given criteria."

    combined_messages = "\n".join(filtered_messages['message'].astype(str).tolist())

    if choice == '1':
        prompt = f"""
        Example:
        Response: Here is a summary of all the messages sent by '{sender_name}':
        Summarize all tasks assigned to '{sender_name}':\n\nMessages:\n{combined_messages}"""
    elif choice == '2':
        prompt = f"""
        Example:
        Response: Here is a summary of all activities related to the task '{task_name}':
        Summarize all activities related to the task '{task_name}':\n\nMessages:\n{combined_messages}"""
    elif choice == '3':
        prompt = f"""
        Example:
        Response: Here is a detailed overview of the task journey for '{task_name}':
        Describe the overall task journey for '{task_name}':\n\nMessages:\n{combined_messages}"""
    elif choice == '4':
        prompt = f"""
        Example:
        Response: Here are the details of tasks performed on '{task_date}':
        Provide details about tasks on '{task_date}':\n\nMessages:\n{combined_messages}"""
    elif choice == '5':
        prompt = f"""
        Example:
        Response: Here is a summary of tasks associated with the team '{team_name}':
        Summarize tasks related to the team '{team_name}':\n\nMessages:\n{combined_messages}"""
    elif choice == '6':
        prompt = f"""
        Example:
        Response: Here is a list of tasks associated with '{sender_name}':
        List tasks with time by '{sender_name}':\n\nMessages:\n{combined_messages}"""
    else:
        prompt = "Invalid choice. Please select a valid option."

    return prompt

# Start command to display buttons
async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Summeize All Reports of Member Team", callback_data='1')],
        [InlineKeyboardButton("Summeize All Reports of Specific Task", callback_data='2')],
        [InlineKeyboardButton("Search for Specific Task Journey", callback_data='3')],
        [InlineKeyboardButton("Search by Task Date", callback_data='4')],
        [InlineKeyboardButton("Search by Team Name Tasks", callback_data='5')],
        [InlineKeyboardButton("List reports of a Member Team", callback_data='6')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please choose an option:", reply_markup=reply_markup)

# Callback query handler to handle button clicks
async def button_click(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    context.user_data["choice"] = query.data

# Prompt the user to provide the required input based on their choice
    if query.data in ['1', '6']:
        # Provide a list of senders for the user to choose from
        senders = df['sender'].unique()
        keyboard = [[InlineKeyboardButton(sender, callback_data=sender)] for sender in senders]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Please select a sender:", reply_markup=reply_markup)
    elif query.data == '2':
        await query.edit_message_text("Please enter the task name:")
    elif query.data == '3':
        await query.edit_message_text("Please enter the task name:")
    elif query.data == '4':
        await query.edit_message_text("Please enter the task date (format YYYY-MM-DD):")
    elif query.data == '5':
        await query.edit_message_text("Please enter the team name:")

# Handle text input or sender selection from the user after they press a button
async def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    choice = context.user_data.get("choice")

    sender_name = task_name = team_name = task_date = None

    if choice == '1' or choice == '6':
        sender_name = user_message
    elif choice == '2':
        task_name = user_message
    elif choice == '3':
        task_name = user_message
    elif choice == '4':
        task_date = user_message
    elif choice == '5':
        team_name = user_message

    # Create the prompt based on user input
    prompt = create_prompt(choice, sender_name, task_name, team_name, task_date)
    response = llm(prompt)

    # Send the response back to the user
    await update.message.reply_text(response)
    
    # Send options again for another round of interaction
    await start(update, context)

def main() -> None:
    # Replace 'YOUR_TOKEN_HERE' with your bot's token
    application = Application.builder().token("7478988236:AAEdP5QJmtu8oKw1Cnd9gGAzeQl-1EmUeiM").build()

    # Register commands and handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_click))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot
    application.run_polling()

if __name__ == "__main__":
    main()