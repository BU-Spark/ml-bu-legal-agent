# BU Law Legal Agent - Technical Project Document

## *Sindhuja Kumar, Amogh Mittal, Riya Parikh, Tomas Samoulis <br /> 2025-02-11 v0.1.0-dev*

## Overview

The goal of the project is to design and prototype an AI-powered legal assistance chatbot tailored for individuals facing eviction and other housing-related legal issues. The chatbot will use (large language models) LLMs to provide end users with accurate legal information, assist in drafting legal pleadings, and guide them through court processes. As a team we will train and test LLMs on the curated datasets provided to us by the client that are credible legal sources (eg: MassLegalHelp.org) and evaluate the chatbot's response for accuracy with the 2L students assigned to this project. 

*It is pertinent to loop in 2L students throughout the evaluation stages to ensure desired behavior of the agent.*   

__Here are the high level steps to complete this project:__

1. Define the Scope of the Legal Issue
    - We must carefully scope the extend to which the _legal agent_ can provide "advice" and/or legal assistance to prevent unnecessary ethical dilemmas for end users using the tool in a court setting.
    - This will involve the definition of the amount of human intervention needed to work with the agent in complex situations. 
    - We will consult with 2L students to help us define the scope of work for the _legal agent_. 

2. Research How to Build LLM Chatbot
    - We will collect a literature that will help us gain field knowledge in building chatbots for legal assistance. 

3. Clean and Prepare Legal Resources Dataset
    - We will complie a dataset that includes a wide variety of text data and examples relavent to the chatbot's intended tasks from the resources that were provided to us by the client. 
    - This contains typical tenant queries, domain-specific jargon, and appropriate legal sources to cite with appropriate responses.  

4. Choose the Right Model Size
    - It is pertinent that we select an LLM size that balances model performace with our available computing resources and financial budget. 
    - We will consult with Spark! staff and course instructors. 

5. General Language Pre-Training
    - We will start with an LLM that has been pre-trained on broad linguistic data which will provide a solid foundation for the chatbot in natural language understanding.

6. Apply Fine-Tuning Techniques
    - This involves using AI techniques such as transfer learning, prompt engineering to adapt the chatbot's creative content to our specific use case. 
    - Here we will provide it with textual data that reflects actual tenant queries and answers in the evication and housing-related legal issues field.

7. Adjust Model Parameters
    - We will adjust LLM training paramteres such as learning rates to improve performance. 
    - This will also include any improvements based on 2L students' review of the chatbot's behavior to certain queries in the evaluation phase. 

8. Test and Evaluate 
    - Here we will conduct rigorous testing using new, unseen data and evaluate it against "ground truth" data sets and 2L students' review to ensure accuracy. 

9. Monitor and Iterate
    - During this last phase, we plan to deploy and monitor the chatbot's performance. 
    - We will collect feedback from real end users (ex: 2L students, real tenants, etc.) and incorporate it into future fine-tuning sessions to maintain and improve the _legal agent's_ relevance and accuracy.


### A. Provide a solution in terms of human actions to confirm if the task is within the scope of automation through AI.

To assist in outlining the steps needed to achieve our final goal, we must outline the AI-less process that we are trying to automate with machine learning. Currently, individuals facing eviction or other housing-related legal issues navigate a complex, time-consuming, and often inaccessible legal system. Below is a breakdown of the manual process individuals must go through without the assistance of an AI legal chatbot:

1. Identify the Legal Issue
    - Tenants must determine the nature of their legal problem whether that be nonpayment of rent, lease violation, discrimination, etc and then research their legal rights through online sources like MassLegalHelp.org or tenant advocacy groups.

2. Seek Legal Information & Resources
    - Tenants must search for reliable and accurate legal aid websites or contact local community legal aid organizations. They must ensure they find the information in a timely manner such that it is still according to the law and arrives before their hearing date. During this process, tenants may become frustrated due to long wait times from high demand or even due to an overwhelming amount of information to decipher.

3. Consult with Legal Aid or an Attorney
    - Tenants must book an appointment to chat with an attorney who will represent their case. While those with the resources may find an attorney in a short time, low-income and undocumented tenants often struggle to access direct legal representation due to financial issues and documentation requirements. So, for certain groups, scheduling these appointments with legal aid can take weeks.

4. Draft Legal Documents & Prepare for Court
    - Tenants must make sure they are well prepared to represent themselves to the best of their abilities in court. This is definetly easier with a lawyer present, but without legal representation, tenants must draft responses (e.g., motions to dismiss, requests for continuance) themselves. Tenants going through the processes alone often rely on generic templates and risk making errors that could harm their case.

5. Attend Hearings & Navigate Court Procedures
    - Tenants must gather evidence, prepare statements, and represent themselves in court. Tenants that lack the understanding of legal terminology and court procedures increase their risk of unfavorable outcomes.

6. Follow-ups & Post-Hearing Steps
    - Tenants must determine their next steps (e.g., filing appeals, negotiating payment plans) without structured guidance if the ruling is unfavorable. 

Challenges in this AI-less process include limited access to legal aid (due to resource constraints or high costs), complex legal language, time sensitivity of matters, and inconsistent information. By automating key aspects of legal assistance, the chatbot aims to provide immediate, accurate, and structured guidance on housing law, document drafting, and court procedures—reducing the burden on both tenants and legal aid organizations.

### B. Problem Statement:

Develop and evaluate an NLP-driven legal chatbot for eviction and housing-related queries. Fine-tune LLMs on curated legal datasets to generate accurate and contextually relevant responses, assessed using benchmark metrics and expert validation.

### C. Checklist for project completion

Checklist for Project Completion
1. Proof of Concept (PoC) Deployment
- AI-powered legal assistance chatbot hosted on Hugging Face.

2. Code and Data Management

- All source code uploaded to GitHub and Google Drive.
- Cleaned and processed datasets stored in the designated Google Drive folder.
- Code scripts for data cleaning, preprocessing, and visualization included.

3. A Presentation with: 
- Summary of How the LLM Works: Basic explanation of the LLM architecture and fine-tuning process.
    - Focus on how it was tailored for the chatbot’s specific use case.
- Findings on LLM Accuracy: Highlight key accuracy metrics (e.g., precision, recall, F1-score).
    - Statistics and Visualizations: Graphs/tables showing model performance.
- Future Development Recommendations
    - Suggestions for scaling, integrating new datasets, or expanding functionality.
    - Methods to improve response accuracy and mitigate errors.

### D. Outline a path to operationalization.

*Data Science Projects should have an operationalized end point in mind from the onset. Briefly describe how you see the tool produced by this project being used by the end user beyond a jupyter notebook or proof of concept. If possible, be specific and call out the relevant technologies that will be useful when making this available to the stakeholders as a final deliverable.*

The optimal use case for this product is as an assistive tool for low-income individuals with housing issues. This tool would ideally be hosted in the Greater Boston Legal Services website, allowing the public to access it. It would function like a regular chatbot, being able to answer questions and sustain a line of conversation. Currently, the client is indicating that their priority is answering general questions and providing accurate information, but has also suggested the chatbot be able to assist in drafting legal documents. 

All the relevant technologies to make this available are still to be determined, however interfacing with major LLM API's to run the conversation will be the primary one. 

## Resources

### Data Sets

- In order to achieve the best results, the LLM will be trained on curated datasets from credible legal sources. During the data sourcing process, it is important that the team determine reliable legal data sources, distinguishing between public vs. proprietary databases. The model's prototype development will begin using publicly available data.
- Data will come from sources including but not limited to Mass Legal Help, Mass. Governmental Websites, Massachusetts Legal Resource Finder, National Housing Law Project, National Consumer Law Center, MA Legislature, and case law sites.
- All the data is being sourced/scraped from online websites, and can be considered unstructured in its format.
- Data can be found at the following sites for reference:
    - [Spark Data Sets List - contains links to 43 different websites](https://docs.google.com/document/d/1neIGtYK0Wm3jK_5MzYZ0Bz30MBtzOQEl/edit)
    - [50 Questions by Tenants](https://docs.google.com/document/d/1e9q4fUrA5hbgMdKLQh0ImUVkiZ_TWzEM/edit#heading=h.gjdgxs)
    - [Chapter 12: Evictions](https://www.masslegalhelp.org/housing-apartments-shelter/eviction/chapter-12-evictions)
    - [Legal Tactics: Tenants' Rights in Massachusetts](https://www.masslegalhelp.org/housing-apartments-shelter/tenants-rights/legal-tactics)

### References

## Weekly Meeting Updates

*Keep track of ongoing meetings in the Project Description document prepared by Spark staff for your project.*


Note: Once this markdown is finalized and merge, the contents of this should also be appended to the Project Description document.
