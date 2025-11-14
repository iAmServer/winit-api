from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from enum import Enum


class SearchRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)

    @field_validator('first_name', 'last_name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty or whitespace only')
        return v.strip()
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "first_name": "John",
                "last_name": "Smith"
            }
        }
    }


class PartyRole(str, Enum):
    PLAINTIFF = "Plaintiff"
    DEFENDANT = "Defendant"
    PETITIONER = "Petitioner"
    RESPONDENT = "Respondent"
    APPELLANT = "Appellant"
    APPELLEE = "Appellee"
    OTHER = "Other"


class Party(BaseModel):
    first_name: str = Field()
    middle_name: str = Field()
    last_name: str = Field()
    role: PartyRole = Field()

    model_config = {
        "json_schema_extra": {
            "example": {
                "first_name": "John",
                "middle_name": "M.",
                "last_name": "Smith",
                "role": PartyRole.DEFENDANT,
            }
        }
    }


class Hearing(BaseModel):
    date: Optional[str] = Field(None)
    type: Optional[str] = Field(None)
    department: Optional[str] = Field(None)
    judge: Optional[str] = Field(None)
    result: Optional[str] = Field(None)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "date": "2024-03-15 09:00 AM",
                "type": "Arraignment",
                "department": "Dept 12",
                "judge": "Hon. Jane Johnson",
                "result": "Continued to 04/15/2024"
            }
        }
    }


class Financial(BaseModel):
    fines: Optional[float] = Field(None)
    fees: Optional[float] = Field(None)
    balance: Optional[float] = Field(None)
    payments: Optional[float] = Field(None)

    model_config = {
        "json_schema_extra": {
            "example": {
                "fines": 500.00,
                "fees": 150.00,
                "balance": 325.00,
                "payments": 325.00
            }
        }
    }


class SourceMetadata(BaseModel):
    search_url: str = Field(...)
    case_url: Optional[str] = Field(None)
    scrape_timestamp: str = Field(...)
    data_source: str = Field(default="fixture")
    raw_html_path: Optional[str] = Field(None)

    model_config = {
        "json_schema_extra": {
            "example": {
                "search_url": "https://portal.scscourt.org/search",
                "case_url": "https://portal.scscourt.org/case/12345",
                "scrape_timestamp": "2024-11-11T10:30:00Z",
                "data_source": "fixture",
                "raw_html_path": "/fixtures/john_smith_case_12345.html"
            }
        }
    }


class CaseMetadata(BaseModel):
    fixture_available: bool = Field(...)
    fixture_path: Optional[str] = Field(None)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "fixture_available": True,
                "fixture_path": "/fixtures/case_21CR012345.html"
            }
        }
    }


class Case(BaseModel):
    case_number: str = Field()
    filing_date: Optional[str] = Field(None)
    case_type: Optional[str] = Field(None)
    status: Optional[str] = Field(None)
    parties: Optional[int] = Field(None)
    metadata: Optional[CaseMetadata] = Field(None)

    model_config = {
        "json_schema_extra": {
            "example": {
                "case_number": "21CR012345",
                "filing_date": "2021-05-15",
                "case_type": "Criminal",
                "status": "Active",
                "parties": 3,
                "metadata": {
                    "fixture_available": True,
                    "fixture_path": "/fixtures/case_21CR012345.html"
                }
            }
        }
    }

        
class Event(BaseModel):
    file_date: str = Field()
    file_type: str = Field()
    filed_by: Optional[str] = Field(None)
    comment: Optional[str] = Field(None)
    has_documents: bool = Field(False)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "file_date": "2024-02-15",
                "file_type": "Motion",
                "filed_by": "Jane Doe",
                "comment": "Request for continuance",
                "has_documents": True
            }
        }
    }


class Attorney(BaseModel):
    first_name: str = Field()
    middle_name: str = Field()
    last_name: str = Field()
    representing: str = Field()
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "first_name": "Jane",
                "middle_name": "A.",
                "last_name": "Doe",
                "representing": "John Smith"
            }
        }
    }


class CaseDetail(BaseModel):
    case_number: str = Field()
    case_caption: str = Field(None)
    filing_date: str = Field(None)
    case_type: str = Field(None)
    status: str = Field(None)
    court_location: str = Field(None)
    parties: List[Party] = Field(default_factory=list)
    attorneys: List[Attorney] = Field(default_factory=list)
    hearings: List[Hearing] = Field(default_factory=list)
    events: List[Event] = Field(default_factory=list)
    financials: Optional[Financial] = Field(None)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "case_number": "21CR012345",
                "case_caption": "People of California vs. John Smith",
                "filing_date": "2021-05-15",
                "case_type": "Criminal",
                "status": "Active",
                "court_location": "Hall of Justice",
                "parties": [
                   {
                       "first_name": "John",
                       "middle_name": "M.",
                       "last_name": "Smith",
                       "role": "Defendant",
                   }
                ],
                "attorneys": [
                    {
                        "first_name": "Jane",
                        "middle_name": "A.",
                        "last_name": "Doe",
                        "representing": "John Smith"
                    }
                ],
                "hearings": [
                    {
                        "date": "2024-03-15 09:00 AM",
                        "type": "Arraignment",
                        "department": "Dept 12",
                        "judge": "Hon. Jane Johnson",
                        "result": "Continued"
                    }
                ],
                "events": [
                    {
                        "file_date": "2024-02-15",
                        "file_type": "Motion",
                        "filed_by": "Jane Doe",
                        "comment": "Request for continuance",
                        "has_documents": True
                    }
                ],
                "financials": None
            }
        }
    }


class SearchResponse(BaseModel):
    query: SearchRequest = Field()
    total_results: int = Field()
    current_page: int = Field()
    total_pages: int = Field()
    cases: List[Case] = Field()
    metadata: SourceMetadata = Field()
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "query": {
                    "firstName": "John",
                    "lastName": "Smith"
                },
                "total_results": 2,
                "current_page": 1,
                "total_pages": 1,
                "cases": [
                    {
                        "case_number": "21CR012345",
                        "filing_date": "2021-05-15",
                        "case_type": "Criminal",
                        "status": "Active",
                        "parties": 3,
                        "metadata": {
                            "fixture_available": True,
                            "fixture_path": "/fixtures/case_21CR012345.html"
                        }
                    }
                ],
                "metadata": {
                    "search_url": "https://portal.scscourt.org/search",
                    "scrape_timestamp": "2024-11-11T10:30:00Z",
                    "data_source": "fixture"
                }
            }
        }
    }

    