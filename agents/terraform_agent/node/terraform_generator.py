# agents/terraform_generator.py

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


def create_terraform_agent(params: dict):
    prompt_template = params.get(
        "prompt", "You are a cloud infrastructure expert. Generate Terraform scripts."
    )
    model = params.get("model", "gpt-4")

    prompt = ChatPromptTemplate.from_messages(
        [("system", prompt_template), ("human", "{input}")]
    )

    llm = ChatOpenAI(model=model)
    return prompt | llm | StrOutputParser()


def terraform_node(state: dict[str, str], config: dict) -> dict[str, str]:
    params = config.get("params", {})
    input_text = state.get("design", "")
    agent = create_terraform_agent(params)
    output = agent.invoke({"input": input_text})
    return {"terraform": output}
