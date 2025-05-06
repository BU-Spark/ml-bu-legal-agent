***Project Information*** 

* What is the project name?
  *   BU School of Law: Legal Chatbot
* What is the link to your project’s GitHub repository?
  * [GitHub repo page](https://github.com/BU-Spark/ml-bu-legal-agent).
* What is the link to your project’s Google Drive folder? \*\**This should be a Spark\! Owned Google Drive folder \- please contact your PM if you do not have access\*\**  
  * [Drive folder](https://drive.google.com/drive/folders/1KHqk_Gim0-fEDxkVgO5m6MOGkFjS6SCR).
* In your own words, what is this project about? What is the goal of this project?   
  *   This project will focus on designing and prototyping an AI-powered legal assistance chatbot tailored for individuals facing eviction and other housing-related legal issues. The chatbot will use large language models (LLMs) to provide users with accurate legal information, assist in drafting legal pleadings, and guide them through court processes. Students will train and test LLMs on curated datasets from credible legal sources (e.g., MassLegalHelp.org, Mass.freelegalanswers.org) and evaluate the chatbot’s responses for accuracy and relevance.
* Who is the client for the project?
  *   BU Law Consumer Economic Justice Clinic
  *   The Consumer Economic Justice Clinic is a new 12-credit year-long experiential course that teaches students civil litigation and consumer law. As part of this program, students analyze the causes of economic injustice while representing low-income consumers in a variety of civil cases.
  *   [Read more about our client here](https://www.bu.edu/law/experiential-learning/clinics/consumer-economic-justice-clinic/).
* Who are the client contacts for the project?
  *   Jade Brown - jbrown20@bu.edu
  *   Orestes Rellos - orellos@bu.edu
  *   John Cloherty - jcloher1@bu.edu
  *   Russ Wilcox, expert in residence - russ@artifexai.io 
* What class was this project part of?
  *   Spark Machine Learning Practicum: CDS DS 594

***Dataset Information***

* What data sets did you use in your project? Please provide a link to the data sets, this could be a link to a folder in your GitHub Repo, Spark\! owned Google Drive Folder for this project, or a path on the SCC, etc.
  *   [Legal tactics textbook](https://github.com/BU-Spark/ml-bu-legal-agent/tree/dev/data).
  *   [Web scraping data links](https://docs.google.com/document/d/1VKD4x6PPNmpP7nMCUztWVns8A_8ouhdFdDawQiDH7QE/edit?tab=t.0) 
* What keywords or tags would you attach to the data set?  
  * Domain(s) of Application: NLP, Text Classification, Summarization, Anomaly Detection, Other: Chatbot  
  * Civic Tech, Housing, Education, Other: Law. 

*The following questions pertain to the datasets you used in your project.*   
*Motivation* 
* For what purpose was the dataset created? Was there a specific task in mind? Was there a specific gap that needed to be filled? Please provide a description.
  * The dataset was created to support the development of an AI-powered legal assistance chatbot. The primary goal was to provide users—particularly tenants and landlords—with accessible, reliable, and well-structured information on housing-related legal issues. By sourcing data from the Legal Tactics textbook and authoritative legal websites, the dataset ensures comprehensive coverage of relevant laws and regulations.
  * The chatbot was designed to fill a critical gap: simplifying complex legal information and making it more digestible for users who might not have formal legal training. It leverages similarity searches within a chroma database to generate responses tailored to user queries. This approach enhances accessibility by providing clear, easy-to-understand answers backed by verified legal sources.
  * Additionally, the dataset was structured to allow ongoing updates. Since housing laws evolve, maintaining a current and accurate repository ensures that users receive up-to-date legal guidance. Future improvements may involve refining keyword tagging, validating data sources, and expanding the database as new laws emerge.
 

*Composition*
* What do the instances that comprise the dataset represent (e.g., documents, photos, people, countries)? Are there multiple types of instances (e.g., movies, users, and ratings; people and interactions between them; nodes and edges)? What is the format of the instances (e.g., image data, text data, tabular data, audio data, video data, time series, graph data, geospatial data, multimodal (please specify), etc.)? Please provide a description.
  * Document instances with text data format.   
* Are there any errors, sources of noise, or redundancies in the dataset? If so, please provide a description.
  * There should not be any errors or sources of noise in the dataset. However, there may be some redundancies solely due to the fact that we are sourcing from both the legal tactics textbook and websites. It is inherent that information from the websites will also be located in the textbook as the textbook is  a summary version of all laws included in the websites, just phrased differently and at different levels of detail. 
* Is the dataset self-contained, or does it link to or otherwise rely on external resources (e.g., websites, tweets, other datasets)? If it links to or relies on external resources,   
  * The dataset is not self contained. It depends on external websites and a published textbook. It is important to guarantee that the links being scraped continue to exist, and if they break, they must be updated with the new links. Currently, there are no fees associated with any of the external resources. But, if we try to obtain a newer copy of the book, we may have to pay. 
  
*Collection Process*
* What mechanisms or procedures were used to collect the data? How were these mechanisms or procedures validated?  
  * Open AI API - LLM
  * Scraped, provided by the client - mass legal links for chroma database knowledge base
  * Taken from other existing datasets - published version 2018 legal tactics textbook
  * These mechanisms or procedures were validated through verbal confirmation with the client as well as examining the validity of responses produced by the chatbot. 

*Preprocessing/cleaning/labeling* 
* Was any preprocessing/cleaning/labeling of the data done (e.g., discretization or bucketing, tokenization, part-of-speech tagging, SIFT feature extraction, removal of instances, processing of missing values)? If so, please provide a description. If not, you may skip the remaining questions in this section.
  * The current data is tagged to assign a role based on detected keywords. The current keywords for 
    tenants are "tenant rights", "rent control", "eviction protections", and "lease termination" and for 
    landlords are "landlord duties", "property maintenance", "rent collection", and "eviction process". This tagging process was done for the legal tactics textbook only. 
* Is the code that was used to preprocess/clean the data available?
  * Find in pdf_process script in the Github repository. 

*Uses* 
* What tasks has the dataset been used for so far? Please provide a description.
  *  Our dataset is the basis for our chatbot. When the user asks a question to the chatbot, it parses the query and draws out the key information/words from it. It then searches the full chroma database for information that would help answer the question by implemented similarity searches. The similarity search returns the topmost relevant information, and this is all used to formulate a friendly, understandable response to the user's question.
* Is there anything about the composition of the dataset or the way it was collected and preprocessed/cleaned/labeled that might impact future uses?
  * It might be necessary to update the chroma database every couple of months, or as laws are updated so that user queries are answered with the most up-to-date information. Additionally, the current data is tagged to assign a role based on detected keywords. It might be necessary to do more research 
    on the keywords themselves to see which ones are the correct keywords to put in each list. The current keywords for 
    tenants are "tenant rights", "rent control", "eviction protections", and "lease termination" and for 
    landlords are "landlord duties", "property maintenance", "rent collection", and "eviction process".

    
*Distribution*
* Based on discussions with the client, what access type should this dataset be given (eg., Internal (Restricted), External Open Access, Other)?
  *   External open access
*Maintenance* 
* If others want to extend/augment/build on/contribute to the dataset, is there a mechanism for them to do so? If so, please provide a description.
  * Currently, the legal tactics textbook is mainly from 2018, with some updated chapters from later years. It would be helpful if we could openly obtain a more recent version of this textbook in order to gain access to the most updated information. If found, the same scripts for chunking and tagging can be used, and a newer/updated chroma database would need to be created. With this, as the mass legal websites continue to get updated, they may have to be rescraped. Again, the exisiting processes can be used and the extended chroma database can be updated. 

