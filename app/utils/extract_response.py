import re

def extract_response_features(text):
    motions = re.findall(r'\{([^}]+)\}', text)
    sounds = re.findall(r'<([^>]+)>', text)
    emotions = re.findall(r'\(([^)]+)\)', text)

    emojis = re.findall(r'[\U0001F600-\U0001F64F]', text)  

    return {
        "motions": motions,
        "sounds": sounds,
        "emotions": emotions + emojis  
    }

