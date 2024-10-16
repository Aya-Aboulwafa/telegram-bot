import pandas as pd
from langchain_ollama.llms import OllamaLLM
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, filters

# Load your cleaned CSV data
df = pd.read_csv("cleaneddata.csv")

# Set up LLaMA model with optimized parameters
llm = OllamaLLM(
    model="llama3.2:3b",        # Model version
    temperature=0.7,         # Balance between randomness and coherence
    top_k=40,                # Ensures diversity while maintaining relevance
    top_p=0.9,               # Nucleus sampling for dynamic response generation
    max_tokens=300           # Limit the response length for clarity and precision
)

# Function to create the prompt based on user input
def create_prompt(choice, sender_name=None, task_name=None, team_name=None, task_date=None):
    filtered_messages = df.copy()

    if sender_name:
        filtered_messages = filtered_messages[filtered_messages['sender'].str.contains(sender_name, case=False, na=False)]

    if task_name:
        filtered_messages = filtered_messages[filtered_messages['message'].str.contains(task_name, case=False, na=False)]

    if team_name:
        filtered_messages = filtered_messages[filtered_messages['message_thread_id'].str.contains(team_name, case=False, na=False)]

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
        Extract and summarize the complete report for team member '{sender_name}'.
        (Summarize all tasks completed by '{sender_name}':\n\nMessages:\n{combined_messages})

        **Example Output:**
        The team is working on several initiatives related to various areas of development. Here's a summary of the key points:

        **Projects:**

        1. **Project A**: Ongoing efforts in this area.
        2. **Project B**: Integrating new technologies and methodologies.
        3. **Project C**: Developing features that enhance user experience.
        4. **Project D**: Collaborating on cross-functional initiatives.

        **Challenges:**

        1. **Challenge 1**: Facing difficulties in integration with existing platforms.
        2. **Challenge 2**: Experiencing issues with resource allocation and timing.
        3. **Challenge 3**: Addressing unexpected technical obstacles.

        **Progress:**

        1. **Completed tasks**: Achievements in various areas of focus.
        2. **In progress**: Continued development on critical components.

        **Meetings:**

        1. **Regular Meetings**: Participating in scheduled discussions to track progress.
        2. **Key Discussions**: Engaging with stakeholders on project updates.

        **Future Plans:**

        1. **Next Steps**: Outlining upcoming actions to maintain momentum.
        2. **Strategic Goals**: Setting targets for the next phase of work.
        """

    elif choice == '2':
      prompt = f"""
        Summarize all activities related to the task '{task_name}':\n\nMessages:\n{combined_messages}

        **Example Output:**
        The activities surrounding the task '{task_name}' encompass various efforts and developments:

        **Progress:**
        - Ongoing advancements have been made, contributing to the overall objectives.

        **Challenges:**
        - Encountered some obstacles that impacted the workflow.

        **Future Steps:**
        - Plans are in place to navigate challenges and ensure continued progress.
        """


    elif choice == '3':
        prompt = f"""
        Example:
        The following is a summary of the task journey for '{task_name}':
        Describe the overall task journey for '{task_name}':\n\nMessages:\n{combined_messages}

        **Example Output:**
        The journey of the task '{task_name}' reflects various significant developments:

        **Key Developments:**
        - Notable actions have shaped the direction of the task.

        **Challenges Faced:**
        - Various challenges have influenced the approach taken for the task.

        **Current Status:**
        - The task is at a pivotal stage, with efforts directed towards its successful completion.
        """


    elif choice == '4':
        prompt = f"""
        Provide all details about activities on '{task_date}':\n\nMessages:\n{combined_messages}

        **Example Output:**
        On '{task_date}', a variety of key activities were recorded:

        **Activities:**
        - A range of tasks and discussions contributed to overall progress.

        **Highlights:**
        - Significant achievements and challenges were observed.

        **Conclusion:**
        - The events of '{task_date}' have laid the groundwork for future activities.
        """


    elif choice == '5':
        prompt = f"""
        Summarize tasks related to the team '{team_name}':\n\nMessages:\n{combined_messages}

        **Example Output:**
        The following summarizes the tasks associated with the team '{team_name}':

        **Task Overview:**
        - A compilation of efforts highlights the team's contributions.

        **Achievements:**
        - Noteworthy accomplishments demonstrate the team's capabilities.

        **Next Steps:**
        - Future actions are planned to enhance performance and address challenges.
        """


    elif choice == '6':
        prompt = f"""
        Example:
        Below is a list of tasks associated with '{sender_name}':
        List all tasks by '{sender_name}':\n\nMessages:\n{combined_messages}"""

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
            response = llm.invoke(prompt)
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
        response = llm.invoke(prompt)
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



