import os
import logging
# from supabase import create_client, Client
from backend.config import settings

logger = logging.getLogger(__name__)

class StorageManager:
    def __init__(self):
        self.supabase_url = settings.SUPABASE_URL
        self.supabase_key = settings.SUPABASE_KEY
        self.bucket_name = settings.SUPABASE_BUCKET
        self.client = None
        
        # if self.supabase_url and self.supabase_key:
        #     try:
        #         self.client: Client = create_client(self.supabase_url, self.supabase_key)
        #         logger.info("Supabase storage client initialized.")
        #     except Exception as e:
        #         logger.error(f"Failed to initialize Supabase client: {e}")
        #         self.client = None
        # else:
        #     logger.warning("Supabase credentials missing. Cloud storage disabled.")
        #     self.client = None

    async def upload_file(self, file_path: str, destination_path: str):
        """Upload a local file to Supabase storage"""
        if not self.client:
            return False
            
        try:
            with open(file_path, "rb") as f:
                self.client.storage.from_(self.bucket_name).upload(
                    path=destination_path,
                    file=f,
                    file_options={"content-type": "application/octet-stream"}
                )
            return True
        except Exception as e:
            logger.error(f"Supabase upload error: {e}")
            return False

    async def upload_content(self, content: bytes, destination_path: str, content_type: str = "application/octet-stream"):
        """Upload bytes directly to Supabase storage"""
        if not self.client:
            return False
            
        try:
            self.client.storage.from_(self.bucket_name).upload(
                path=destination_path,
                file=content,
                file_options={"content-type": content_type}
            )
            return True
        except Exception as e:
            logger.error(f"Supabase upload error: {e}")
            return False

    def get_public_url(self, file_path: str):
        """Get a public URL for a file"""
        if not self.client:
            return None
        return self.client.storage.from_(self.bucket_name).get_public_url(file_path)

    def download_file(self, storage_path: str, local_path: str):
        """Download a file from storage to local disk"""
        if not self.client:
            return False
            
        try:
            res = self.client.storage.from_(self.bucket_name).download(storage_path)
            with open(local_path, "wb") as f:
                f.write(res)
            return True
        except Exception as e:
            logger.error(f"Supabase download error: {e}")
            return False

storage_manager = StorageManager()
