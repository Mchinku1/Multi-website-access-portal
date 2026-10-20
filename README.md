🌐 Multi-Website Access Portal

A web-based research hub built with Python and Streamlit that helps users discover information across multiple sources, explore useful websites, and save search results for future reference.

✨ Features
Multi-source search: Search Wikipedia, Open Library, and Hacker News.
Academic research: Search Crossref publications and arXiv scientific preprints.
Website directory: Browse and filter websites by category.
Research results: View results with titles, descriptions, and links to original sources.
Data exploration: Inspect search results and visualize results by source.
Saved searches: Store, reload, and delete previous searches using SQLite.
Data export: Download research results in CSV and JSON formats.
Progress feedback: Track searches and view provider-specific errors.
🛠️ Built With
Python
Streamlit
Pandas
Requests
SQLite
Crossref API
arXiv API
Wikipedia API
Open Library API
Hacker News Search API
📁 Project Structure
Multi-website-access-portal/
├── app.py
├── connectors.py
├── storage.py
├── requirements.txt
├── .gitignore
└── README.md


The portal.db SQLite database is created automatically when the application initializes.

🚀 Getting Started
Prerequisites
Python 3.10 or newer
Git
Internet access for online search providers
1. Clone the repository
git clone https://github.com/Mchinku1/Multi-website-access-portal.git
cd Multi-website-access-portal

2. Create a virtual environment

On Linux or macOS:

python3 -m venv .venv
source .venv/bin/activate


On Windows PowerShell:

py -m venv .venv
.venv\Scripts\Activate.ps1

3. Install dependencies
python -m pip install -r requirements.txt

4. Run the application
python -m streamlit run app.py


Open the local URL printed in your terminal, usually http://localhost:8501.

🔎 How to Use
Open Multi-Source Search.
Enter a topic or research question.
Choose one provider or search all supported providers.
Review the results and open original sources.
Filter or sort results and export them to CSV or JSON.
Visit Saved Searches to reload or delete stored searches.
🔐 Privacy and Security
Local search history is stored in a SQLite database.
The local database and environment secrets should not be committed to a public repository.
Search requests are sent to the selected external providers.
Avoid entering confidential or sensitive information into public search services.
⚠️ Limitations
Search availability depends on external APIs and internet connectivity.
Different providers return different types and amounts of information.
Results should be verified against their original sources.
The application is not a universal search engine and does not index the entire web.
🗺️ Future Improvements
Individual bookmarks and research notes
Advanced search filters and relevance ranking
More academic and public-data sources
Improved error handling, caching, and search performance
Optional source-grounded AI research summaries
User accounts and personalized research libraries
👨‍💻 Author

Mchinku1

GitHub: @Mchinku1

📄 License

No license has been specified yet. Add a license if you want to define how other people may use, modify, and distribute this project.

