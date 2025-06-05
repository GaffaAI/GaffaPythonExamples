# Convert Any Web Page to LLM-Ready Markdown Using Gaffa - Building a Simple Python CLI Tool
This folder contains a simple script which will show you how you can use Gaffa to convert any web page to markdown for ingesting into an LLM app. For more information, read the [accompanying post on the Gaffa blog](https://gaffa.dev/blog/convert-any-web-page-to-llm-ready-markdown-using-gaffa) or the [full tutorial](https://gaffa.dev/docs/tutorials/convert-any-webpage-into-llm-ready-markdown-using-gaffa).

## How to Run
First make sure you have the required libraries installed and your API keys set up in the `.env` file. 

Required libraries:
```bash
pip install requests python-dotenv openai
```

Then, run the script using Python:

```bash
python file_name.py
```
Make sure to replace `file_name.py` with the actual name of your Python script.

A successful run will look like this:

```bash
Enter the URL of the article: https://www.freecodecamp.org/news/importerror-cannot-import-name-force-text-from-django-utils-encoding-python-error-solved/        
Calling Gaffa API to generate markdown...
📥 Fetching markdown from: https://storage.gaffa.dev/brq/md/brq_VEmgFwpWCV7J4UrwMMsLXR2wJxputA/act_VEmgFz8kZCichGSVNvTEmRxaEHT5Pg.md


✅ Markdown successfully retrieved from Gaffa.

Ask a question about the content (or type 'exit'): From the article what are the two main reasons mentioned that might cause the error?


💬 Answer: The two main reasons mentioned in the article that might cause the error `ImportError: cannot import name 'force text' from 'django.utils.encoding'` are:
1. Outdated package
2. Incorrect import statement

Ask a question about the content (or type 'exit'): What are API keys

💬 Answer: The markdown content does not contain any information about API keys. It focuses on explaining how to solve the Python error "ImportError: cannot import name 'force text' from 'django.utils.encoding." The content provides steps to update packages and Django, as well as ensuring the correct import statement is used in the code.

Ask a question about the content (or type 'exit'):
```

For more information on the `generate-markdown` action, please see the Gaffa docs.
