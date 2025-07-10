from typing import List
from langchain_core.tools import tool
from utils.db_connector import DBConnector
from utils.models import Endorsement

class EndorsementTool:
    def __init__(self):
        self.endorsement_tool_list = self._setup_tools()

    def _setup_tools(self) -> List:
        """Setup all tools for handling endorsement/modification requests"""

        @tool
        def register_endorsement_tool(policy_id: str, endorsement_type: str, old_value: str, new_value: str) -> str:
            """
            Registers an endorsement request for a given insurance policy. Also use this function wants to modify any details
            in their policy.

            Parameters:
                policy_id (str): The unique identifier of the policy for which the endorsement is being requested.
                endorsement_type (str): The type of endorsement (e.g., 'address change', 'nominee update', 'contact number update').
                old_value (str): The current value that will be updated (e.g., old address).
                new_value (str): The new value to be updated (e.g., new address).

            Returns:
                str: A message indicating success or failure of the endorsement registration process and returns endorsement_id if success.
            """
            if not policy_id or not endorsement_type or not old_value or not new_value:
                return "Please provide all required fields: policy_id, endorsement_type, old_value, and new_value."
            print(policy_id,endorsement_type,old_value,new_value)
            db_connector = DBConnector()
            try:
                db_connector.connect()
                endorsement_data = Endorsement(
                    policy_id=policy_id,
                    type=endorsement_type,
                    old_value=old_value,
                    new_value=new_value
                ).dict(exclude_none=True)

                query = f"""
                    INSERT INTO endorsements ({', '.join(endorsement_data.keys())})
                    VALUES ({', '.join(['%s'] * len(endorsement_data))})
                    RETURNING endorsement_id
                """
                values = tuple(endorsement_data.values())
                result = db_connector.execute_query(query, values, fetch_results=True)

                if result:
                    return f"Hello, your endorsement has been registered successfully. Your Endorsement ID is {result[0]}."
                else:
                    return "An error occurred while registering your endorsement."
            except Exception as e:
                print(e)
                return f"Unable to register endorsement request. EXCEPTION: {str(e)}"
            finally:
                db_connector.close()

        @tool
        def get_endorsement_status(endorsement_id: str) -> str:
            """Fetch the status of a submitted endorsement by ID.

            Args:
                endorsement_id (str): The ID of the endorsement to look up.

            Returns:
                str: Current status of the endorsement.
            """
            db_connector = DBConnector()
            try:
                db_connector.connect()
                query = "SELECT status FROM endorsements WHERE endorsement_id = %s"
                result = db_connector.execute_query(query, (endorsement_id,), fetch_results=True)

                if result:
                    return f"The current status of endorsement ID {endorsement_id} is '{result[0]}'."
                else:
                    return f"No endorsement found with ID: {endorsement_id}"

            except Exception as e:
                print(e)
                return f"An error occurred while fetching endorsement status for ID {endorsement_id}: {e}"
            finally:
                db_connector.close()

        return [register_endorsement_tool, get_endorsement_status]
