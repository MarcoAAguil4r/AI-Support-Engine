from enum import Enum

from pydantic import BaseModel, Field, field_validator


class Category(str, Enum):
    ACCESS = "ACCESS"
    BUG = "BUG"
    FEATURE = "FEATURE"
    SECURITY = "SECURITY"


class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Mode(str, Enum):
    traditional = "traditional"
    generative = "generative"


class AnalyzeRequest(BaseModel):
    message: str = Field(min_length=1, max_length=5000)
    mode: Mode

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("message must contain non-whitespace characters")
        return value.strip()


class AnalyzeResponse(BaseModel):
    category: Category
    priority: Priority
    response: str = Field(min_length=1)
    requiresHumanReview: bool
    mode: Mode

    @field_validator("response")
    @classmethod
    def response_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("response must contain non-whitespace characters")
        return value.strip()
