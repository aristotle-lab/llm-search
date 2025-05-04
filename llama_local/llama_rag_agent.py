# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.

from uuid import uuid4

import fire
from llama_stack_client import Agent, AgentEventLogger, LlamaStackClient, RAGDocument
from termcolor import colored


def main(disable_safety: bool = False):
    file_name = [
        'llama_local/files/Core Concept 13bffbff6dcb804da632fe98737584fc.html',
        'llama_local/files/Key Technologies 13bffbff6dcb803ba576f10cf1019bfc.html',
        'llama_local/files/Patterns 13cffbff6dcb804499f2c66ea0f44ce9.html',
        'llama_local/files/System Design Learning Delivery Format 13bffbff6dcb80a394d5e922434d03da.html'
    ]
    documents = [
        RAGDocument(
            document_id=f"num-{i}",
            content=f"{f}",
            mime_type="text/html",
            metadata={},
        )
        for i, f in enumerate(file_name)
    ]
    model_id = "meta-llama/Llama-3.2-3B-Instruct"

    client = LlamaStackClient(base_url="http://localhost:5001")
    available_models = [
        model.identifier for model in client.models.list() if model.model_type == "llm"
    ]
    if not available_models:
        print(colored("No available models. Exiting.", "red"))
        return
    if model_id not in available_models:
        available_models_str = "\n".join(available_models)
        print(
            f"Model `{model_id}` not found. Available models:\n\n{available_models_str}\n"
        )
        print(colored("Exiting.", "red"))
        return

    

    selected_vector_provider = "pgvector"

    # Create a vector database instead of memory bank
    vector_db_id = "pgvector_db"
    client.vector_dbs.register(
        vector_db_id=vector_db_id,
        embedding_model="all-MiniLM-L6-v2",
        embedding_dimension=384,
        provider_id=selected_vector_provider,
    )

    # Insert documents using the RAG tool
    client.tool_runtime.rag_tool.insert(
        documents=documents,
        vector_db_id=vector_db_id,
        chunk_size_in_tokens=512,
    )

    print(f"Using model: {model_id}")

    agent = Agent(
        client,
        model=model_id,
        instructions="You are a interview coach. Use knowledge_search tool to gather information needed to answer questions for students who are prepare system design interview. Answer succintly.",
        sampling_params={
            "strategy": {"type": "top_p", "temperature": 1.0, "top_p": 0.9},
        },
        tools=[
            {
                "name": "builtin::rag/knowledge_search",
                "args": {"vector_db_ids": [vector_db_id]},
            }
        ]
    )
    session_id = agent.create_session("test-session")
    print(f"Created session_id={session_id} for Agent({agent.agent_id})")

    user_prompts = [
        "Tell me about the system design learning delivery format",
        "What are the key technologies?",
        "What are the core concepts?",
        "What are the patterns?",
        "What are the key technologies?",
        "I am a newcomer to system design. Can you help me?",
    ]

    for prompt in user_prompts:
        response = agent.create_turn(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            session_id=session_id,
        )
        print(f"User> {prompt}")
        for log in AgentEventLogger().log(response):
            log.print()


if __name__ == "__main__":
    fire.Fire(main)