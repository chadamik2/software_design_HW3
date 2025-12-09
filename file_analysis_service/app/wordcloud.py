from urllib.parse import quote_plus


def generate_wordcloud_url(text: str) -> str:
    encoded_text = quote_plus(text)
    return f"https://quickchart.io/wordcloud?text={encoded_text}"
