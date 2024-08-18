import streamlit as st
from langchain_groq import ChatGroq
from langchain.chains import LLMMathChain, LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.agents.agent_types import AgentType
from langchain.agents import Tool, initialize_agent
from langchain.callbacks import StreamlitCallbackHandler

## Set up the Streamlit app
st.set_page_config(
    page_title="AI Math & Knowledge Assistant", 
    page_icon="🧮", 
    layout="wide"
)

# Sidebar Configuration
with st.sidebar:
    st.title("AI Assistant")
    st.markdown("### Settings")
    groq_api_key = st.text_input(label="Groq API Key", type="password")
    st.markdown("---")

if not groq_api_key:
    st.info("Please add your Groq API key to continue")
    st.stop()

llm = ChatGroq(model="Gemma2-9b-It", groq_api_key=groq_api_key)

## Initialize Tools
wikipedia_wrapper = WikipediaAPIWrapper()
wikipedia_tool = Tool(
    name="Wikipedia",
    func=wikipedia_wrapper.run,
    description="Search the Internet for relevant information."
)

math_chain = LLMMathChain.from_llm(llm=llm)
calculator = Tool(
    name="Calculator",
    func=math_chain.run,
    description="Answer math-related questions."
)

prompt = """
You are an agent tasked with solving users' mathematical questions. Provide a clear and logical step-by-step explanation.
Question: {question}
Answer:
"""

prompt_template = PromptTemplate(
    input_variables=["question"],
    template=prompt
)

chain = LLMChain(llm=llm, prompt=prompt_template)

reasoning_tool = Tool(
    name="Reasoning Tool",
    func=chain.run,
    description="Answer logic-based and reasoning questions."
)

assistant_agent = initialize_agent(
    tools=[wikipedia_tool, calculator, reasoning_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=False,
    handle_parsing_errors=True
)

# Session State Management
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "👋 Hi! I'm your AI assistant for math and knowledge-based queries. How can I help you today?"}
    ]

# Display Chat Messages
st.markdown("## 💬MathGPT")
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# User Input Section
st.markdown("---")
st.markdown("### Ask a Question")
question = st.text_area("Enter your question here:", placeholder="Type your question...")

col1, col2 = st.columns([3, 1])
with col1:
    if st.button("Find My Answer"):
        if question:
            with st.spinner("Thinking..."):
                st.session_state.messages.append({"role": "user", "content": question})
                st.chat_message("user").write(question)

                st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
                response = assistant_agent.run(st.session_state.messages, callbacks=[st_cb])
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.write("### Response:")
                st.success(response)
        else:
            st.warning("Please enter a question.")

with col2:
    st.markdown(" ")
    st.image("https://example.com/assistant-logo.png", use_column_width=True)  # Optional branding

# Footer
st.markdown("---")
st.markdown("### Powered by Streamlit and LangChain")
st.markdown("Designed for math enthusiasts and learners.")





c
