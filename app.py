import streamlit as st
from QA_utils import make_output
import openai



st.title('🦜🔗 Robotics QA Bot 🦜🔗')


# Function to validate OpenAI API key
def validate_openai_api_key(api_key):
    try:
        openai.api_key = api_key
        # Make a test call to validate the API key
        openai.Engine.list()
        return True
    except openai.error.AuthenticationError:
        return False
    except openai.error.OpenAIError as e:
        st.error(f"OpenAI API error occurred: {e}")
        return False
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return False

openai_api_key = st.text_input("Enter OpenAI API Key", type='password')

if openai_api_key:
    if validate_openai_api_key(openai_api_key):
        st.success("API Key loaded successfully!")
    
    
        st.title("Question Answering System")

        # Text input for the user query
        user_query = st.text_input("Enter your question:")
    
        if user_query:
            result, metadata = make_output(user_query,api_key=openai_api_key)
        
            st.write("Answer: ", result)
         
            #display soures
            st.write("Sources: ",metadata)
    else:
        st.error("Invalid OpenAI API Key. Please enter a valid key.")
else:
    st.warning("Please enter your OpenAI API key to start.")
