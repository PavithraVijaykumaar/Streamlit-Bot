# importing libraries
import tempfile
import streamlit as st
from mbot_backend import pdf_reader,get_conversation_chain,get_text_chunks,get_vectorstore,csv_reader
from langchain.callbacks import get_openai_callback
from langchain. prompts import PromptTemplate
prompt= PromptTemplate(input_variables=["product"],
                       template="How would you suggest a good name for the {product}?",)


# ----------------------------------------------------------------


user_key="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"

# side bar

with st.sidebar:
    
    with st.sidebar:
        doc_input = st.file_uploader(
            f"Upload your PDF", ["pdf"], accept_multiple_files=False
        )

    if st.button("Process"):
        with st.spinner("Processing"):

            
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(doc_input.getvalue())
                tmp_file_path = tmp_file.name
            doc = pdf_reader(tmp_file_path)
    
 

            #initializing the coverstation variable in session state
            if "conversation" not in st.session_state:
                st.session_state.conversation = None

            
            # get pdf text
            raw_text = pdf_reader(doc_input)

            # get the text chunks
            text_chunks = get_text_chunks(raw_text)
            
            
            # create vector store
            vectorstore = get_vectorstore(text_chunks,user_key)

            

            template= '''
                         We have provided context information below enclosed by double quotes.
                            
                        {context_str}
                              
                        You are an expert on reading laboratory medical results and summarizing the patients's details and should answer to the medical questions given by the users - do not hallucinate features: {query_str}
            '''
            prompt= PromptTemplate(input_variables=["context_str","query_str"],
                       template=template)

            # create conversation chain
            st.session_state.conversation = get_conversation_chain(
                vectorstore,user_key)
            
    
            
            st.write('Document processed successfully ✅')




#--------------------------------------------------------------------------------------------------------



# main page
st.title("MEDICO BOT💉🩺")

with st.chat_message("assistant"):
    st.markdown('Hi there👋 I\'m your friendly AI assistant. I can help you answer your queries by uploading your documents. Just ask me anything!')

# initializing chat history - This is to show the previous converasation of the user and LLM.
if "messages" not in st.session_state:
    st.session_state.messages = []



# Showing the previous conversation
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# handling error


# checking for prompt
if prompt :=  st.chat_input('Ask your query here...'):


    # appending the user prompt to session state
    st.session_state.messages.append({"role": "user", "content": prompt})
    # displaying the prompt 
    with st.chat_message("user"):
        st.markdown(prompt)

    # displaying the answer
    with st.chat_message("assistant"):
        # getting response from the model through chain
        response = st.session_state.conversation({'question': prompt})
        st.markdown(response['answer'])
    # adding the response from the model to session state
    st.session_state.messages.append({"role": "assistant", "content": response['answer']})


    
