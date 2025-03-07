import tiktoken 


# Helper function to calculate the number of tokens used
def calculate_tokens(text):
    # Use cl100k_base, which is the encoding for gpt-3.5-turbo
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))