import os
import tempfile
import zipfile
from pathlib import Path
from typing import Union

import boto3
import botocore
import botocore.config
from loguru import logger

from src.slack_integrations_offline.config import settings


class S3Client:
    """Client for interacting with AWS S3 storage for file operations.
    
    Handles uploading folders as zip archives, bucket management, and presigned URL generation.
    
    Attributes:
        bucket_name: Name of the S3 bucket to interact with.
        region: AWS region for the S3 bucket.
        no_sign_request: Whether to use unsigned requests for public buckets.
        s3_client: Boto3 S3 client instance for API operations.
    """

    def __init__(
        self,
        bucket_name: str, 
        no_sign_request: bool = False,
        region: str = settings.AWS_DEFAULT_REGION,
    ) -> None:
        
        self.bucket_name = bucket_name
        self.region = region
        self.no_sign_request = no_sign_request

        if no_sign_request:
            # Use unsigned mode for public buckets
            self.s3_client = boto3.client(
                "s3",
                region_name = self.region,
                config = botocore.config.Config(signature_version=botocore.UNSIGNED)

            )

        else:
            # Default authenticated S3 client (using AWS cred)
            self.s3_client = boto3.client(
            "s3", 
            region_name = self.region,
            aws_access_key_id = settings.AWS_ACCESS_KEY,
            aws_secret_access_key = settings.AWS_SECRET_KEY,
            )

    
    def upload_folder(self, local_path: Union[str, Path], s3_prefix: str = "") -> str:
        """Upload a local folder to S3 as a compressed zip archive.
    
        Args:
            local_path: Path to the local folder to upload.
            s3_prefix: S3 prefix path where the zip file will be stored.
        
        Returns:
            str: S3 key path of the uploaded zip file.
        """
        
        # Ensure bucket exists before proceeding
        self.__create_bucket_if_doesnt_exist()

        local_path = Path(local_path)

        if not local_path.exists():
            raise FileNotFoundError(f"Local path does not exist: {local_path}")
        
        if not local_path.is_dir():
            raise NotADirectoryError(f"Local path is not a directory: {local_path}")
        

        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_zip:
            with zipfile.ZipFile(temp_zip.name, "w", zipfile.ZIP_DEFLATED) as zip_file:
                # walk through all files in the directory 
                for root, _, files in os.walk(local_path):
                    for file_name in files:
                        file_path = Path(root) / file_name
                    
                        zip_file.write(file_path, file_path.relative_to(local_path))


            zip_filename = f"{local_path.name}.zip"
            s3_key = f"{s3_prefix.rstrip('/')}/{zip_filename}".lstrip("/")

            logger.debug(
                f"Uploading {local_path} to {self.bucket_name} with key {s3_key}"
            )

            self.s3_client.upload_file(
                temp_zip.name, 
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ACL': 'public-read',
                }
            )

        # clean up temporary zip file
        os.unlink(temp_zip.name)
        return s3_key


    def __create_bucket_if_doesnt_exist(self) -> None:
        """Check if the S3 bucket exists and create it if it doesn't.
    
        Returns:
            None
        
        Raises:
            Exception: If bucket creation fails or access is denied.
        """

        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)

        except self.s3_client.exceptions.ClientError as e:
            error_code = e.response["Error"]["Code"]

            if error_code == "404":
                try:
                    self.s3_client.create_bucket(
                        Bucket = self.bucket_name,
                    )
                except self.s3_client.exceptions.ClientError as create_error:
                    raise Exception(
                        f"Failed to create bucket {self.bucket_name}: {str(create_error)}"
                    )
            elif error_code == "403":
                raise Exception(f"No permission to access bucket {self.bucket_name}")
            else:
                raise


    def get_public_url(self, s3_key: str) -> str:
        """Constructs the public URL for the object."""
        
        url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
        
        logger.info(f"Generated public URL: {url}")
        return url


