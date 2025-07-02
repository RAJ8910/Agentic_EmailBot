from fastapi import FastAPI
from agent.agentic_workflow import GraphBuilder
from pydantic import BaseModel
from fastapi.responses import JSONResponse   
import os

app = FastAPI()


class QueryRequest(BaseModel):
    query: str

@app.post("/query")
async def query_email_bot(query: QueryRequest):
    try:
        print(query)
        graph= GraphBuilder(model_provider="groq")
        react_app=graph()
        png_graph = react_app.get_graph().draw_mermaid_png()
        with open("graph.png", "wb") as f:
            f.write(png_graph)
        print("Graph saved as graph.png in",os.getcwd())
        messages = {"messages": [query.query]}
        output = react_app.invoke(messages)

        if isinstance(output,dict) and "messages" in output:
            final_response = output["messages"][-1].content
        else:
            final_response = str(output)
        return {"answer": final_response}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})