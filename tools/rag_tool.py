import os
from langchain_huggingface import HuggingFaceEmbeddings
# Changed: Import FAISS
from langchain_community.vectorstores import FAISS 
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.tools import tool 
from prompt_library.prompt import RAG_SYSTEM_PROMPT



def get_rag_tool(
    llm,
    pdf_directory: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../docs")),
    faiss_index_path: str = "faiss_index_hf_directory", # Directory to save/load FAISS index
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    chunk_size: int = 1000, # Kept reasonable for 8GB RAM
    chunk_overlap: int = 200
):
    """
    Creates and returns a RAG tool using FAISS for document retrieval.

    Args:
        llm: The Language Model (e.g., ChatGroq instance).
        pdf_directory (str): The path to the directory containing PDF documents.
        faiss_index_path (str): The path where the FAISS index will be saved/loaded.
        model_name (str): The name of the Hugging Face embedding model to use.
        chunk_size (int): The size of text chunks for embedding.
        chunk_overlap (int): The overlap between text chunks.
    """

    embeddings = HuggingFaceEmbeddings(model_name=model_name, model_kwargs={'device': 'cpu'})

    # --- Load or Create FAISS Index ---
    if os.path.exists(faiss_index_path) and os.path.exists(os.path.join(faiss_index_path, "index.faiss")):
        print(f"Loading existing FAISS index from {faiss_index_path}...")
        # allow_dangerous_deserialization=True is needed for loading from disk
        vector_store = FAISS.load_local(faiss_index_path, embeddings, allow_dangerous_deserialization=True)
        print("FAISS index loaded.")
    else:
        print(f"FAISS index not found. Loading documents from {pdf_directory} and creating new index...")
        
        if not os.path.exists(pdf_directory):
            raise FileNotFoundError(f"The specified PDF directory does not exist: {pdf_directory}")

        loader = PyPDFDirectoryLoader(path=pdf_directory, glob="**/*.pdf", recursive=True)
        documents = loader.load()

        if not documents:
            print(f"No PDF documents found in {pdf_directory}. Please check the path and content.")
            return None # Or raise an error if you prefer

        print(f"Loaded {len(documents)} raw documents (pages).")
        
        print(f"Splitting documents into chunks (Chunk Size: {chunk_size}, Overlap: {chunk_overlap})...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        chunks = text_splitter.split_documents(documents)
        print(f"Created {len(chunks)} chunks from all documents.")

        print(f"Generating embeddings and creating FAISS vector store using {model_name}...")
        vector_store = FAISS.from_documents(chunks, embeddings)
        print("FAISS vector store created.")

        vector_store.save_local(faiss_index_path)
        print(f"FAISS index saved to {faiss_index_path}")

    retriever = vector_store.as_retriever()
    document_chain = create_stuff_documents_chain(llm, RAG_SYSTEM_PROMPT)
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    @tool
    def rag_tool(query: str) -> str:
        """Use this tool when the customer is asking about policy information such as terms and conditions,
        coverage details, policy benefits, or is interested in understanding or buying other insurance products.
        Do NOT use this tool to send personal details of the customer regarding the policy — use the policy copy tool for that.
        This tool explains policy-related queries based on company documents and FAQs."""
        print(f"Invoking rag_tool with query: {query}") # Added for debugging/tracing
        result = retrieval_chain.invoke({"input": query})
        
        # It's good practice to also return sources, though the tool's signature is `-> str`
        # For a tool, you typically want just the answer.
        # If you needed sources, the tool signature would be `-> dict` or a custom Pydantic model.
        # For now, we'll stick to string and just print sources internally if needed for debugging.
        # print("\n--- Sources from RAG Tool ---")
        # if "context" in result:
        #     for doc in result["context"]:
        #         print(f"- {doc.metadata.get('source', 'N/A')} (Page: {doc.metadata.get('page', 'N/A')})")
        # print("----------------------------")
        answer = result["answer"]
    # Remove special markers if present
        if "<｜tool▁outputs▁end｜>" in answer:
            answer = answer.split("<｜tool▁outputs▁end｜>")[0].strip()
        return answer

    return rag_tool

