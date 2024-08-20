import pandas as pd
from langchain_ollama.llms import OllamaLLM
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, filters

# Load your cleaned CSV data
df = pd.read_csv("cleaneddata.csv")

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
        return "No data found for the given criteria."

    combined_messages = "\n".join(filtered_messages['message'].astype(str).tolist())

    # Ensure combined_messages is not None
    if combined_messages is None:
        combined_messages = "No messages available."

    # Construct prompt based on choice
    if choice == '1':
        prompt = f"""
        Example:
        Response: Below is a summary of the messages sent by '{sender_name}':

        Overall Summary:
        {sender_name} has been actively involved in various tasks and collaborations. Their efforts have contributed significantly to the project, showcasing a blend of technical skills and team cooperation.

        Specific Contributions:

        * Participated in key tasks related to design, development, and implementation.
        * Engaged with team members to resolve issues and enhance workflows.
        * Continuously updated skills and applied them effectively in ongoing projects.

        Key Collaborations:

        * Worked closely with various team members to ensure project goals were met.
        * Regularly attended meetings to discuss progress and plan future tasks.

        Skills and Knowledge Gained:

        * Acquired and applied new skills, contributing to personal and team growth.

        Summarize all tasks assigned to '{sender_name}':\n\nMessages:\n{combined_messages}"""

    elif choice == '2':
        prompt = f"""
        Example:
        Response: Below is a summary of activities related to the task '{task_name}':

        Task Overview:

        The task '{task_name}' was initiated to address a key area of the project, with a focus on improving specific features or components.

        Key Actions:

        * Researched and identified critical aspects to be addressed.
        * Designed and implemented solutions in line with project goals.
        * Collaborated with relevant teams to ensure smooth integration and functionality.

        Collaborative Efforts:

        * Worked with various teams to align task outcomes with project requirements.

        Summarize all activities related to the task '{task_name}':\n\nMessages:\n{combined_messages}"""

    elif choice == '3':
        prompt = f"""
        Example:
        Response: The following is a summary of the task journey for '{task_name}':

        Task Journey:

        The task '{task_name}' was undertaken to make significant improvements to an important aspect of the project, requiring careful planning and execution.

        Planning Phase:

        * Identified key challenges and outlined potential solutions.
        * Collaborated with the team to refine the approach.

        Execution:

        * Implemented the task in phases, ensuring continuous progress.
        * Monitored and adjusted the approach as needed to stay on track.

        Review and Iteration:

        * Conducted thorough reviews and iterations to refine the final product.

        Completion:

        The task '{task_name}' was successfully completed, meeting all objectives.

        Describe the overall task journey for '{task_name}':\n\nMessages:\n{combined_messages}"""

    elif choice == '4':
        prompt = f"""
        Example:
        Response: Below is an overview of activities on '{task_date}':

        Overview of the Day:

        On '{task_date}', several tasks were completed, contributing to the overall progress of the project.

        Completed Tasks:

        * Focused on key areas that needed attention, ensuring they were addressed effectively.
        * Collaborated with the team to verify the completion of tasks.

        Team Interactions:

        * Engaged in discussions and meetings to align on priorities and next steps.

        Provide details about tasks on '{task_date}':\n\nMessages:\n{combined_messages}"""

    elif choice == '5':
        prompt = f"""
        Example:
        Response: Below is a summary of tasks completed by the '{team_name}' team:

        Team Overview:

        The '{team_name}' team has been responsible for key aspects of the project, driving progress in critical areas.

        Major Contributions:

        * Focused on enhancing specific features and ensuring smooth project execution.
        * Collaborated with other teams to integrate new developments seamlessly.

        Summarize tasks related to the team '{team_name}':\n\nMessages:\n{combined_messages}"""

    elif choice == '6':
        prompt = f"""
        Example:
        Response: Below is a summary of tasks associated with '{sender_name}':

        Summary of Tasks:

        * Actively contributed to various aspects of the project, focusing on key deliverables.
        * Collaborated with the team to resolve issues and enhance performance.

        Summarize all tasks by '{sender_name}':\n\nMessages:\n{combined_messages}"""

    else:
        prompt = "Invalid choice. Please select a valid option."

    return prompt

# Start command to display buttons
async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Summarize All Reports of Member Team", callback_data='1')],
        [InlineKeyboardButton("Summarize All Reports of Specific Task", callback_data='2')],
        [InlineKeyboardButton("Search for Specific Task Journey", callback_data='3')],
        [InlineKeyboardButton("Search by Task Date", callback_data='4')],
        [InlineKeyboardButton("Search by Team Name Tasks", callback_data='5')],
        [InlineKeyboardButton("List reports of a Member Team", callback_data='6')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text("Please choose an option:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text("Please choose an option:", reply_markup=reply_markup)

# Callback query handler to handle button clicks
async def button_click(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    choice = query.data

    if choice in ['1', '6']:
        context.user_data["choice"] = choice

        senders = df['sender'].unique()
        keyboard = []
        row = []
        for sender in senders:
            row.append(InlineKeyboardButton(sender, callback_data=f'sender_{sender}'))
            if len(row) == 2:  # If the row has 2 buttons, add it to the keyboard and start a new row
                keyboard.append(row)
                row = []
        
        if row:  # Add the last row if it contains any buttons
            keyboard.append(row)
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Please select a sender:", reply_markup=reply_markup)

    elif choice.startswith('sender_'):
        sender_name = choice.split('sender_')[1]
        context.user_data['sender_name'] = sender_name

        # Retrieve stored choice
        stored_choice = context.user_data.get("choice")

        # Log selected sender & choice
        print(f"Sender Name: {sender_name}")
        print(f"Stored Choice: {stored_choice}")

        # Generate prompt
        prompt = create_prompt(stored_choice, sender_name=sender_name)

        # Check if prompt is valid
        if not prompt:
            prompt = "The prompt could not be generated. Please try again."

        # Get response from LLM
        try:
            response = llm(prompt)
        except Exception as e:
            response = f"An error occurred: {e}"

        # Log the response
        print(f"Response: {response}")

        # Send response to the user
        await query.message.reply_text(response)

        keyboard = [
            [InlineKeyboardButton("Choose another option", callback_data='choose_again')],
            [InlineKeyboardButton("End conversation", callback_data='end_conversation')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Would you like to choose another option or end the conversation?", reply_markup=reply_markup)

    elif choice in ['2', '3', '4', '5']:
        context.user_data["choice"] = choice
        await ask_for_input(update, context)

    elif choice == 'choose_again':
        # Restart the conversation
        await start(update, context)

    elif choice == 'end_conversation':
        # End the conversation with a farewell message
        await query.message.reply_text("Thank you! If you need anything else, feel free to start a new conversation.")

    else:
        # Handle other cases where choice might not be a sender selection
        context.user_data["choice"] = choice
        await query.edit_message_text("Please provide the required input:")

# Function to ask for user input after choosing options 2-5
async def ask_for_input(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    choice = query.data

    if choice == '2':
        await query.message.reply_text("Please enter the task name:")
    elif choice == '3':
        await query.message.reply_text("Please enter the task name for the task journey:")
    elif choice == '4':
        await query.message.reply_text("Please enter the task date (e.g., YYYY-MM-DD):")
    elif choice == '5':
        await query.message.reply_text("Please enter the team name:")

    # Store the user's choice for later use
    context.user_data["choice"] = choice

# Function to handle user input for options 2-5
async def handle_input(update: Update, context: CallbackContext) -> None:
    user_input = update.message.text
    choice = context.user_data.get("choice")

    # Initialize variables to pass into the prompt
    task_name = None
    task_date = None
    team_name = None

    if choice == '2':
        task_name = user_input
    elif choice == '3':
        task_name = user_input
    elif choice == '4':
        task_date = user_input
    elif choice == '5':
        team_name = user_input

    # Generate the prompt based on the user's choice and input
    prompt = create_prompt(choice, task_name=task_name, task_date=task_date, team_name=team_name)

    # Check if prompt is valid
    if not prompt:
        prompt = "The prompt could not be generated. Please try again."

    # Get response from LLM
    try:
        response = llm(prompt)
    except Exception as e:
        response = f"An error occurred: {e}"

    # Log the response
    print(f"Response: {response}")

    # Send response to the user
    await update.message.reply_text(response)

    # Offer the user a chance to choose another option or end the conversation
    keyboard = [
        [InlineKeyboardButton("Choose another option", callback_data='choose_again')],
        [InlineKeyboardButton("End conversation", callback_data='end_conversation')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Would you like to choose another option or end the conversation?", reply_markup=reply_markup)

# Update the main function to include the new handlers
def main() -> None:
    # Replace 'YOUR_TOKEN_HERE' with your bot's token
    application = Application.builder().token("7478988236:AAEdP5QJmtu8oKw1Cnd9gGAzeQl-1EmUeiM").build()

    # Register commands and handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_click))
    application.add_handler(CallbackQueryHandler(ask_for_input, pattern='^(2|3|4|5)$'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))

    # Run the bot
    application.run_polling()

if __name__ == '__main__':
    main()
