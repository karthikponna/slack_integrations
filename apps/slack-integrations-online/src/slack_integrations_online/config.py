from loguru import logger
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8",
    )

    # OpenAI Configuration
    OPENAI_API_KEY: str = Field(
        description="API key for OpenAI service authentication."
    )

    # Slack Configuration
    SLACK_BOT_TOKEN: str = Field(
        description="Bot token for slack."
    )

    SLACK_APP_TOKEN: str = Field(
        description="App token of Socket model for slack."
    )

    # MongoDB Configuration
    MONGODB_DATABASE_NAME: str = Field(
        default="slack_integrations",
        description="Name of the MongoDB database.",
    )

    MONGODB_URI: str = Field(
        default="mongodb://slack:slack@localhost:27017/?directConnection=true", 
        # default="mongodb+srv://karthikponna963_db_user:ccWG3CrTZbWiEhXd@cluster0.yuyvgml.mongodb.net/",
        description="Connection URI for the local MongoDB Atlas instance.",
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