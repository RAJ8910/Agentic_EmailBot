from typing import List
from utils.db_connector import DBConnector
from langchain.tools import tool
from utils.models import Policy,convert_db_row_to_model

@tool
def PolicyCopyTool(customer_id: str) -> List[Policy] | str:
    """Fetches and returns the policy details for a given customer.

    Args:
        customer_id: The unique identifier (string) of the customer.

    Returns:
        A Customer model containing the customer's details and their associated
        policy information if found, otherwise a descriptive string indicating
        that no policy was found for the given customer ID.
    """
    db_connector=DBConnector()
    db_connector.connect()
    
    query = f"select * from policies where customer_id = '{customer_id}'"
    try:
        result = db_connector.execute_query(query, fetch_results=True)
        db_connector.close()
        if result:
            return [convert_db_row_to_model(row, Policy) for row in result]
        else:
            return f"No policy found for customer_id: {customer_id}"
    except Exception as e:
        print(f"Error fetching policy for customer {customer_id}: {e}")
        db_connector.close()
        return f"An error occurred while fetching policy for customer_id: {customer_id}"
