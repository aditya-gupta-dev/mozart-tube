import os
from src.config import ConfigLoader
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from progress.bar import Bar
from src.logger import Logger, LoggingLevel

class YouTubeUploader:
    def __init__(self, logger: Logger, config_loader: ConfigLoader,client_secrets_file='client_secrets.json', token_file='token.json'):
        self.logger = logger
        self.config_loader = config_loader
        self.client_secrets_file = client_secrets_file
        self.token_file = token_file
        self.scopes = ['https://www.googleapis.com/auth/youtube.upload']
        self.youtube = None
        self.upload_speed = 5 * 1024 * 1024 # upload speed (size of each chunk)

        if not os.path.exists(self.client_secrets_file):
            self.logger.log_file_with_stdout(f'client_secrets.json not found : searhed at [ {self.client_secrets_file} ]', LoggingLevel.Error)
            exit()
        
    def authenticate(self):
        """Authenticate with Google OAuth2"""
        creds = None
        
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # if self._is_headless_environment():
                #     creds = self._headless_authentication()
                # else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.client_secrets_file, self.scopes)
                    creds = flow.run_local_server(port=8080)
            
            # Save credentials for next run
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        
        # Build YouTube API service
        self.youtube = build('youtube', 'v3', credentials=creds)
        self.logger.log_file_with_stdout("Successfully authenticated with YouTube API", LoggingLevel.Info)
    
    def _is_headless_environment(self):
        """Check if running in headless environment"""
        import shutil
        return (os.environ.get('DISPLAY') is None or 
                shutil.which('xdg-open') is None or
                os.environ.get('DOCKER_CONTAINER') == 'true')
    
    def _headless_authentication(self):
        """Handle authentication in headless environment"""
        flow = InstalledAppFlow.from_client_secrets_file(
            self.client_secrets_file, self.scopes)
        
        auth_url, _ = flow.authorization_url(prompt='consent')
        
        print("\n" + "="*60)
        print("🔐 MANUAL AUTHENTICATION REQUIRED")
        print("="*60)
        print("Since we're running in a headless environment (Docker),")
        print("please complete authentication manually:")
        print("\n1. Open this URL in your browser:")
        print(f"\n{auth_url}\n")
        print("2. Complete the authorization process")
        print("3. Copy the authorization code from the redirect URL")
        print("4. Paste it below when prompted")
        print("="*60)
        
        auth_code = input("\nEnter the authorization code: ").strip()
    
        flow.fetch_token(code=auth_code)
        return flow.credentials
        
    def upload_video(self, video_file, title, description, tags=None, category_id="22", privacy_status="private"):
        """Upload video to YouTube with progress bar"""
        if not self.youtube:
            raise Exception("Not authenticated. Call authenticate() first.")
        
        if not os.path.exists(video_file):
            raise FileNotFoundError(f"Video file not found: {video_file}")
        
        # Get file size for progress bar
        file_size = os.path.getsize(video_file)
        
        tags = tags or []
        
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status
            }
        }
        
        # Create media upload object with 5mbps upload speed
        media = MediaFileUpload(
            video_file,
            chunksize=self.upload_speed,
            resumable=True
        )
        
        try:
            # Execute upload request
            insert_request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None

            self.logger.log_file_with_stdout(f"Starting upload of '{title}' ({self._format_bytes(file_size)})", LoggingLevel.Info)

            with Bar("Uploading", max=100, suffix='%(percent).1f%% - %(eta)ds') as progress_bar:            
                previous_progress = 0 
                while response is None:
                    status, response = insert_request.next_chunk()

                    if status is None:
                        break 

                    current_progress = status.progress() - previous_progress

                    progress_bar.next(round(current_progress*100))
                    self.logger.log_file_only(f'Upload progress: {current_progress}, bar progress: {round(current_progress*100)}, Response : {response}', LoggingLevel.Info)
                    previous_progress = current_progress

                progress_bar.finish()

            if response == None:
                self.logger.log_file_with_stdout(f'Video Upload probably failed as Response: {response}', LoggingLevel.Error)
                return None
            
            self.logger.log_file_only(f'Response object: {response}', LoggingLevel.Info)
            self.logger.log_file_with_stdout(f"Video '{title}' uploaded successfully. Video ID: {response['id']}", LoggingLevel.Info)
            self.logger.log_file_with_stdout(f"URL: https://www.youtube.com/watch?v={response['id']}", LoggingLevel.Info)

            return response['id']
            
        except HttpError as e:
            self.logger.log_file_with_stdout(f"HTTP error Check your internet connection", LoggingLevel.Error)
            self.logger.log_file_only(f"HTTP error {e.resp.status}: {e.content}", LoggingLevel.Error)

            return None
            
        except Exception as e:
            self.logger.log_file_with_stdout(f'Fatal Error. Quitting...', LoggingLevel.Fatal)
            self.logger.log_file_only(f"Upload error: {str(e)}", LoggingLevel.Fatal)
            
            return None 
        
    # def _resumable_upload_with_progress(self, insert_request, total_size):
    #     """Handle resumable upload with tqdm progress bar"""
    #     response = None
    #     error = None
        
    #     try:
    #         while response is None:
    #             try:
    #                 status, response = insert_request.next_chunk()
    #                 if status:
    #                     # Update progress bar
    #                     current_progress = int(status.resumable_progress)
    #                     progress_increment = current_progress - last_progress
    #                     self.logger.log_file_only(f'Upload progress {progress_increment}', LoggingLevel.Info)
    #                     last_progress = current_progress
                        
    #             except HttpError as e:
    #                 if e.resp.status in [500, 502, 503, 504]:
    #                     error = f"Retriable HTTP error {e.resp.status}: {e.content}"
    #                     self.logger.log_file_only(f'Error while uploading file check your connection !', LoggingLevel.Error)
    #                     self.logger.log_file_only(f'Upload Error :{error}', LoggingLevel.Error)
    #                 else:
    #                     raise
    #             except Exception as e:
    #                 error = f"Retriable error: {e}"
                
    #             if error is not None:
    #                 retry += 1
    #                 if retry > 3:
    #                     raise Exception("Maximum retry attempts exceeded")
                    
    #                 # Exponential backoff
    #                 wait_time = 2 ** retry
    #                 time.sleep(wait_time)
    #                 error = None
            
    #     except Exception as e:
    #         self.logger.log_file_only(f'Error while uploading file check your connection !', LoggingLevel.Error)
    #         self.logger.log_file_only(f'Upload Error :{e}', LoggingLevel.Error)
        
    #     return response
    
    def upload_thumbnail(self, video_id, thumbnail_path):
        """Upload thumbnail for a video."""
        if not self.youtube:
            self.logger.log_file_with_stdout(f'authenticate your channel.', LoggingLevel.Fatal)
            exit()

        try:
            self.logger.log_file_with_stdout(f"Uploading thumbnail: {os.path.basename(thumbnail_path)}", LoggingLevel.Info)
            self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
            self.logger.log_file_with_stdout("Thumbnail uploaded successfully!", LoggingLevel.Error)
        except Exception as e:
            self.logger.log_file_with_stdout(f"Error uploading thumbnail: {e}", LoggingLevel.Error)
    

    def _format_bytes(self, bytes_size):
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} TB"    
