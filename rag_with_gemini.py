from pathlib import Path
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore  # Fixed import
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


load_dotenv()


os.environ["GOOGLE_API_KEY"] = os.getenv("API_KEY", "")

def setup_rag_pipeline():
    """Initialize the RAG pipeline components"""
    
  
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    client = QdrantClient(url="http://localhost:6333")
    
 
    vector_store = QdrantVectorStore(
        client=client,
        collection_name="learning_langchain",
        embedding=embeddings
    )
    
 
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})  # Retrieve top 3 documents
    
    # 5. Initialize Gemini LLM
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)
    
    # 6. Create prompt template
    template = """You are an AI assistant specialized in providing accurate and helpful responses about mental health.
    
Context: {context}

User Question: {question}

Instructions:
1. Use the provided context to give comprehensive advice on managing stress and mental health
2. Be empathetic and supportive in your response
3. Provide practical tips and techniques that can help
4. If the context doesn't have enough specific information, provide general evidence-based advice
5. keep your response concise and to the point and make it user friendly 
6. give the response in casual and friendly tone as if a friend or mentor is talking to the user
Answer:"""

    prompt = ChatPromptTemplate.from_template(template)
    
    # 7. Create the RAG chain
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return vector_store, retriever, rag_chain

def scrape_article(url):
    """Scrape article content from a URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        article_text = soup.get_text()
        
        # Clean up the text
        lines = (line.strip() for line in article_text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return None

def load_urls(urls):
    """Load documents from multiple URLs"""
    all_docs = []
    
    for url in urls:
        print(f"Loading {url}...")
        
        if url.endswith('.pdf'):
            # For PDF URLs, use the PDF loader
            from langchain_community.document_loaders import PyPDFLoader
            loader = PyPDFLoader(url)
            docs = loader.load()
        else:
            # For web pages, use scraped content
            content = scrape_article(url)
            if content:
                # Create a document object manually
                from langchain_core.documents import Document
                domain = urlparse(url).netloc
                doc = Document(
                    page_content=content,
                    metadata={"source": url, "domain": domain, "type": "web"}
                )
                docs = [doc]
            else:
                continue
        
        all_docs.extend(docs)
    
    return all_docs

def inject_documents(urls):
    """Load and inject web documents into Qdrant"""
    # Load documents from URLs
    docs = load_urls(urls)
    
    if not docs:
        print("No documents loaded!")
        return
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    split_docs = text_splitter.split_documents(documents=docs)
    
    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Create vector store using QdrantVectorStore
    vector_store = QdrantVectorStore.from_documents(
        documents=split_docs,
        embedding=embeddings,
        url="http://localhost:6333",
        collection_name="mental_health_articles"  # New collection name
    )
    
    print(f"✅ Successfully injected {len(split_docs)} document chunks from {len(urls)} sources")

def add_new_url(url, vector_store):
    """Add a new URL to the existing vector store"""
    docs = load_urls([url])
    
    if not docs:
        print(f"Failed to load {url}")
        return
    
    # Split document into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    split_docs = text_splitter.split_documents(documents=docs)
    
    # Add to existing vector store
    vector_store.add_documents(split_docs)
    
    print(f"✅ Successfully added {len(split_docs)} chunks from {url}")

def generate_response(query: str, retriever, rag_chain):
    """Generate response for a user query"""
    
    # 1. Retrieve relevant documents
    relevant_docs = retriever.invoke(query)
    
    print(f"\n🔍 Found {len(relevant_docs)} relevant documents")
    for i, doc in enumerate(relevant_docs):
        print(f"{i+1}. {doc.page_content[:100]}...\n")
    
    # 2. Generate response using RAG chain
    response = rag_chain.invoke(query)
    
    return response, relevant_docs

def main():
    # First, inject the mental health articles
    urls = [
        "https://medlineplus.gov/howtoimprovementalhealth.html",
        "https://www.mentalhealth.org.uk/explore-mental-health/publications/our-best-mental-health-tips",  # Adding an extra NIMH article
    ]
    
    # Inject documents if not already done
    try:
        # Use a new collection name to avoid mixing with your problem statements
        client = QdrantClient(url="http://localhost:6333")
        collection_exists = client.collection_exists("mental_health_articles")
        
        if not collection_exists:
            print("Creating new collection with mental health articles...")
            inject_documents(urls)
    except Exception as e:
        print(f"Warning: Could not check/create collection: {e}")
    
    # Initialize the RAG pipeline with the proper collection
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    client = QdrantClient(url="http://localhost:6333")
    
    vector_store = QdrantVectorStore(
        client=client,
        collection_name="mental_health_articles",  # Use the new collection
        embedding=embeddings
    )
    
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    
    # Initialize Gemini LLM
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)
    
    # Create prompt template
    template = """You are an AI assistant specialized in providing accurate and helpful responses about mental health.
    
Context: {context}

User Question: {question}

Instructions:
1. Use the provided context to give comprehensive advice on managing stress and mental health
2. Be empathetic and supportive in your response
3. Provide practical tips and techniques that can help
4. If the context doesn't have enough specific information, provide general evidence-based advice
5. Complete your response - don't cut it off midway

Answer:"""

    prompt = ChatPromptTemplate.from_template(template)
    
    # Create the RAG chain
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    # Interactive CLI
    print("🤖 AI Assistant ready! Commands:")
    print("  - Type your question")
    print("  - Type 'add <url>' to add a new article/website")
    print("  - Type 'exit' to quit\n")
    
    while True:
        user_input = input("👤 You: ").strip()
        
        if user_input.lower() == 'exit':
            print("👋 Goodbye!")
            break
        
        if not user_input:
            continue
        
        try:
            if user_input.lower().startswith('add '):
                url = user_input[4:].strip()
                add_new_url(url, vector_store)
            else:
                response, docs = generate_response(user_input, retriever, rag_chain)
                print(f"\n🤖 Assistant: {response}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()