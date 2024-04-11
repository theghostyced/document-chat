import os
from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI
import time
import functions

load_dotenv()

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"],
    organization="org-oYVKtT5sFiNpcO6eApTpupX2",
)

if "assistant_id" not in st.session_state:
    st.session_state.assistant_id = functions.create_assistant(client)

# Initialize all the session state variables
if "file_id" not in st.session_state:
    st.session_state.file_id = []

if "thread_id" not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id

if "messages" not in st.session_state:
    st.session_state.messages = []


def wait_on_run(run):
    print("run", run, "thread_id", st.session_state.thread_id)
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread_id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run


def process_file(file):
    if file:
        try:
            uploaded_file = client.files.create(file=file, purpose="assistants")
            file_id = uploaded_file.id
            st.session_state.file_id = file_id
            st.sidebar.success("File uploaded successfully.")
            return file_id
        except Exception as e:
            print(f"Failed to upload file: {str(e)}")
            st.error(f"Failed to upload file: {str(e)}")
            return None


def get_response(question):
    try:
        message = client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=question,
            file_ids=[st.session_state.file_id],
        )
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=st.session_state.assistant_id,
        )
        run = wait_on_run(run)

        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )
        message_content = messages.data[0].content[0].text
        # Remove annotations
        annotations = message_content.annotations
        for annotation in annotations:
            message_content.value = message_content.value.replace(annotation.text, "")
        return message_content.value
    except Exception as e:
        st.error(f"Error in generating response: {str(e)}")
        return None


st.subheader("Chat with your Data")

uploaded_file = st.sidebar.file_uploader(
    "Upload your CSV or Excel file", type=["csv", "xlsx"]
)
if uploaded_file is not None:
    process_file(uploaded_file)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("How can I help you?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner(text="Generating response..."):
            response = get_response(prompt)
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
