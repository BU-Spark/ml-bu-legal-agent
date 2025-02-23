# Research and Projects Overview
[Access contribution history from this Google Doc](https://docs.google.com/document/d/18kg9A_ETLTsL98QjafQc6otS9yGOVAQnd6OsH7GAjbQ/edit?usp=sharing)

## 1. **Build Your First LLM Chatbot - Alisha Saboowala**  
   **Key Concepts:**
   - **Fine-tuning**: Re-training pre-trained LLM with new data to optimize for tasks like sentiment analysis and predictions.  
   - **Context Injection**: Adding relevant context into the prompt instead of altering the LLM.  
   - **Vector Databases**: Storing large amounts of vector data for searching and retrieval based on similarity.  
   - **LangChain's RetrievalQA**: Enables optimized Q&A for documents by retrieving the closest vectors to the query and providing context to the LLM.  
   [Read the full article here](https://medium.com/@alishasaboowala/build-your-first-llm-chatbot-a-beginners-guide-to-large-language-2c19d05b4d4f)

## 2. **Build Your Own AI Chatbot: A Beginner’s Guide to RAG and LangChain - Suraj Bansal**  
   **Key Concepts:**
   - **RAG (Retrieval-Augmented Generation)**: Combines LLM with external knowledge retrieval for more accurate responses.  
   - **Chunking and Overlap**: Splitting documents into smaller parts for memory efficiency and preserving context.  
   - **Stateful Chatbot**: Stores interaction history for natural conversation flow and context.  
   - **ConversationalRetrievalChain**: Builds effective question-answering applications by retrieving and processing documents in LangChain.  
   [Read the full article here](https://medium.com/@surajbansal/build-your-own-ai-chatbot-a-beginners-guide-to-rag-and-langchain-76b6fe9286e8)

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
   [Read the full article here](https://medium.com/@Experto_AI/llm-apis-price-comparison-by-model)

## 5. **Retrieval-Augmented Generation (RAG) - AWS**  
   **Key Insights:**
   - **RAG** enhances LLM performance by retrieving external knowledge during query response.  
   - **Benefits**: Improves response relevance, reduces retraining costs, and supports real-time updates without the need to retrain models.  
   - **Use Cases**: Legal, healthcare, and customer service applications where up-to-date or specialized information is needed.  
   [Read the full article here](https://aws.amazon.com/what-is/retrieval-augmented-generation/)

## 6. **Legal Chatbot Considerations**  
   - **Concerns**: Legal chatbots, like Roxanne (housing-related in NYC), must ensure transparency, privacy, and avoid providing legal advice directly.  
   - **Challenges**: Updating legal data regularly and addressing ambiguity in liability.  
   - **Best Practices**: Inform clients that AI guidance is not legal advice, ensure informed consent, and integrate human oversight for sensitive matters.  
   [Read more about Roxanne here](https://www.thomsonreuters.com/en-us/posts/ai-in-courts/housing-repairs-chatbot/)

## 7. **Research Paper: "Intention and Context Elicitation with LLMs in Legal Aid"**  
   **Key Insights:**
   - This study focuses on enhancing legal intake with LLMs by improving intent and context recognition.  
   - **Application**: Implementing this approach can improve chatbot accuracy in understanding legal contexts and handling multi-turn dialogues.  
   - **Evaluation**: Key metrics like precision, recall, and F1-score are essential for assessing chatbot reliability.  
   [Read the full paper here](https://paperswithcode.com/paper/intention-and-context-elicitation-with-large)

## 8. **Existing Project: LawGPT**  
   **Key Insights:**
   - A reference project on LLMs in the legal domain. Though not directly aligned with our needs, it offers insights into the challenges and solutions for hosting and implementing legal guidance systems using LLMs.  
   [View the project on GitHub](https://github.com/harshitv804/LawGPT)

## 9. **BU Spark ML Chatbot Project Roadmap**  
   **Project Steps:**
   - **Data Scraping & Storage**: Collect data and structure it for retrieval.  
   - **Technologies**: LangChain for orchestrating workflows, Faiss for vector databases.  
   - **Data Chunking & Vectorization**: Split and store data in a Faiss database.  
   - **Response Generation**: Use OpenAI APIs for converting raw data into structured chatbot responses.  
   - **User Interface**: Build UI with tools like Streamlit or Gradio, and deploy via Hugging Face.

## 10. **Additional Resources and Tutorials**  
   - LangChain tutorials and DeepLearning.ai’s LangChain short course for LLM development.  
   [LangChain Documentation](https://python.langchain.com/docs/tutorials/rag/)  
   [LangChain for LLM Application Development](https://www.deeplearning.ai/short-courses/langchain-for-llm-application-development/)

## 11. **Legal Chatbots in Housing**  
   - Examples like Roxanne in NYC and other legal aid tools show practical applications for housing-related legal issues, similar to the chatbot we aim to develop.  
   - Further reading on housing-related chatbots and legal implications for implementing such systems.

## 12. **Key Considerations for Client**  
   - Ensure clarity regarding legal limitations and privacy issues.  
   - Request high-quality legal documents from clients to minimize risks of outdated or incorrect legal information.

## Conclusion  
This research outlines various aspects of building AI-powered legal assistance systems using large language models. It covers methodologies for improving response accuracy, integrating real-time data, and ensuring privacy and ethical standards are met in legal applications. Key technologies such as LangChain, Faiss, and RAG play a crucial role in making these systems efficient and scalable.
