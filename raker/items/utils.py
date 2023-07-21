import re

EMOJI_PATTERN = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)
def normalize_text(in_text):
    # Remove \xa0 (non-breaking space) and \u200b (zero-width space) characters
    content = re.sub("[\xa0\u200b]", " ", content)
    # Remove multiple spaces, tabs, and newlines
    content = re.sub("\n+", "\n", content)
    content = re.sub("\t+", "\t", content)
    content = re.sub(" +", " ", content)
    # Remove leading and trailing spaces, tabs, and newlines
    content = content.strip()
    return item
