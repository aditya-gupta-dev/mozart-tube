from src.config import ConfigLoader
from src.logger import Logger, LoggingLevel
import requests
import re 
import os 
import subprocess
import math
import time
import requests 

class VideoEditor():
    def __init__(self, link: str, logger: Logger, configLoader: ConfigLoader):
        self.link = link
        self.logger = logger 
        self.failed = False
        self.already_as_mp4 = False
        self.final_output_video_duration: int = 30
        self.config_loader = configLoader
        self.video_id = self.get_video_id()
        self.logger.log_file_with_stdout(f'Started Editing [ {self.video_id} ]', LoggingLevel.Info)

    def get_video_id(self) -> None | str:
        self.logger.log_file_only(f'parsing link {self.link}', LoggingLevel.Info)
        regex = r"(?:youtu\.be\/|youtube\.com\/(?:.*v=|.*\/|.*embed\/|v\/|shorts\/))([\w-]{11})"
        match = re.search(regex, self.link)
        self.logger.log_file_only(f'parsed link {self.link} -> Result {match.group(1)}', LoggingLevel.Info)
        return match.group(1) if match else None 

    def get_video_title(self):
        api_key = self.config_loader.get_youtube_api_key()
        video_id = self.get_video_id()
        api_url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&part=snippet,contentDetails,statistics&key={api_key}"
        
        try:
            response = requests.get(api_url)

            if not response.ok:
                self.logger.log_file_with_stdout(f'Failed to request youtube. Status code :{response.status_code}', LoggingLevel.Error)
                self.logger.log_file_with_stdout(f'Returning default name : <Viral song 1 hour looped>')
            
                return 'Viral Song'
            
            self.logger.log_file_only(f'Youtube Response Headers with {response.headers}', LoggingLevel.Info)
            self.logger.log_file_only(f'Extracted Title {response.json()['items'][0]['snippet']['title']}', LoggingLevel.Info)
            
            return response.json()['items'][0]['snippet']['title']

        except requests.ConnectionError as conn_error:
            self.logger.log_file_with_stdout(f'Please check your internet connection !!', LoggingLevel.Error)
            self.logger.log_file_only(f'Connection error Url :{conn_error.request.url}', LoggingLevel.Error)
            self.logger.log_file_only(f'Connection error Headers :{conn_error.response.headers}', LoggingLevel.Error)
            self.logger.log_file_only(f'Connection error Status code :{conn_error.response.status_code}', LoggingLevel.Error)

            return 'Viral Song'

        except Exception as e:
            self.logger.log_file_with_stdout('Fatal Error, Ending everything.', LoggingLevel.Fatal)
            self.logger.log_file_only(f'Fatal Error Requests {e}', LoggingLevel.Fatal)
            
            return 'Viral Song'

    def generate_output_filename(self, yt_title: str) -> str:
        sanitized_title = re.sub(r'[^a-zA-Z0-9_]', ' ', yt_title)
        suffix = " 1 Hour looped"
        youtube_title_limit = 100
        required_title_length = youtube_title_limit - len(suffix)

        if len(sanitized_title) > required_title_length:
            extracted_title = f'{sanitized_title[:required_title_length]} {suffix}'
            self.logger.log_file_only(f'Extracted title : {extracted_title}')

            return f"{sanitized_title[:required_title_length]} {suffix}"
        else:
            extracted_title = f'{sanitized_title} {suffix}'
            self.logger.log_file_only(f'Extracted title : {extracted_title}', LoggingLevel.Info)
            
            return f"{sanitized_title} {suffix}"
 
    def edit(self):
        self.convert_to_mp4()
        self.extract_audio_from_video()
        self.merging_asset_and_audio_file()
        self.get_video_duration()
        self.generate_concat_demuxer_file()
        self.render_final_output_video() 
        self.download_original_thumbnail()               

    def convert_to_mp4(self):
        saved_dir = f'files/{self.video_id}'
        self.logger.log_file_with_stdout(f'Converting [ {saved_dir}/input.webm ] to mp4', LoggingLevel.Info)
       
        if os.path.exists(f'{saved_dir}/input.mp4'):
            self.already_as_mp4 = True 
            self.logger.log_file_with_stdout(f'Video was already downloaded as .mp4, Skipping conversion', LoggingLevel.Info)
            return 
        
        if os.path.exists(f'{saved_dir}/output.mp4'):
            self.logger.log_file_with_stdout(f'output.mp4 already exists. skipping this step!!', LoggingLevel.Info)
            return
        
        ffmpeg_path = self.config_loader.get_ffmpeg_path()

        try:
            process = subprocess.run(
                args=[ffmpeg_path, '-i', f'{saved_dir}/input.webm', '-c', 'copy', f'{saved_dir}/output.mp4'],
                capture_output=True,
                shell=True,
                check=True
            )

            self.logger.log_file_only(f'ffmpeg return code {process.returncode}', LoggingLevel.Info)
            self.logger.log_file_only(f'ffmpeg args : {process.args}', LoggingLevel.Info)
            self.logger.log_file_with_stdout(f'Completed converting to mp4 {saved_dir}/output.mp4', LoggingLevel.Info)
            
            if process.stdout:
                self.logger.log_file_only(f'Ffmpeg stdout {process.stdout}', LoggingLevel.Info)
                self.failed = False
            if process.stderr:
                self.logger.log_file_only(f'Ffmpeg stderr {process.stderr}', LoggingLevel.Info)
                self.failed = False
        
        except subprocess.CalledProcessError as process_error:
            self.logger.log_file_with_stdout(f'Failed converting to mp4 {saved_dir}/ouptut.mp4', LoggingLevel.Error)
            self.logger.log_file_only(f'ffmpeg returned with status code {process_error.returncode}', LoggingLevel.Error)
            self.logger.log_file_only(f'ffmpeg stderr {process_error.stderr}', LoggingLevel.Error)
            self.failed = True
        
        except Exception as e:
            self.logger.log_file_with_stdout(f'Fatal error, quitting.', LoggingLevel.Fatal)
            self.logger.log_file_only(f'Error {e}.', LoggingLevel.Fatal)
            self.failed = True
    
    def extract_audio_from_video(self):
        filename = 'input.webm'

        if self.failed:
            self.logger.log_file_with_stdout(f'previous step was failed quitting (extraction of audio) for this video entirely.', LoggingLevel.Error)
            return

        if self.already_as_mp4:
            filename = 'input.mp4'


        saved_dir = f'files/{self.video_id}'
        self.logger.log_file_with_stdout(f'Extracting audio from [ {saved_dir}/input.webm ]', LoggingLevel.Info)
        
        if os.path.exists(f'{saved_dir}/audio.mp3'):
            self.logger.log_file_with_stdout('audio.mp3 already exists. Skipping this step !!', LoggingLevel.Info)
            return 

        ffmpeg_path = self.config_loader.get_ffmpeg_path()

        try:
            process = subprocess.run(
                args=[ffmpeg_path, '-i', f'{saved_dir}/{filename}', '-q:a', '0', '-map', 'a', f'{saved_dir}/audio.mp3'],
                capture_output=True,
                shell=True,
                check=True
            )

            self.logger.log_file_only(f'ffmpeg return code {process.returncode}', LoggingLevel.Info)
            self.logger.log_file_only(f'ffmpeg args : {process.args}', LoggingLevel.Info)
            self.logger.log_file_with_stdout(f'Completed extracting audio from {saved_dir}/output.mp4', LoggingLevel.Info)
            
            if process.stdout:
                self.logger.log_file_only(f'Ffmpeg stdout {process.stdout}', LoggingLevel.Info)
                self.failed = False
            if process.stderr:
                self.logger.log_file_only(f'Ffmpeg stderr {process.stderr}', LoggingLevel.Info)
                self.failed = False
        
        except subprocess.CalledProcessError as process_error:
            self.logger.log_file_with_stdout(f'Failed extracting audio from {saved_dir}/ouptut.mp4', LoggingLevel.Error)
            self.logger.log_file_only(f'ffmpeg returned with status code {process_error.returncode}', LoggingLevel.Error)
            self.logger.log_file_only(f'ffmpeg stderr {process_error.stderr}', LoggingLevel.Error)
            self.failed = True
        
        except Exception as e:
            self.logger.log_file_with_stdout(f'Fatal error, quitting.', LoggingLevel.Fatal)
            self.logger.log_file_only(f'Error {e}.', LoggingLevel.Fatal)
            self.failed = True
    
    def merging_asset_and_audio_file(self):
        if self.failed:
            self.logger.log_file_with_stdout(f'previous step was failed quitting (merger of asset and audio) for this video entirely.', LoggingLevel.Error)
            return

        saved_dir = f'files/{self.video_id}'
        self.logger.log_file_with_stdout(f'Merging audio and asset file together', LoggingLevel.Info)

        if os.path.exists(f'{saved_dir}/final_output.mp4'):
            self.logger.log_file_with_stdout('final_output.mp4 already exists. Skipping this step !!', LoggingLevel.Info)
            return

        ffmpeg_path = self.config_loader.get_ffmpeg_path()
        asset_video_path = self.config_loader.get_asset_video_path()

        try:
            process = subprocess.run(   
                args=[ffmpeg_path, '-i', asset_video_path, '-i', f'{saved_dir}/audio.mp3', '-c:v', 'copy', '-c:a', 'aac', f'{saved_dir}/final_output.mp4'],
                capture_output=True,
                shell=True,
                check=True
            )

            self.logger.log_file_only(f'ffmpeg return code {process.returncode}', LoggingLevel.Info)
            self.logger.log_file_only(f'ffmpeg args : {process.args}', LoggingLevel.Info)
            self.logger.log_file_with_stdout(f'Completed merging asset and audio file', LoggingLevel.Info)
            
            if process.stdout:
                self.logger.log_file_only(f'Ffmpeg stdout {process.stdout}', LoggingLevel.Info)
                self.failed = False
            if process.stderr:
                self.logger.log_file_only(f'Ffmpeg stderr {process.stderr}', LoggingLevel.Info)
                self.failed = False
        
        except subprocess.CalledProcessError as process_error:
            self.logger.log_file_with_stdout(f'Failed merging asset and audio file', LoggingLevel.Error)
            self.logger.log_file_only(f'ffmpeg args : {process_error.args}', LoggingLevel.Info)
            self.logger.log_file_only(f'ffmpeg returned with status code {process_error.returncode}', LoggingLevel.Error)
            self.logger.log_file_only(f'ffmpeg stderr {process_error.stderr}', LoggingLevel.Error)
            self.failed = True
        
        except Exception as e:
            self.logger.log_file_with_stdout(f'Fatal error, quitting.', LoggingLevel.Fatal)
            self.logger.log_file_only(f'Error {e}.', LoggingLevel.Fatal)
            self.failed = True

    def generate_concat_demuxer_file(self):
        if self.failed:
            self.logger.log_file_with_stdout(f'previous step was failed quitting (concat-demuxer) for this video entirely.', LoggingLevel.Error)
            return
        
        saved_dir = f'files/{self.video_id}'
        self.logger.log_file_with_stdout(f'Generating concat demuxer file.', LoggingLevel.Info)

        if os.path.exists(f'{saved_dir}/files.txt'): 
            self.logger.log_file_with_stdout('files.txt already exists. Skipping this step !!', LoggingLevel.Info)
            return 

        try:
            output_video_duration = self.config_loader.get_final_video_duration()
            merged_video_duration = self.final_output_video_duration

            repititions = math.ceil(output_video_duration/merged_video_duration)

            with open(f'{saved_dir}/files.txt', 'a') as demuxer_file:
                for element in range(0, repititions):
                    file_path = os.path.join(self.config_loader.pwd, saved_dir, 'final_output.mp4')
                    self.logger.log_file_with_stdout(f'\t-{element} - {file_path}', LoggingLevel.Info)
                    demuxer_file.write(f"file '{file_path}'\n")

        except Exception as e:
            self.logger.log_file_with_stdout(f'Failed to generate demuxer file.', LoggingLevel.Error)
            self.logger.log_file_only(f'Demuxer file generation Error: {e}', LoggingLevel.Error)

    def render_final_output_video(self):
        if self.failed:
            self.logger.log_file_with_stdout(f'previous step was failed (Rendering final video) for this video entirely.', LoggingLevel.Error)
            return
        
        title = self.get_video_title()
        filename = self.generate_output_filename(title)
        
        saved_dir = f'files/{self.video_id}'
        self.logger.log_file_with_stdout(f'Rendering final video.', LoggingLevel.Info)
        
        ffmpeg_path = self.config_loader.get_ffmpeg_path()
        output_dir = self.config_loader.get_output_directory()

        if not os.path.exists(f'{output_dir}/{self.video_id}'):
            self.logger.log_file_with_stdout(f'Output directory not found. creating one instead ! -> {output_dir}/{self.video_id}', LoggingLevel.Info)
            os.mkdir(f'{output_dir}/{self.video_id}')
        else:
            self.logger.log_file_with_stdout(f'Output directory exists. Moving on', LoggingLevel.Info)

        if os.path.exists(f'{output_dir}/{self.video_id}/{filename}.mp4'):
            self.logger.log_file_with_stdout(f'Output was already created, Skipping this step !', LoggingLevel.Info)
            return 

        try:

            start_time = time.time()

            process = subprocess.run(   
                args=[ffmpeg_path, '-f', 'concat', '-safe', '0', '-i', f'{saved_dir}/files.txt', '-c', 'copy', f'{output_dir}/{self.video_id}/{filename}.mp4'],
                capture_output=True,
                shell=True,
                check=True
            )

            end_time = time.time()

            self.logger.log_file_only(f'ffmpeg return code {process.returncode}', LoggingLevel.Info)
            self.logger.log_file_only(f'ffmpeg args : {process.args}', LoggingLevel.Info)
            self.logger.log_file_with_stdout(f'Completed Rendering output file -> {output_dir}/{self.video_id}/{filename}.mp4', LoggingLevel.Info)
            self.logger.log_file_with_stdout(f'Render Time Took : {end_time - start_time} sec', LoggingLevel.Info)
            

            if process.stdout:
                self.logger.log_file_only(f'ffmpeg stdout {process.stdout}', LoggingLevel.Info)
                self.failed = False
            if process.stderr:
                self.logger.log_file_only(f'ffmpeg stderr {process.stderr}', LoggingLevel.Info)
                self.failed = False
        
        except subprocess.CalledProcessError as process_error:
            self.logger.log_file_with_stdout(f'Failed Rendering final file', LoggingLevel.Error)
            self.logger.log_file_only(f'ffmpeg args : {process_error.args}', LoggingLevel.Info)
            self.logger.log_file_only(f'ffmpeg returned with status code {process_error.returncode}', LoggingLevel.Error)
            self.logger.log_file_only(f'ffmpeg stderr {process_error.stderr}', LoggingLevel.Error)
            self.failed = True
        
        except Exception as e:
            self.logger.log_file_with_stdout(f'Fatal error, quitting.', LoggingLevel.Fatal)
            self.logger.log_file_only(f'Error {e}.', LoggingLevel.Fatal)
            self.failed = True

    def download_original_thumbnail(self):
        output_dir = self.config_loader.get_output_directory()
        video_id = self.get_video_id()

        api_url = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"

        try:
            response = requests.get(api_url)
            
            if not response.ok or response.status_code == 404:
                self.logger.log_file_with_stdout(f'Failed to request youtube. Status code :{response.status_code}', LoggingLevel.Error)
                self.logger.log_file_with_stdout(f'Thumbnail JSON Response : {response.json()}', LoggingLevel.Error)
            
            else:
                with open(f'{output_dir}/{video_id}/{video_id}.jpg', 'wb') as thumbnail_file:
                    thumbnail_file.write(response.content)
            
            self.logger.log_file_with_stdout(f'Successfully downloaded thumbnail file : {output_dir}/{video_id}/{video_id}.jpg', LoggingLevel.Info)
            
        except requests.ConnectionError as conn_error:
            self.logger.log_file_with_stdout(f'connection error while downloading thumbnail.', LoggingLevel.Fatal)
            self.logger.log_file_only(f'Connection Error {conn_error}', LoggingLevel.Fatal)

        except Exception as e:
            self.logger.log_file_with_stdout(f'Unexpected error while parsing image.', LoggingLevel.Fatal)
            self.logger.log_file_only(f'Thumbnail Download Error Details {e}.', LoggingLevel.Fatal)        

    def get_video_duration(self):
        if self.failed:
            self.logger.log_file_with_stdout(f'previous step was failed, (calculating video duration) for this video entirely.', LoggingLevel.Error)
            return

        saved_dir = f'files/{self.video_id}'
        self.logger.log_file_with_stdout(f'Calculating video duration.', LoggingLevel.Info)
        
        ffprobe_path = self.config_loader.get_ffprobe_path()

        try:
            process = subprocess.run(
                args=[ffprobe_path, '-v', 'quiet', '-show_entries', 'format=duration', '-of', 'csv=p=0', f'{saved_dir}/final_output.mp4'],
                capture_output=True,
                shell=True,
                check=True
            )

            self.logger.log_file_only(f'ffmpeg return code {process.returncode}', LoggingLevel.Info)
            self.logger.log_file_only(f'ffmpeg args : {process.args}', LoggingLevel.Info)
            self.logger.log_file_with_stdout(f'Completed Extracting duration', LoggingLevel.Info)
            
            if process.stdout:
                self.logger.log_file_only(f'ffmpeg stdout {process.stdout}', LoggingLevel.Info)
                self.final_output_video_duration = int(float(process.stdout.strip()))
                self.failed = False
            if process.stderr:
                self.logger.log_file_only(f'ffmpeg stderr {process.stderr}', LoggingLevel.Error)
                self.failed = False

            self.logger.log_file_with_stdout(f'Calculated video duration :{self.final_output_video_duration} s', LoggingLevel.Info)
        
        except subprocess.CalledProcessError as process_error:
            self.logger.log_file_only(f'ffmpeg args : {process.args}', LoggingLevel.Info)
            self.logger.log_file_with_stdout(f'Failed Calculating video duration', LoggingLevel.Error)
            self.logger.log_file_only(f'ffmpeg returned with status code {process_error.returncode}', LoggingLevel.Error)
            self.logger.log_file_only(f'ffmpeg stderr {process_error.stderr}', LoggingLevel.Error)
            self.failed = True
        
        except Exception as e:
            self.logger.log_file_with_stdout(f'Fatal error, quitting.', LoggingLevel.Fatal)
            self.logger.log_file_only(f'Error {e}.', LoggingLevel.Fatal)
            self.failed = True