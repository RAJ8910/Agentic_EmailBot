from typing import List
from utils.db_connector import DBConnector
from langchain.tools import tool

class ClaimStatusTool:
    def __init__(self):
        self.claim_status_tool_list = self._setup_tools()

    def _setup_tools(self) -> List:
        """Setup all tools for the claim status tool"""
        
        @tool
        def get_claim_status(claim_id: str) -> str:
            """Get the status of a claim by its ID"""
            print(f"Fetching claim status for claim_id: {claim_id}")
            db_connector = DBConnector()
            db_connector.connect()
            
            query = f"SELECT status FROM claims WHERE claim_id = '{claim_id}'"
            try:
                result = db_connector.execute_query(query, fetch_results=True)
                db_connector.close()
                print(result)
                if result:
                    return f"Claim ID {claim_id} status: {result}"
                else:
                    return f"No claim found with ID: {claim_id}"
            except Exception as e:
                db_connector.close()
                return f"An error occurred while fetching claim status for ID {claim_id}: {e}"
            
        @tool
        def register_claims_tool(policy_id,amount_requested,reason) -> str:
            """Register the claim status tool for a given policy ID, amount requested, and reason given by the 
            customer"""
            print(f"Registering claim for policy_id: {policy_id}, amount_requested: {amount_requested}, reason: {reason}")
            if not policy_id or not amount_requested or not reason:
                return "Please provide all required fields: policy_id, amount_requested, and reason."
            
            db_connector = DBConnector()
            db_connector.connect()
            # Check if the policy exists
            query = f"SELECT policy_id,claim_id FROM claims WHERE policy_id = '{policy_id}'"
            result1 = db_connector.execute_query(query, fetch_results=True)
            db_connector.close()
            if result1:
                # print(f"Claim already exists for policy_id: {policy_id}, claim_id: {result1[1]}")
                return f"Claim already exists for policy_id: {policy_id}, claim_id: {result1[1]}"
            claim_data = {
            'policy_id': policy_id,
            'customer_id': 1,
            'claim_type': 'Accident',
            'claim_amount_requested': amount_requested,
            'claim_amount_approved': 0.0,
            'status': 'under review',
            'reason': reason,
            'remarks': ''
            }
            query = f"""
            INSERT INTO claims ({', '.join(claim_data.keys())})
            VALUES ({', '.join(['%s'] * len(claim_data))})
            RETURNING claim_id
            """
          
            values = tuple(claim_data.values())
            result=db_connector.execute_query(query, values,fetch_results=True)
            db_connector.close()
            print(f"Claim registration result: {result}")
            if result:
                return f"Hello, your claim has been registered successfully. Your Claim ID is {result[0]}." 
            else: 
                db_connector.close()
            return "An error occurred while registering your claim."
        
        return [get_claim_status,register_claims_tool]