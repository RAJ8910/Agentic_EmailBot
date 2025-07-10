import time
from typing import Union
from utils.models import ConversationHistory
from datetime import datetime
from utils.db_connector import DBConnector

def tracking_interaction(
    output,
    input_query: str,
    customer_email: str,
    start_time_ms: float,
    status: str,
    bot_version: str = "v1.0"
    ):
    """
    Extracts relevant data from model output and constructs a ConversationHistory object.
    """
    bot_response = ""
    intent_captured = None
    if output:
        try:
            if isinstance(output, dict) and "messages" in output:
                for msg in output["messages"]:
                    if hasattr(msg, "type") and msg.type == "ai":
                        bot_response = msg.content
                    elif hasattr(msg, "type") and msg.type == "tool":
                        intent_captured = getattr(msg, "name", None)
                        print(intent_captured)

                # Fallbacks
                if not bot_response and output["messages"]:
                    bot_response = output["messages"][-1].content

                intent_captured = (
                    output.get("tool") or
                    output.get("intent") or
                    intent_captured
                )

            elif isinstance(output, str):
                bot_response = output

        except Exception as e:
            bot_response = str(output)
            status = f"parsing_error: {e}"
    
    end_time_ms= time.perf_counter()
    response_time_ms = round((end_time_ms - start_time_ms) * 1000, 2)
   
    data=ConversationHistory(
        customer_email=customer_email,
        customer_message=input_query,
        bot_response=bot_response,
        intent_captured=intent_captured,
        status=status,
        response_time_ms=response_time_ms,
        bot_version=bot_version,
        attachments_sent=None
    ).dict(exclude_none=True)

    db_connector=DBConnector()
    query = f"""
    INSERT INTO conversation_history ({', '.join(data.keys())})
    VALUES ({', '.join(['%s'] * len(data))})
    """
    values = tuple(data.values())
    db_connector.execute_query(query, values)






