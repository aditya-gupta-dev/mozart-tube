import re 

def generate_output_filename(yt_title: str) -> str:
    sanitized_title = re.sub(r'[^a-zA-Z0-9_]', ' ', yt_title)
    suffix = " 1 Hour looped"
    youtube_title_limit = 100
    required_title_length = youtube_title_limit - len(suffix)
    
    if len(sanitized_title) > required_title_length:
        return f"{sanitized_title[:required_title_length]} {suffix}"
    else:
        return f"{sanitized_title} {suffix}"