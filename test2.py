import pandas as pd
from langchain_ollama.llms import OllamaLLM
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext

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

    # Prompts based on choices
    if choice == '1':
        prompt = f"""
        Example:
        Response: Here is a summary of all the messages sent by '{sender_name}':

        Overall Summary:

        {sender_name} has been working on various tasks related to designing and developing different screens and features for an application. They have been attending daily meetings with R&D and Dev teams, receiving feedback from colleagues, and implementing changes based on that feedback.

        Specific Tasks and Achievements:

        * Designed and implemented screens using Material 3 (e.g., room limited reached, calendar format, filter & quick actions, action screen, running meeting screen)
        * Resolved git issues with a team member
        * Attended multiple review and audit sessions with colleagues
        * Learned Tailwind CSS and used it to design home and calendar tab screens
        * Designed subscription tab with different states using Shadcn UI
        * Redesigned recording tab and share record options using Shadcn
        * Created a system design for the V Chat app

        Key Meetings and Discussions:

        * Held extensive meetings with Masreya, Abdallah, Toqaa, Serag, and Abdelghafaur to discuss various topics related to the application's flow and design
        * Participated in quick discussions with colleagues to solve issues or clarify doubts
        * Developed a plan for August tasks and regularly reviewed progress

        Skills and Knowledge Acquired:

        * Learned Material 3, Tailwind CSS, and Shadcn UI
        * Improved their understanding of the application's flow and design principles

        Summarize all tasks assigned to '{sender_name}':\n\nMessages:\n{combined_messages}"""
    elif choice == '2':
        prompt = f"""
        Example:
        Response: Here is a summary of all activities related to the task '{task_name}':

        Task Overview:

        The task '{task_name}' was initiated to improve the user experience on the calendar screen. The goal was to implement a new filtering system that would allow users to quickly navigate to specific dates.

        Steps Taken:

        * Conducted initial research on user needs and identified key features for the filter system.
        * Designed the UI/UX for the filter system and reviewed it with the design team.
        * Implemented the filter system using Material 3 and integrated it into the existing calendar component.
        * Tested the filter system with various data sets to ensure it worked correctly.

        Collaborations:

        * Worked closely with the UX team to ensure the filter system met user expectations.
        * Coordinated with the backend team to ensure data flow between the calendar and filter components was seamless.

        Current Status:

        The task '{task_name}' has been successfully completed, with all initial goals met. The filter system is now live and has received positive feedback from users.

        Summarize all activities related to the task '{task_name}':\n\nMessages:\n{combined_messages}"""
    elif choice == '3':
        prompt = f"""
        Example:
        Response: Here is a detailed overview of the task journey for '{task_name}':

        Task Journey:

        The task '{task_name}' began as a high-priority item due to its impact on the overall user experience. It required a significant overhaul of the existing navigation system.

        Planning Phase:

        * Identified the need for a more intuitive navigation system after user feedback indicated confusion with the current layout.
        * Conducted several brainstorming sessions with the design team to explore potential solutions.
        * Finalized a design that would simplify the navigation process while maintaining all existing functionality.

        Execution:

        * Broke down the task into smaller, manageable components and assigned them to relevant team members.
        * Implemented the new navigation system in stages, starting with the main menu and moving to submenus.
        * Regularly reviewed progress with the team and made adjustments as needed to stay on schedule.

        Review and Iteration:

        * Conducted multiple testing rounds to ensure the new system worked seamlessly across all devices.
        * Gathered feedback from a small group of users and made iterative improvements based on their experiences.

        Completion:

        The task '{task_name}' was successfully completed with all objectives met. The new navigation system is now live and has been well-received by users.

        Describe the overall task journey for '{task_name}':\n\nMessages:\n{combined_messages}"""
    elif choice == '4':
        prompt = f"""
        Example:
        Response: Here are the details of tasks performed on '{task_date}':

        Overview of the Day:

        On '{task_date}', the focus was on finalizing the design for the application's notification system and addressing several bugs reported in the previous version.

        Tasks Completed:

        * Finalized the UI/UX design for the notification system and reviewed it with the design team.
        * Fixed bugs related to the message display issue in the chat module.
        * Coordinated with the QA team to verify the bug fixes and ensure no new issues were introduced.

        Challenges:

        * Encountered a challenge with the notification system design not being compatible with older devices. Worked closely with the development team to find a workaround.

        Team Interactions:

        * Had a meeting with the QA team to discuss the bugs and prioritize the ones that needed immediate attention.
        * Reviewed the notification system design with the product manager and made necessary adjustments.

        Provide details about tasks on '{task_date}':\n\nMessages:\n{combined_messages}"""
    elif choice == '5':
        prompt = f"""
        Example:
        Response: Here is a summary of tasks associated with the team '{team_name}':

        Team Overview:

        The '{team_name}' team is responsible for the development and maintenance of the application's core features. Recently, they have been focusing on enhancing the user experience across multiple platforms.

        Key Tasks:

        * Implemented a new authentication system that allows users to log in using their social media accounts.
        * Redesigned the settings page to provide a more intuitive and user-friendly interface.
        * Fixed critical bugs reported in the Android version of the application.

        Collaborations:

        * Worked closely with the UX team to ensure the new settings page met user expectations.
        * Coordinated with the backend team to integrate the new authentication system seamlessly.

        Achievements:

        * Successfully reduced the login time by 30% with the new authentication system.
        * Received positive feedback from users on the redesigned settings page.

        Summarize tasks related to the team '{team_name}':\n\nMessages:\n{combined_messages}"""
    elif choice == '6':
        prompt = f"""
        Example:
        Response: Here is a list of tasks associated with '{sender_name}':

        list Tasks  for {sender_name}:
        

        * Designed and implemented the user profile page, ensuring it was fully responsive across all devices.
        * Collaborated with the QA team to identify and fix issues related to the notification system.
        * Participated in brainstorming sessions for the upcoming feature release, providing valuable insights based on user feedback.

        
        * Worked with the development team to optimize the application's performance, resulting in a 20% improvement in load times.
        * Held regular meetings with the design team to ensure the user profile page aligned with the overall design vision.


        * Enhanced knowledge of responsive design techniques and best practices.
        * Gained experience in cross-team collaboration and project management.

        List tasks with time by '{sender_name}':\n\nMessages:\n{combined_messages}"""
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


        #retrive stored choice
        stored_choice = context.user_data.get("choice")

        #log selected sender & choice
        print(f"Sender Name: {sender_name}")
        print(f"Stored Choice: {stored_choice}")

        #Generate promt
        prompt = create_prompt(stored_choice, sender_name=sender_name)

        #log generated prompt
        print(f"Generated Prompt: {prompt}")


        #get responce from LLM
        response = llm(prompt)


        #log the response
        print(f"Respose: {response}")


        #send respose to the user
        await query.message.reply_text(response)
        keyboard = [
            [InlineKeyboardButton("Choose another option", callback_data='choose_again')],
            [InlineKeyboardButton("End conversation", callback_data='end_conversation')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Would you like to choose another option or end the conversation?", reply_markup=reply_markup)
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

        #Ask if user want other option
        # await start(update, context)
    # else:
    #     # Handle other cases 
    #     context.user_data["choice"] = choice
    #     await query.edit_message_text("Please provide the required input:")


def main() -> None:
    # Replace 'YOUR_TOKEN_HERE' with your bot's token
    application = Application.builder().token("7478988236:AAEdP5QJmtu8oKw1Cnd9gGAzeQl-1EmUeiM").build()

    # Register commands and handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_click))

    # Start the Bot
    application.run_polling()

if __name__ == "__main__":
    main()
