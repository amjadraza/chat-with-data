
# from langchain.llms import OpenAI
from pandasai import SmartDataframe
from pandasai.llm import OpenAI
from pandasai.callbacks import StdoutCallback
from pandasai.llm import OpenAI
import streamlit as st
import pandas as pd
import os
# from pandasai_app.components.faq import faq

def faq():
    st.markdown(
        """
# FAQ
## How does Pandasai App work?
When you upload a cleaned CSV, it is converted into pandas dataframe. 
Using OpenAI API, A python code is generated and run as per submitted query or 
prompt.


## Is my data safe?
Yes, your data is safe. Pandasai APp does not store your documents or
questions or API Key. All uploaded data is deleted after you close the browser tab.

## What are the costs associated to using Openai API?
Yes, there is cost associated when using Openai API. Please read the Pricing when signing up.

## Does this App Supports Plots?
This is Work In Progress.Yes, Plots will be supported in future.

## Are the answers 100% accurate?
No, the answers are not 100% accurate. Pandasai App uses the Openai API which tries to match answers close to 100%.
As you are aware, this is still work in progress.

## Support of Other APIs e.g Azure, HuggingFace, Dolly or Bard?
This tool will be expanded to allow use of other LLMs API providers.

## Support of Other APIs e.g Azure, HuggingFace, Dolly or Bard?
This tool will be expanded to allow use of other LLMs API providers.

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


st.set_page_config(page_title="PandasAI ", page_icon="🐼")
st.title("🐼 PandasAI: Chat with CSV")

uploaded_file = st.file_uploader(
    "Upload a Data file",
    type=list(file_formats.keys()),
    help="Various File formats are Support",
    on_change=clear_submit,
)

if uploaded_file:
    df = load_data(uploaded_file)

openai_api_key = st.sidebar.text_input("OpenAI API Key",
                                        type="password",
                                        placeholder="Paste your OpenAI API key here (sk-...)")

with st.sidebar:
        st.markdown("---")
        st.markdown(
            "## How to use\n"
            "1. Enter your [OpenAI API key](https://platform.openai.com/account/api-keys) below🔑\n"  # noqa: E501
            "2. Upload a csv file with data📄\n"
            "3. A csv file is read as Pandas Dataframe📄\n"
            "4. Ask a question about to make dataframe conversational💬\n"
        )

        st.markdown("---")
        st.markdown("# About")
        st.markdown(
            "📖Pandasai App allows you to ask questions about your "
            "csv / dataframe and get accurate answers"
        )
        st.markdown(
            "Pandasai is in active development so is this tool."
            "You can contribute to the project on [GitHub]() "  # noqa: E501
            "with your feedback and suggestions💡"
        )
        st.markdown("Made by [DR. AMJAD RAZA](https://www.linkedin.com/in/amjadraza/)")
        st.markdown("---")

        faq()

if "messages" not in st.session_state or st.sidebar.button("Clear conversation history"):
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(placeholder="What is this data about?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    #PandasAI OpenAI Model
    llm = OpenAI(api_token=openai_api_key)
    # llm = OpenAI(api_token=openai_api_key)

    sdf = SmartDataframe(df, config = {"llm": llm,
                                        "enable_cache": False,
                                        "conversational": True,
                                        "callback": StdoutCallback()})

    with st.chat_message("assistant"):
        response = sdf.chat(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.write(response)
