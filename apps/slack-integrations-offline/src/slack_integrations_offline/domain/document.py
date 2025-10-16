import json

from pathlib import Path
from pydantic import BaseModel, Field

from src.slack_integrations_offline.utils import generate_random_hex


class DocumentMetadata(BaseModel):
    id: str
    url: str
    title: str
    properties: dict


class Document(BaseModel):
    id: str = Field(default_factory=lambda: generate_random_hex(length=32))
    metadata: DocumentMetadata
    content: str
    summary: str | None = None
    content_quality_score: float | None = None
    child_urls: list[str] = Field(default_factory=list)

    @classmethod
    def from_file(cls, file_path: Path) -> "Document":

        json_data = file_path.read_text(encoding="utf-8")

        return cls.model_validate_json(json_data)


    def write(
        self, output_dir: Path, also_save_as_txt: bool = False,
    ) -> None:
        
        json_page = self.model_dump()

        output_file = output_dir/f"{self.id}.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(
                json_page,
                f,
                indent=4,
                ensure_ascii=False,
            )

        if also_save_as_txt:
            txt_path = output_file.with_suffix(".txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(self.content)

        


    def __eq__(self, other: object) -> bool:
        
        if not isinstance(other, Document):
            return False
        return self.id == other.id
    

    def __hash__(self) -> int:

        return hash(self.id)