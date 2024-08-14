import pandas as pd
from langchain_ollama.llms import OllamaLLM
import sys

# Load the cleaned CSV file using pandas for easier data manipulation
df = pd.read_csv("cleaneddata.csv")

# Set up LLaMA 3.1:8B model and run on CPU
llm = OllamaLLM(model="llama3.1")

# Function to create the prompt based on user choice
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
                    Response:  Here is a summary of all the messages sent by 'Sender name':

                    Overall Summary

                    Sender name has been working on various tasks related to designing and developing different screens and features for an application. she has been attending daily meetings with R&D and Dev teams, receiving feedback from colleagues, and implementing changes based on those feedbacks.

                    Specific Tasks and Achievements

                    * Designed and implemented screens using Material 3 (e.g., room limited reached, calendar format, filter & quick actions, action screen, running meeting screen)
                    * Resolved git issues with a team member
                    * Attended multiple review and audit sessions with colleagues
                    * Learned Tailwind CSS and used it to design home and calendar tab screens
                    * Designed subscription tab with different states using Shadcn UI
                    * Redesigned recording tab and share record options using Shadcn
                    * Made a system design for V chat app

                    Key Meetings and Discussions

                    * Had long meetings with Masreya, Abdallah, Toqaa, Serag, and Abdelghafaur to discuss various topics related to the application's flow and design
                    * Had quick discussions with colleagues to solve issues or clarify doubts
                    * Made a plan for August tasks and reviewed progress regularly

                    Skills and Knowledge Acquired

                    * Learned Material 3, Tailwind CSS, and Shadcn UI
                    * Improved his understanding of the application's flow and design principles
                    
                    Summarize all tasks assigned to '{sender_name}':\n\nMessages:\n{combined_messages}"""
    elif choice == '2':
        prompt = (
            f"Task Summary for the specific task '{task_name}':\n\n"
            f"Summarize all activities related to the task '{task_name}':\n\nMessages:\n{combined_messages}"
        )
    elif choice == '3':
        prompt = (
            f"Task journey for the specific task '{task_name}':\n\n"
            f"Describe the overall task journey for '{task_name}':\n\nMessages:\n{combined_messages}"
        )
    elif choice == '4':
        prompt = (
            f"Details about tasks on '{task_date}':\n\n"
            f"Provide details about tasks on '{task_date}':\n\nMessages:\n{combined_messages}"
        )
    elif choice == '5':
        prompt = (
            f"List and summarize tasks associated with the team '{team_name}':\n\n"
            f"Tasks related to the team '{team_name}':\n\nMessages:\n{combined_messages}"
        )
    elif choice == '6':
        prompt = (
            f"List tasks associated by '{sender_name}':\n\n"
            f"Tasks related to the team '{sender_name}':\n\nMessages:\n{combined_messages}"
        )
    else:
        prompt = "Invalid choice. Please select a valid option."

    return prompt

# Interactive query loop
while True:
    print("Choose what you want to search:")
    print("1. Search by Sender Name")
    print("2. Search by Specific Task")
    print("3. Search for Task Journey of a Specific Task")
    print("4. Search by Task Date")
    print("5. Search by Team Name")
    print("6. List reports of specific name")
    choice = input("Enter your choice (1-5) or 'exit' to quit: ")

    if choice.lower() == 'exit':
        print('Exiting')
        sys.exit()

    sender_name = task_name = team_name = task_date = None

    if choice == '1':
        sender_name = input("Enter sender name: ")
    elif choice == '2':
        task_name = input("Enter task name: ")
    elif choice == '3':
        task_name = input("Enter task name: ")
    elif choice == '4':
        task_date = input("Enter task date (format YYYY-MM-DD): ")
    elif choice == '5':
        team_name = input("Enter team name: ")
    elif choice == '6':
        sender_name = input("Enter the name: ")
    else:
        print("Invalid choice. Please select a valid option.")
        continue

    # Create the prompt
    prompt = create_prompt(choice, sender_name, task_name, team_name, task_date)

    # Debugging statements
    print("Prompt Type:", type(prompt))
    print("Prompt Content:", prompt[:500])  # Print the first 500 characters for brevity

    # Run the prompt through the LLM directly
    result = llm(prompt)
    print("Response: ", result)

    # if __name__ == "__main__":
    #     create_prompt()

    
