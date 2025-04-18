# agents/application_designer.py

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


def create_application_designer_agent(params: dict):
    prompt_template = params.get(
        "prompt",
        "You are a software architect. Design an event-driven Java/Kafka system.",
    )
    model = params.get("model", "gpt-4")

    prompt = ChatPromptTemplate.from_messages(
        [("system", prompt_template), ("human", "{input}")]
    )

    llm = ChatOpenAI(model=model)
    return prompt | llm | StrOutputParser()


def app_designer_node(state: dict[str, str], config: dict) -> dict[str, str]:
    params = config.get("params", {})
    agent = create_application_designer_agent(params)
    output = agent.invoke({"input": state["input"]})
    return {"design": output}
