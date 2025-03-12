from google.cloud import storage as google_storage
import os
from datetime import datetime

class CloudStorage:
    def __init__(self):
        try:
            # Set the path to your service account key file
            credentials_path = os.path.join(os.path.dirname(__file__), '..', 'service-account-key.json')
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
            
            self.client = google_storage.Client()
            self.bucket_name = "steganography-app-bucket"
            self.bucket = self.client.bucket(self.bucket_name)
        except Exception as e:
            raise AttributeError(f"Failed to initialize storage client: {str(e)}")

    def check_storage_status(self):
        try:
            # Test if we can list buckets (tests authentication)
            self.client.list_buckets(max_results=1)
            
            # Test if the specified bucket exists and is accessible
            if self.bucket.exists():
                return {
                    'status': 'connected',
                    'bucket_exists': True,
                    'bucket_name': self.bucket_name
                }
            else:
                return {
                    'status': 'connected',
                    'bucket_exists': False,
                    'bucket_name': self.bucket_name,
                    'error': 'Bucket does not exist'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def upload_file(self, file_path, user_id):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        destination_blob_name = f"user_{user_id}/{timestamp}_{os.path.basename(file_path)}"
        blob = self.bucket.blob(destination_blob_name)
        
        blob.upload_from_filename(file_path)
        return blob.public_url

    def download_file(self, blob_name, destination_file_name):
        blob = self.bucket.blob(blob_name)
        blob.download_to_filename(destination_file_name)

# Remove or comment these lines
# storage = CloudStorage()
# status = storage.check_storage_status()
# print(status)