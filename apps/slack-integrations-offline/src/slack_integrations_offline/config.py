from loguru import logger
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8",
    )

    # AWS Configuration
    AWS_ACCESS_KEY: str | None = Field(
        default=None, description="AWS access key for authentication."
    )

    AWS_SECRET_KEY: str | None = Field(
        default=None, description="AWS secret key for authentication."
    )

    AWS_DEFAULT_REGION: str = Field(
        default="us-east-1", description="AWS region for cloud services."
    )

    AWS_S3_BUCKET_NAME: str = Field(
        default="support-public-data",
        description="Name of the S3 bucket for storing application data."
    )

    # OpenAI Configuration
    OPENAI_API_KEY: str = Field(
        description="API key for OpenAI service authentication."
    )

    # Slack Configuration
    SLACK_BOT_TOKEN: str = Field(
        description="Bot token for slack."
    )


    @field_validator("OPENAI_API_KEY")
    @classmethod
    def check_not_empty(cls, value:str, info) -> str:
        if not value or value.strip() == "":
            logger.error(f"{info.field_name} cannot be empty")
            raise ValueError(f"{info.field_name} cannot be empty.")
        
        return value
    

try:
    settings = Settings()

except Exception as e:
    logger.error(f"Failed to load configuration: {e}")
    raise SystemExit(e)