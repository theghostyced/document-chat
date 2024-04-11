import json
import os

assistant_instructions = """You are a helpful assistant that answers to questions of users based on the knowledge base provided (within the attached file by user). If the user question requires you to perform sql query, computation or any other operation on the knowledge base, you must do so."""

def create_assistant(client):
    assistant_file_path = 'assistant.json'

    # If there is an assistant.json file already, then load that assistant
    if os.path.exists(assistant_file_path):
        with open(assistant_file_path, 'r') as file:
            assistant_data = json.load(file)
            assistant_id = assistant_data['assistant_id']
            print("Loaded existing assistant ID.")
    else:
        # If no assistant.json is present, create a new assistant using the below specifications
        assistant = client.beta.assistants.create(
            instructions=assistant_instructions,
            model="gpt-4-1106-preview",
            tools=[
                {
                    "type": "retrieval"  # This adds the knowledge base as a tool
                }
            ])

        # Create a new assistant.json file to load on future runs
        with open(assistant_file_path, 'w') as file:
            json.dump({'assistant_id': assistant.id}, file)
            print("Created a new assistant and saved the ID.")

        assistant_id = assistant.id

    return assistant_id
