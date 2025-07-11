
from utils.model_loader import ModelLoader
from prompt_library.prompt import SYSTEM_PROMPT
from langgraph.graph import StateGraph, MessagesState, END, START
from langgraph.prebuilt import ToolNode, tools_condition
from tools.weather_info_tool import WeatherInfoTool
from tools.policy_copy_tool import PolicyCopyTool
from tools.claim_status_tool import ClaimStatusTool
from tools.rag_tool import get_rag_tool
from tools.endorsement_tool import EndorsementTool

class GraphBuilder():
    def __init__(self,model_provider: str = "groq"):
        self.model_loader = ModelLoader(model_provider=model_provider)
        self.llm = self.model_loader.load_llm()
        
        self.tools = []
       
        self.weather_info_tool = WeatherInfoTool()
        self.claim_status_tool = ClaimStatusTool()
        self.endorsement_tool = EndorsementTool()
        self.tools.extend([
              * self.weather_info_tool.weather_tool_list,
              PolicyCopyTool,
              * self.claim_status_tool.claim_status_tool_list,
              * self.endorsement_tool.endorsement_tool_list
              ])
        
        self.llm_with_tools = self.llm.bind_tools(tools=self.tools)
        rag_tool = get_rag_tool(self.llm)
        self.tools.append(rag_tool)
        self.llm_with_tools = self.llm.bind_tools(tools=self.tools)
        self.graph = None
        
        self.system_prompt = SYSTEM_PROMPT
    
    
    def agent_function(self,state: MessagesState):
        """Main agent function"""
        user_question = state["messages"]
        input_question = [self.system_prompt] + user_question
        response = self.llm_with_tools.invoke(input_question)
        return {"messages": [response]}
    def build_graph(self):
        graph_builder=StateGraph(MessagesState)
        graph_builder.add_node("agent", self.agent_function)
        graph_builder.add_node("tools", ToolNode(tools=self.tools))
        graph_builder.add_edge(START,"agent")
        graph_builder.add_conditional_edges("agent",tools_condition)
        graph_builder.add_edge("tools","agent")
        graph_builder.add_edge("agent",END)
        self.graph = graph_builder.compile()
        return self.graph
        
    def __call__(self):
        return self.build_graph()