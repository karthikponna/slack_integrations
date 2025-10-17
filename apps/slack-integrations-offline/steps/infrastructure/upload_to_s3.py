from pathlib import Path
import time
from loguru import logger

from typing_extensions import Annotated
from zenml import get_step_context, step

from src.slack_integrations_offline.config import settings
from src.slack_integrations_offline.infrastructure.aws.s3 import S3Client


@step
def upload_to_s3(
    folder_path: Path,
    s3_prefix: str = "",
) -> Annotated[str, "output"]:
    
    time.sleep(1)

    s3_client = S3Client(bucket_name=settings.AWS_S3_BUCKET_NAME)
    s3_key = s3_client.upload_folder(local_path=folder_path, s3_prefix=s3_prefix)

    download_url = s3_client.generate_presigned_url(s3_key=s3_key)
    
    step_context = get_step_context()
    step_context.add_output_metadata(
        output_name="output",
        metadata={
            "folder_path": str(folder_path),
            "s3_prefix": s3_prefix,
            "download_url": download_url,
        }
    )

    logger.info(f"Uploaded to S3: {s3_key}")
    logger.info(f"Download URL: {download_url}")
    return str(folder_path)