# Research and Projects Overview
[Access contribution history from this Google Doc](https://docs.google.com/document/d/18kg9A_ETLTsL98QjafQc6otS9yGOVAQnd6OsH7GAjbQ/edit?usp=sharing)

## 1. **Build Your First LLM Chatbot - Alisha Saboowala**  
   **Key Concepts:**
   - **Fine-tuning**: Re-training pre-trained LLM with new data to optimize for tasks like sentiment analysis and predictions.  
   - **Context Injection**: Adding relevant context into the prompt instead of altering the LLM.  
   - **Vector Databases**: Storing large amounts of vector data for searching and retrieval based on similarity.  
   - **LangChain's RetrievalQA**: Enables optimized Q&A for documents by retrieving the closest vectors to the query and providing context to the LLM.  
   [Read the full article here](https://medium.com/@alisha3/build-your-first-llm-chatbot-77456438f57b)

## 2. **Build Your Own AI Chatbot: A Beginner’s Guide to RAG and LangChain - Suraj Bansal**  
   **Key Concepts:**
   - **RAG (Retrieval-Augmented Generation)**: Combines LLM with external knowledge retrieval for more accurate responses.  
   - **Chunking and Overlap**: Splitting documents into smaller parts for memory efficiency and preserving context.  
   - **Stateful Chatbot**: Stores interaction history for natural conversation flow and context.  
   - **ConversationalRetrievalChain**: Builds effective question-answering applications by retrieving and processing documents in LangChain.  
   [Read the full article here](https://medium.com/@suraj_bansal/build-your-own-ai-chatbot-a-beginners-guide-to-rag-and-langchain-0189a18ec401)

## 3. **Building Effective Agents - Anthropic**  
   **Key Concepts:**
   - **Workflows**: Predetermined paths for LLMs to accomplish tasks efficiently with consistency.  
   - **Agents**: Dynamic LLM systems that use external tools and maintain control over their process, useful for complex tasks.  
   - **Prompt Chaining**: Decomposes tasks into smaller steps for improved accuracy.  
   - **Orchestrator-Workers**: Central LLM breaks tasks into subtasks, synthesizing results from worker LLMs.  
   [Read the full paper here](https://www.anthropic.com/research/building-effective-agents)

## 4. **LLM Pricing Comparison - Medium**  
   **Key Insights:**
   - Pricing varies across providers (OpenAI, Azure, Anthropic, AWS, Google), with different models offering varying context sizes and rates.  
   - Considerations include input/output tokens and model specifications based on application needs.  
   [Read the full article here](https://medium.com/@Experto_AI/llm-apis-price-comparison-by-model-66d1c7bd259d)

## 5. **Retrieval-Augmented Generation (RAG) - AWS**  
   **Key Insights:**
   - **RAG** enhances LLM performance by retrieving external knowledge during query response.  
   - **Benefits**: Improves response relevance, reduces retraining costs, and supports real-time updates without the need to retrain models.  
   - **Use Cases**: Legal, healthcare, and customer service applications where up-to-date or specialized information is needed.  
   [Read the full article here](https://aws.amazon.com/what-is/retrieval-augmented-generation/)

## 6. **ChromaDB for Vector Storage and Retrieval**  
   **Key Concepts:**
   - **ChromaDB**: A powerful vector database used for storing and retrieving vectorized data, ideal for AI models requiring similarity-based search and retrieval.  
   - **Vectorization**: Transforms text into numerical representations (embeddings) that preserve semantic meaning, enabling efficient similarity searches.  
   - **Cosine Similarity**: A method to compare vectors by calculating the cosine of the angle between them, used to measure similarity between text data.  
   - **Retrieval Workflow**: ChromaDB stores vectorized data (e.g., from PDFs) and retrieves relevant documents based on similarity to a given query.  
   - **Offline Capabilities**: Once downloaded, ChromaDB enables offline retrieval, ensuring functionality in environments without internet access.  
   [Explore ChromaDB Documentation](https://www.trychroma.com/docs)

## 7. **How to Build a RAG System Using DeepSeek R1**  
   **Overview of DeepSeek R1**:  
   - **DeepSeek R1**: An open-source AI model designed for high-quality reasoning and knowledge retrieval. It provides advanced reasoning capabilities, analyzes information step by step, and can handle complex queries better than other models.  
   - **Cost-Effective**: DeepSeek R1 offers a fraction of the cost of proprietary models like OpenAI’s offerings, making it a competitive choice for building efficient RAG systems.  
   - **Customizable**: The model is open-source and can be fine-tuned, integrated into various applications, and customized to suit specific needs.  
   - **Benchmarking**: DeepSeek R1 is on par or better than OpenAI’s models for reasoning tasks, providing reliable performance for RAG workflows.  
   - **Transparency**: DeepSeek R1 uses a chain of thought methodology that makes reasoning steps visible, aiding debugging and system refinement.  
   - **Offline Capability**: Once downloaded, DeepSeek R1 can function offline, making it a strong choice for environments with limited or no internet access.  
   
   **Steps to Build a RAG System Using DeepSeek R1**:  
   - **Dependencies**: Install necessary dependencies such as `langchain`, `langchain-openai`, `langchain-community`, and `langchain-chroma`.  
   - **Process PDF**: Load and split PDF documents, converting them into text for storage.  
   - **Vector Database**: Store the vectorized text data in ChromaDB.  
   - **Similarity Search**: Use cosine similarity to retrieve relevant documents based on a user’s query.  
   - **Response Generation**: DeepSeek R1 generates responses by processing retrieved documents, ensuring high-quality, accurate answers.  
   - **Model Configuration**: Configure the model using LangChain’s Retrieval module, which connects to DeepSeek and formats the query results for concise and structured responses.  
   
   **Steps for Building the RAG Pipeline**:  
   - **Text Retrieval**: Fetch relevant documents from ChromaDB based on query similarity.  
   - **Model Response**: Use a structured prompt template to instruct DeepSeek R1 in generating a detailed response.  
   - **Chain Testing**: Ensure that the LLM generates fact-based responses strictly from the retrieved context.  
   
   [Read More About DeepSeek R1]([https://www.deepsseek.com/](https://www.analyticsvidhya.com/blog/2025/01/rag-system-using-deepseek/))

## 8. **Building Agentic RAG with DeepSeek R1 and Qwen**  
   **Overview of Qwen 2.5**:  
   - **Qwen 2.5**: A pre-trained AI model that supports up to 128K tokens and offers multilingual capabilities. It is built on Alibaba’s extensive dataset of up to 18 trillion tokens, making it highly versatile for future language expansion.  
   - **Primary Agent**: Qwen 2.5 acts as the primary interface, processing user queries and deciding when to answer directly or when to use RAG for complex questions.  
   - **Gradio UI**: A user-friendly interface for interacting with the primary agent, simplifying the user experience.  
   
   **Key Enhancements for RAG Systems**:
   - **Fallback Logic**: Implements a web search trigger when the confidence level of DeepSeek R1 is low, improving system reliability.  
   - **Multi-Hop Queries**: Supports iterative querying, refining responses through multiple steps to ensure the highest quality output.  
   - **LangGraph Integration**: Allows the creation of complex workflows, including state management and sequential task processing.  
   - **Faiss Integration**: Utilizes Faiss for faster retrieval in large datasets, improving overall system speed.  
   - **Batch Processing**: Optimizes embedding generation by batching text chunks, reducing processing time.  

   **Steps to Build the Agentic RAG System**:
   1. **Install Dependencies**: Set up libraries like `LangChain` and integrate Qwen 2.5 with the model’s environment.  
   2. **Configure RAG System**: Establish a workflow where DeepSeek R1 handles reasoning and document retrieval, and Qwen 2.5 serves as the querying agent.  
   3. **Integrate User Interface**: Build a Gradio-based UI for simple interactions with the chatbot agent.  
   4. **Run the Agent**: Deploy the agent and test its performance with real queries.  

   [Explore the Agentic RAG GitHub Repository](https://github.com/deepujain/agentic-rag-deepseek-qwen)\
   [DeepSeek R1 RAG Chatbot With Chroma, Ollama, and Gradio](https://www.datacamp.com/tutorial/deepseek-r1-rag)\
   [Zero to RAG: A quick OpenSearch vector database and DeepSeek integration guide](https://opensearch.org/blog/deepseek-integration-rag/)

## 9. **Legal Chatbot Considerations**  
   - **Concerns**: Legal chatbots, like Roxanne (housing-related in NYC), must ensure transparency, privacy, and avoid providing legal advice directly.  
   - **Challenges**: Updating legal data regularly and addressing ambiguity in liability.  
   - **Best Practices**: Inform clients that AI guidance is not legal advice, ensure informed consent, and integrate human oversight for sensitive matters.  
   [Read more about Roxanne here](https://www.thomsonreuters.com/en-us/posts/ai-in-courts/housing-repairs-chatbot/)

## 10. **Research Paper: "Intention and Context Elicitation with LLMs in Legal Aid"**  
   **Key Insights:**
   - This study focuses on enhancing legal intake with LLMs by improving intent and context recognition.  
   - **Application**: Implementing this approach can improve chatbot accuracy in understanding legal contexts and handling multi-turn dialogues.  
   - **Evaluation**: Key metrics like precision, recall, and F1-score are essential for assessing chatbot reliability.  
   [Read the full paper here](https://paperswithcode.com/paper/intention-and-context-elicitation-with-large)

## 11. **Existing Project: LawGPT**  
   **Key Insights:**
   - A reference project on LLMs in the legal domain. Though not directly aligned with our needs, it offers insights into the challenges and solutions for hosting and implementing legal guidance systems using LLMs.  
   [View the project on GitHub](https://github.com/harshitv804/LawGPT)

## 12. **BU Spark ML Chatbot Project Roadmap**  
   **Project Steps:**
   - **Data Scraping & Storage**: Collect data and structure it for retrieval.  
   - **Technologies**: LangChain for orchestrating workflows, Faiss for vector databases.  
   - **Data Chunking & Vectorization**: Split and store data in a Faiss database.  
   - **Response Generation**: Use OpenAI APIs for converting raw data into structured chatbot responses.  
   - **User Interface**: Build UI with tools like Streamlit or Gradio, and deploy via Hugging Face.

## 13. **Additional Resources and Tutorials**  
   - LangChain tutorials and DeepLearning.ai’s LangChain short course for LLM development.  
   [LangChain Documentation](https://python.langchain.com/docs/tutorials/rag/)  
   [LangChain for LLM Application Development](https://www.deeplearning.ai/short-courses/langchain-for-llm-application-development/)

## 14. **Legal Chatbots in Housing**  
   - Examples like Roxanne in NYC and other legal aid tools show practical applications for housing-related legal issues, similar to the chatbot we aim to develop.  
   - Further reading on housing-related chatbots and legal implications for implementing such systems.

## 15. **Key Considerations for Client**  
   - Ensure clarity regarding legal limitations and privacy issues.  
   - Request high-quality legal documents from clients to minimize risks of outdated or incorrect legal information.

## Conclusion  
This research outlines various aspects of building AI-powered legal assistance systems using large language models. It covers methodologies for improving response accuracy, integrating real-time data, and ensuring privacy and ethical standards are met in legal applications. Key technologies such as LangChain, Faiss, and RAG play a crucial role in making these systems efficient and scalable.
