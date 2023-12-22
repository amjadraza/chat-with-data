
# from langchain.llms import OpenAI
from pandasai import SmartDataframe
from pandasai.llm import OpenAI
# from pandasai.callbacks import StdoutCallback
from pandasai.llm import OpenAI
import streamlit as st
import pandas as pd
import os

from langchain.agents import AgentType
from langchain_experimental.agents.agent_toolkits.pandas.base import create_pandas_dataframe_agent
from langchain.callbacks.streamlit import StreamlitCallbackHandler
from langchain.chat_models import ChatOpenAI
# from pandasai_app.components.faq import faq

def faq():
    st.markdown(
        """
# FAQ
## What is this Application?
This application helps users interact with SPICE analytics in a conversational way.


## What sort of Data is Used?
For a demo purpose, we have created a syntehtic Data with Events, Country and Engagaments. \n
| Event | Country | Engagements | \n

## Example Questions

1. What is this Data About? 
2. What are the number of engagements related to Gitex23 and India?
3. 


"""
    )

file_formats = {
    "csv": pd.read_csv,
    "xls": pd.read_excel,
    "xlsx": pd.read_excel,
    "xlsm": pd.read_excel,
    "xlsb": pd.read_excel,
}

def clear_submit():
    """
    Clear the Submit Button State
    Returns:

    """
    st.session_state["submit"] = False


@st.cache_data(ttl="2h")
def load_data(uploaded_file):
    try:
        ext = os.path.splitext(uploaded_file.name)[1][1:].lower()
    except:
        ext = uploaded_file.split(".")[-1]
    if ext in file_formats:
        return file_formats[ext](uploaded_file)
    else:
        st.error(f"Unsupported file format: {ext}")
        return None


st.set_page_config(page_title="Chat-Data-SPICA", page_icon="🦜|🐼")
st.title("Demo SPICA| Interact with Insights About Topic")

uploaded_file = st.file_uploader(
    "Upload a Data file With Topic & Engagaments",
    type=list(file_formats.keys()),
    help="Various File formats are Support",
    on_change=clear_submit,
)

if uploaded_file:
    df = load_data(uploaded_file)

# openai_api_key = st.sidebar.text_input("OpenAI API Key",
#                                         type="password",
#                                         placeholder="Paste your OpenAI API key here (sk-...)")

openai_api_key = "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"


chat_data = st.sidebar.selectbox("Choose a Backend", ['langchain', 'pandasai'])

with st.sidebar:
#         st.markdown("---")
#         st.markdown(
#             "## How to use\n"
#             "1. Enter your [OpenAI API key](https://platform.openai.com/account/api-keys) below🔑\n"  # noqa: E501
#             "2. Choose Backend PandasAI or LangChain\n"
#             "3. Upload a csv file with data📄\n"
#             "4. A csv file is read as Pandas Dataframe📄\n"
#             "5. Ask a question about to make dataframe conversational💬\n"
#         )

#         st.markdown("---")
#         st.markdown("# About")
#         st.markdown(
#             "📖Pandasai App allows you to ask questions about your "
#             "csv / dataframe and get accurate answers"
#         )
#         st.markdown(
#             "Pandasai is in active development so is this tool."
#             "You can contribute to the project on [GitHub]() "  # noqa: E501
#             "with your feedback and suggestions💡"
#         )
#         st.markdown("Made by [DR. AMJAD RAZA](https://www.linkedin.com/in/amjadraza/)")
#         st.markdown("---")

        faq()

if "messages" not in st.session_state or st.sidebar.button("Clear conversation history"):
    st.session_state["messages"] = [{"role": "assistant", "content": "Welcome to Spice Analytics, Ask me?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(placeholder="What is this data about?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()
    if chat_data == "pandasai":
        #PandasAI OpenAI Model
        llm = OpenAI(api_token=openai_api_key)
        # llm = OpenAI(api_token=openai_api_key)

        sdf = SmartDataframe(df, config = {"llm": llm,
                                            "enable_cache": False,
                                            "conversational": True,
                                            "verbose": True})

        with st.chat_message("assistant"):
            response = sdf.chat(st.session_state.messages)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.write(response)
    
    if chat_data == "langchain":

        llm = ChatOpenAI(
            temperature=0, model="gpt-3.5-turbo-0613", openai_api_key=openai_api_key, streaming=True
        )

        pandas_df_agent = create_pandas_dataframe_agent(
            llm,
            df,
            verbose=True,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            handle_parsing_errors=True,
        )

        with st.chat_message("assistant"):
            st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
            response = pandas_df_agent.run(st.session_state.messages, callbacks=[st_cb])
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.write(response)
