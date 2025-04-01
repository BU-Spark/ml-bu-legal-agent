# AI-Powered Legal Assistance Chatbot for Housing-related Legal Issues

## Client: BU Law Consumer Economic Justice Clinic

### Project Overview
The Consumer Economic Justice Clinic is a year-long experiential course at Boston University's School of Law, focused on teaching students civil litigation and consumer law. As part of this course, students analyze the causes of economic injustice while representing low-income consumers in civil cases. 

The project aims to design and prototype an AI-powered legal assistance chatbot tailored for individuals facing eviction and other housing-related legal issues. Using Large Language Models (LLMs), this chatbot will provide users with accurate legal information, assist in drafting legal pleadings, and guide them through court processes.

### Project Description
The chatbot will leverage LLMs trained on curated datasets from credible legal sources such as MassLegalHelp.org and Mass.freelegalanswers.org. The goal is to ensure that the AI provides accurate, relevant legal advice and resources to individuals dealing with housing-related issues. Students in the clinic will train, test, and evaluate the chatbot’s responses for accuracy and relevance, ensuring the tool is effective in assisting low-income consumers with their legal needs.

### Ideal Output & Final Deliverables
The final deliverables of the project will include:
- **Proof of Concept (PoC)**: Hosted on HuggingFace, showcasing the AI chatbot’s ability to provide legal assistance.
- **Code and Datasets**: All code and cleaned datasets will be uploaded to a designated Google Drive and GitHub repository. This will include code used to process and clean datasets, as well as any scripts for creating visualizations.
- **Presentation**: The final presentation will cover:
  - **How the LLM Works**: A basic explanation of the LLM architecture and fine-tuning process, with a focus on tailoring it for the chatbot’s specific use case.
  - **Findings on LLM Accuracy**: Key accuracy metrics, including precision, recall, and F1-score, to demonstrate the chatbot’s effectiveness.
  - **Statistics and Visualizations**: Graphs and tables to showcase model performance.
  - **Future Development Recommendations**: Ideas for scaling the project, integrating new datasets, and expanding functionality. Discussion on methods to mitigate inaccuracies in responses.

## Installation & Setup

To get started with this project, follow the steps below:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/BU-Spark/ml-bu-legal-agent.git
   cd ml-bu-legal-agent
   ```

2. **Download and pull Ollama**:
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
    python poc-v1/pdf_process.ipynb
    ```

[will update as we add more code to repo]