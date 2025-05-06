import requests
import openai

GAFFA_API_KEY = os.getenv("GAFFA_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def fetch_markdown_with_gaffa(url):
    payload = {
        "url": url,
        "proxy_location": None,
        "async": False,
        "max_cache_age": 0,
        "settings": {
            "record_request": False,
            "actions": [
                {
                    "type": "wait",
                    "selector": "article"
                },
                {
                    "type": "generate_markdown"
                }
            ]
        }
    }


    headers = {
        "x-api-key": GAFFA_API_KEY,
        "Content-Type": "application/json"
    }


    print("Calling Gaffa API to generate markdown...")
    response = requests.post("https://api.gaffa.dev/v1/browser/requests", json=payload, headers=headers)
    response.raise_for_status()


    markdown_url = response.json()["data"]["actions"][1]["output"]


    print(f"📥 Fetching markdown from: {markdown_url}")
    markdown_response = requests.get(markdown_url)
    markdown_response.raise_for_status()


    return markdown_response.text
  
  def ask_question(markdown, question):
    openai.api_key = OPENAI_API_KEY
    prompt = (
        f"You are an assistant helping analyze different webpages.\n\n"
        f"Markdown content:\n{markdown[:3000]}\n\n"
        f"Question: {question}\nAnswer as clearly as possible."
    )


    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message["content"]

  def main():
    url = input("Enter the URL of the article: ")
    try:
        markdown = fetch_markdown_with_gaffa(url)
        print("\n✅ Markdown successfully retrieved from Gaffa.\n")


        while True:
            question = input("Ask a question about the content (or type 'exit'): ")
            if question.lower() == "exit":
                break
            answer = ask_question(markdown, question)
            print(f"\n💬 Answer: {answer}\n")


    except Exception as e:
        print(f"⚠️ Error: {e}")

 if __name__ == "__main__":
    main()
