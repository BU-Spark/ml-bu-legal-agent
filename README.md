# AI-Powered Legal Assistance Chatbot for Housing-related Legal Issues

## Client: BU Law Consumer Economic Justice Clinic

### Project Overview
The **Consumer Economic Justice Clinic** is a year-long experiential course at Boston University's School of Law, focused on teaching students civil litigation and consumer law. As part of this course, students analyze the causes of economic injustice while representing low-income consumers in civil cases. 

The project aims to design and prototype an AI-powered legal assistance chatbot tailored for individuals facing eviction and other housing-related legal issues. Using Large Language Models (LLMs), this chatbot will provide users with accurate legal information, assist in drafting legal pleadings, and guide them through court processes.

### Project Description
The chatbot will leverage LLMs trained on curated datasets from credible legal sources such as MassLegalHelp.org and Mass.freelegalanswers.org. The goal is to ensure that the AI provides accurate, relevant legal advice and resources to individuals dealing with housing-related issues. Students in the clinic will train, test, and evaluate the chatbot’s responses for accuracy and relevance, ensuring the tool is effective in assisting low-income consumers with their legal needs.

### Ideal Output & Final Deliverables

The final deliverables of the project will include:
- **Proof of Concept (PoC)**: Hosted on HuggingFace, showcasing the AI chatbot’s ability to provide legal assistance. ✅
- **Code and Datasets**: All code and cleaned datasets will be uploaded to a designated Google Drive and GitHub repository. This will include code used to process and clean datasets, as well as any scripts for creating visualizations. ✅
    
- **Presentation**: The final presentation will cover:
  - **How the LLM Works**: A basic explanation of the LLM architecture and fine-tuning process, with a focus on tailoring it for the chatbot’s specific use case. ✅

  - **Findings on LLM Accuracy**: Key accuracy metrics, including precision, recall, and F1-score, to demonstrate the chatbot’s effectiveness. ✅

  - **Future Development Recommendations**: Ideas for scaling the project, integrating new datasets, and expanding functionality. Discussion on methods to mitigate inaccuracies in responses. ✅


### Task Status Key
| Task Status | Meaning              |
|-------|----------------------|
| ✅    | Task completed        |
| ⏳    | Work in progress      |
| 🚧   | Blocker      |
| 🛑    | Not started    |

## Installation & Setup (can be found in `README` of poc_v2.1 folder as well)

To get started with this project, follow the steps below:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/BU-Spark/ml-bu-legal-agent.git
   cd ml-bu-legal-agent
   ```

2. **[`OPTIONAL`] Download and pull Ollama**:  
*Optional. OpenAI LLM is system default.*  
*Note: this LLM has not been fully developed and could result in bugs!*
    * Download here: https://ollama.com/download
    * In your terminal, enter the command
         ```
          ollama pull deepseek-r1:1.5b
         ```
    
    * To verify the download
         ```
          ollama list
         ```


3.  **Create a `.env` file:**

    * In the root directory of the repository, create a file named `.env`.
    * Add your OpenAI API key to the `.env` file:

        ```
        OPENAI_API_KEY=your-actual-api-key
        ```

        * Replace `your-actual-api-key` with your actual OpenAI API key.

4.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

5.  **Run the script:**

    ```bash
    python poc-v2.1/main.py
    python poc-v2.1/app.py
    ```

6. **Launch the App Locally:**

    After running the above scripts, open your browser and go to [`http://localhost:7860/`](http://localhost:7860/) to access the app locally. 
    
    You should be able to see the application running on your local machine.

### Further Notes:
* After the chroma databases are installed the first time, it is uneccesary to run `main.py` again, unless you change code inherent to how the databases are being written or validated, or if you are adding new documents/changing the databases themselves. 



## Next Steps

* Explore the possibility of hosting the data on a cloud platform for scalability and accessibility. 
* Deploy the application to a publicly accessible server or hosting platform.
* Extend the data scraping capabilities for the RAG architecture (currently, [these](https://docs.google.com/document/d/1VKD4x6PPNmpP7nMCUztWVns8A_8ouhdFdDawQiDH7QE/edit?usp=drive_link) are the datasets processed in the vector database) 
    * Consider implementing a drag-and-drop feature to facilitate user updates to the RAG architecture.
* Assess the model's performance on a broader range of questions and perform the necessary fine-tuning.
* Collaborate with a UX/UI team to enhance the front-end user interface.
* Integrate a memory component to enable the chatbot to handle follow-up questions in a more conversational manner.
* Investigate the potential for the chatbot to assist users in filling out legal forms, particularly for tenants. 
* Develop the Ollama DeepSeek model, despite concerns regarding performance, as it may prove worthwhile given budgetary constraints.
* Integrate a way to access the cited sources directly through the chatbot website
