import streamlit as st
import ubiops
import os

# App title

st.set_page_config(page_title=" Llama 3 Chatbot Assistent")

# Replicate Credentials

with st.sidebar:
   st.title(' Llama 3.1 Chatbot Assistent')

   # Initialize the variable outside the if-else block

   if 'UBIOPS_API_TOKEN' in st.secrets:
       st.success('API key already provided!')
       ubiops_api_token = st.secrets['UBIOPS_API_TOKEN']
   else:
       ubiops_api_token = st.text_input('Enter UbiOps API token:', type='password')

       if not ubiops_api_token.startswith('Token '):
           st.warning('Please enter your credentials!', icon='')
       else:
           st.success('Proceed to entering your prompt message!', icon='')

   st.markdown(' Learn how to build this app in this [blog](#link-to-blog)!')

# Move the environment variable assignment outside the with block
os.environ['UBIOPS_API_TOKEN'] = ubiops_api_token




# Store LLM-generated responses

if "messages" not in st.session_state.keys():

   st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]




# Display or clear chat messages

for message in st.session_state.messages:

   with st.chat_message(message["role"]):

       st.write(message["content"])




def clear_chat_history():

   st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

st.sidebar.button('Clear Chat History', on_click=clear_chat_history)




# Function for generating Mistral response


def generate_mistral_response(prompt_input):

   string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."

   for dict_message in st.session_state.messages:

       if dict_message["role"] == "user":

           string_dialogue += "User: " + dict_message["content"] + "\\n\\n"

       else:

           string_dialogue += "Assistant: " + dict_message["content"] + "\\n\\n"



   # Request mistral

   api = ubiops.CoreApi()

   response = api.deployment_version_requests_create(

       project_name = st.secrets["project_name"],

       deployment_name = st.secrets["deployment_name"],

       version = st.secrets["version"],

       data = {"prompt" : prompt_input,
               "config": {}},

       timeout= 3600

   )

   api.api_client.close()

   return response.result['output']




# User-provided prompt

if prompt := st.chat_input(disabled=not ubiops_api_token):

   st.session_state.messages.append({"role": "user", "content": prompt})

   with st.chat_message("user"):

       st.write(prompt)




# Generate a new response if the last message is not from assistant

if st.session_state.messages[-1]["role"] != "assistant":

   with st.chat_message("assistant"):

       with st.spinner("Thinking..."):

           response = generate_mistral_response(prompt)

           placeholder = st.empty()

           full_response = ''

           for item in response:

               full_response += item

               placeholder.markdown(full_response)

           placeholder.markdown(full_response)

   message = {"role": "assistant", "content": full_response}

   st.session_state.messages.append(message)
