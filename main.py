from fastapi import FastAPI
from agent.agentic_workflow import GraphBuilder
from pydantic import BaseModel
from fastapi.responses import JSONResponse   
import time
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
from utils.tracking_interaction import tracking_interaction
from utils.db_connector import DBConnector
app = FastAPI()


class QueryRequest(BaseModel):
    query: str

@app.post("/query")
async def query_email_bot(query: QueryRequest):
    try:
        start_time = time.perf_counter()
        print(query)
        graph= GraphBuilder(model_provider="groq")
        react_app=graph()
        png_graph = react_app.get_graph().draw_mermaid_png()
        with open("graph.png", "wb") as f:
            f.write(png_graph)
        # print("Graph saved as graph.png in",os.getcwd())
        messages = {"messages": [query.query]}
        output = react_app.invoke(messages)
        if isinstance(output,dict) and "messages" in output:
            final_response = output["messages"][-1].content
        else:
            final_response = str(output)
        
        tracking_interaction(
            output=output,
            input_query=query.query,
            customer_email="test@test.com",
            start_time_ms=start_time, 
            status="success"
        )
        return {"answer": final_response}
    except Exception as e:
        tracking_interaction(
            input_query=query.query,
            customer_email="test@test.com",
            start_time_ms=start_time,
            end_time_ms=end_time,
            status=f"failure :{e}"
        )
        return JSONResponse(status_code=500, content={"error": str(e)})
    

@app.get("/tracking")
async def get_tracking_table():
    try:
        db = DBConnector()
        rows = db.execute_query("SELECT * FROM conversation_history", fetch_results=True)
        if not rows:
            return {"data": []}
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM conversation_history LIMIT 1")
        columns = [desc[0] for desc in cursor.description]
        cursor.close()
        data = [dict(zip(columns, row)) for row in rows]
        return {"data": data}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
