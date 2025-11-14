import os
import logging
from datetime import datetime, timezone
from typing import List, Optional
from pathlib import Path

from models.schemas import Case, CaseMetadata, CaseDetail, SearchRequest, SearchResponse, SourceMetadata
from utils.parser import case_record_parser

logger = logging.getLogger(__name__)
SEARCH_URL = "https://portal.scscourt.org/search"


class SearchService:
    def __init__(self):
        self.mode = os.getenv("USE_FIXTURES", "true").lower() == "true"
        self.fixtures_dir = Path("fixtures")
                
        if self.mode and not self.fixtures_dir.exists():
            logger.warning(f"Fixtures directory not found: {self.fixtures_dir}")
    
    def get_mode(self) -> str:
        return "fixture" if self.mode else "live"
    
    def has_fixtures(self) -> bool:
        return self.fixtures_dir.exists() and any(self.fixtures_dir.iterdir())

    async def search(self, first_name: str, last_name: str, page: int = 1, page_size: int = 10) -> SearchResponse:
        if self.mode:
            return await self._search_fixtures(first_name, last_name, page, page_size)
        else:
            return await self._search_live(first_name, last_name, page, page_size)
        
    async def get_case_detail(self, case_number: str) -> Optional[CaseDetail]:
        if self.mode:
            return await self._get_case_detail_fixture(case_number)
        else:
            return await self._get_case_detail_live(case_number)

    async def _search_fixtures(self, first_name: str, last_name: str, page: int, page_size: int) -> SearchResponse:
        fixture_name: str = f"{first_name.lower()}_{last_name.lower()}"
        search_file: Path = self.fixtures_dir / f"{fixture_name}_search.html"
        response_time: str = datetime.now(timezone.utc).isoformat()
        
        if not search_file.exists():
            return SearchResponse(
                query=SearchRequest(first_name=first_name, last_name=last_name),
                total_results=0,
                current_page=page,
                total_pages=0,
                cases=[],
                metadata=SourceMetadata(
                    search_url=SEARCH_URL,
                    scrape_timestamp=response_time,
                    data_source="fixture",
                    raw_html_path=None
                )
            )
                    
        html_content: str = search_file.read_text(encoding='utf-8')
        cases: List[Case] = case_record_parser.parse_search_results(html_content)
        enriched_cases: List[Case] = []
        
        for case in cases:
            case_file: Path = self.fixtures_dir / f"case_{case.case_number}.html"
            
            if case_file.exists():
                case.metadata = CaseMetadata(
                    fixture_available=True,
                    raw_html_path=case_file.as_posix()
                )

            enriched_cases.append(case)
        
        total_results: int = len(enriched_cases)
        start_idx: int = (page - 1) * page_size
        end_idx: int = start_idx + page_size
        enriched_cases: List[Case] = enriched_cases[start_idx:end_idx]
        
        return SearchResponse(
            query=SearchRequest(first_name=first_name, last_name=last_name),
            total_results=total_results,
            current_page=page,
            total_pages=(total_results + page_size - 1) // page_size,
            cases=enriched_cases,
            metadata=SourceMetadata(
                search_url=SEARCH_URL,
                scrape_timestamp=response_time,
                data_source="fixture",
                raw_html_path=str(search_file)
            )
        )

    async def _search_live(self, first_name: str, last_name: str, page: int, page_size: int) -> SearchResponse:
        raise NotImplementedError(
            "Live mode requires CAPTCHA solution and legal authorization."
        )
    
    async def _get_case_detail_fixture(self, case_number: str) -> Optional[CaseDetail]:
        case_file: Path = self.fixtures_dir / f"case_{case_number}.html"
        
        if not case_file.exists():
            return None
        
        try:
            html_content = case_file.read_text(encoding='utf-8')
            return case_record_parser.parse_case_detail(html_content, case_number)
        except Exception:
            return None
    
    async def _get_case_detail_live(self, case_number: str) -> Optional[CaseDetail]:
        raise NotImplementedError(
            "Live mode requires CAPTCHA solution and legal authorization."
        )
        
search_service = SearchService()