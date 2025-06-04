# import re 
# import requests

# def get_video_id(link: str) -> None | str:
#     regex = r"(?:youtu\.be\/|youtube\.com\/(?:.*v=|.*\/|.*embed\/|v\/|shorts\/))([\w-]{11})"
#     match = re.search(regex, link)
#     return match.group(1) if match else None 


# def generate_output_filename(yt_title: str) -> str:
#     sanitized_title = re.sub(r'[^a-zA-Z0-9_]', ' ', yt_title)
#     suffix = " 1 Hour looped"
#     youtube_title_limit = 100
#     required_title_length = youtube_title_limit - len(suffix)

#     if len(sanitized_title) > required_title_length:
#         return f"{sanitized_title[:required_title_length]} {suffix}"
#     else:
#         return f"{sanitized_title} {suffix}"


# links = 'https://youtu.be/snYu2JUqSWs?feature=shared'
# api_key = 'AIzaSyCFXnN-uxP6hTJN2yruxaKc1d6R_83sBeg'
# video_id = get_video_id(links) 
# api_url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&part=snippet,contentDetails,statistics&key={api_key}"

# res = requests.get(api_url)

# print(generate_output_filename(res.json()['items'][0]['snippet']['title']))

print("mp3" in "apodkasdok.mp4")