from llama_index.retrievers import PathwayRetriever
from llama_index.query_engine import RetrieverQueryEngine
from llama_index.chat_engine.condense_question import CondenseQuestionChatEngine
from rag import chat_engine


PATHWAY_HOST = "api-pathway-indexer.staging.deploys.pathway.com"
PATHWAY_PORT = 80

retriever = PathwayRetriever(host=PATHWAY_HOST, port=PATHWAY_PORT)


chat_engine = CondensePlusContextChatEngine.from_defaults(
    retriever=retriever,
    verbose=True,
)

st.title("Pathway + LlamaIndex")

if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi, ask me a question. My knowledge is always up to date!"}
    ]

    st.session_state.chat_engine = chat_engine

if prompt := st.chat_input("Your question"):
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])



if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.chat_engine.chat(prompt)
            st.write(response.response)
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message)