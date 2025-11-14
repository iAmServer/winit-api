from datetime import datetime
import re
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from models.schemas import Attorney, Case, CaseDetail, CaseMetadata, Event, Hearing, Party


class CourtRecordParser:
    # search results fixture parsing utils
    def parse_search_results(self, html: str) -> List[Case]:
        soup = BeautifulSoup(html, 'html.parser')
        cases = []
        results_table = soup.find('table', id='tblPartySearchResults')
        
        if not results_table:
            results_table = soup.find('table', class_=re.compile(r'dataTable|table-bordered', re.I))
        
        if not results_table:
            return cases
        
        tbody = results_table.find('tbody')
        if not tbody:
            return cases
        
        data_rows = tbody.find_all('tr', role='row')
        
        for row in data_rows:
            try:
                case = self._extract_case_from_datatable_row(row)
                if case:
                    cases.append(case)
            except Exception:
                continue
        
        return cases
    
    def _extract_case_from_datatable_row(self, row) -> Optional[Case]:
        try:
            cells = row.find_all('td')
            
            if len(cells) < 6:
                return None
            
            case_number = cells[1].get_text(strip=True)
            if not case_number:
                return None
            
            case_style = cells[2].get_text(separator=' ', strip=True)
            parties = self._extract_count(case_style)
            status = cells[3].get_text(strip=True)
            case_type = cells[4].get_text(strip=True)
            filing_date = cells[5].get_text(strip=True)
            
            return Case(
                case_number=case_number,
                filing_date=filing_date,
                case_type=case_type,
                status=status,
                parties=parties,
                metadata=CaseMetadata(
                    fixture_available=False,
                    raw_html_path=None
                )
            )
        except Exception:
            return None
    
    def _extract_count(self, case_style: str) -> Optional[int]: 
        parties: Optional[int] = None
        
        if 'XXXX' in case_style or not case_style.strip():
            return parties
        
        if ' vs. ' in case_style:
            parts = case_style.split(' vs. ')
        elif ' vs ' in case_style:
            parts = case_style.split(' vs ')
        elif ' v. ' in case_style:
            parts = case_style.split(' v. ')
        elif ' v ' in case_style:
            parts = case_style.split(' v ')
        else:
            return parties
        
        parties = len(parts)
        
        return parties

    # individual case fixture parsing utils
    def parse_case_detail(self, html: str, case_number: str = None) -> Optional[CaseDetail]:
        soup = BeautifulSoup(html, 'html.parser')
        
        try:
            extracted_case_number = self._extract_case_number_from_header(soup)
            case_number = case_number or extracted_case_number
            case_caption = self._extract_case_caption(soup)
            case_info = self._extract_case_info_from_detail(soup)
            parties = self._extract_parties(soup)
            attorneys = self._extract_attorneys(soup)
            events = self._extract_events(soup)
            hearings = self._extract_hearings(soup)
            financials = None  # I couldn't find financials in the detail or search pages
            
            return CaseDetail(
                case_number=case_number,
                case_caption=case_caption,
                filing_date=case_info.get('filing_date'),
                case_type=case_info.get('case_type'),
                status=case_info.get('status'),
                court_location=case_info.get('court_location'),
                parties=parties,
                attorneys=attorneys,
                hearings=hearings,
                events=events,
                financials=financials
            )
            
        except Exception as e:
            print(f"Error parsing case detail for case {case_number}: {str(e)}")
            return None
    
    def _extract_case_number_from_header(self, soup: BeautifulSoup) -> Optional[str]:
        case_num_element = soup.find('h1', id='caseNumber')
        if case_num_element:
            return case_num_element.get_text(strip=True)
        return None
    
    def _extract_case_caption(self, soup: BeautifulSoup) -> Optional[str]:
        caption_element = soup.find('h3', id='caseCaption')
        if caption_element:
            return caption_element.get_text(strip=True)
        return None
    
    def _extract_case_info_from_detail(self, soup: BeautifulSoup) -> Dict[str, str]:
        info = {}
        case_info_section = soup.find('div', id='info')
        
        if case_info_section:
            case_details = case_info_section.find('div', id='caseinfo1')
            if case_details:
                paragraph = case_details.find('p')
                
                if paragraph:
                    text_parts = []
                    for content in paragraph.contents:
                        if content.name == 'br':
                            continue
                        text = str(content).strip()
                        if text:
                            text_parts.append(text)
                            
                    full_text = ' '.join(text_parts)
                    case_type_match = re.search(r'Case Type:\s*</strong>\s*([^<]+)', full_text)
                    if case_type_match:
                        info['case_type'] = case_type_match.group(1).strip()
                    
                    filing_date_match = re.search(r'Filing Date:</strong>\s*(\d{1,2}/\d{1,2}/\d{4})', full_text)
                    if filing_date_match:
                        info['filing_date'] = self._normalize_date(filing_date_match.group(1))
                    
                    status_match = re.search(r'Case Status:</strong>\s*([^<]+)', full_text)
                    if status_match:
                        info['status'] = status_match.group(1).strip()
                    
                    location_match = re.search(r'Court Location:</strong>\s*([^<]+)', full_text)
                    if location_match:
                        info['court_location'] = location_match.group(1).strip()
        
        return info

    def _extract_parties(self, soup: BeautifulSoup) -> List[Party]:
        parties: List[Party] = []
        parties_tab = soup.find('div', id='parties')
        
        if parties_tab:
            parties_table = parties_tab.find('table')
            
            if parties_table:
                tbody = parties_table.find('tbody')
                
                if tbody:
                    rows = tbody.find_all('tr', role='row')
                    
                    for row in rows:
                        cells = row.find_all('td')
                        
                        if len(cells) == 1:
                            continue
                        
                        if len(cells) >= 4:
                            party_type = cells[0].get_text(strip=True)
                            first_name = cells[1].get_text(strip=True)
                            middle_name = cells[2].get_text(strip=True)
                            last_name = cells[3].get_text(strip=True)

                            if party_type:
                                parties.append(Party(
                                    role=party_type,
                                    first_name=first_name,
                                    middle_name=middle_name,
                                    last_name=last_name
                                ))

        return parties

    def _extract_attorneys(self, soup: BeautifulSoup) -> List[Attorney]:
        attorneys: List[Attorney] = []
        parties_tab = soup.find('div', id='parties')
        
        if parties_tab:
            tables = parties_tab.find_all('table')
            
            if len(tables) >= 2:
                attorneys_table = tables[1]
                tbody = attorneys_table.find('tbody')
                if tbody:
                    rows = tbody.find_all('tr')
                    
                    for row in rows:
                        cells = row.find_all('td')
                        
                        if len(cells) == 1 and 'no data' in cells[0].get_text().lower():
                            continue
                        
                        if len(cells) >= 4:
                            representing = cells[0].get_text(strip=True)
                            first_name = cells[1].get_text(strip=True)
                            middle_name = cells[2].get_text(strip=True)
                            last_name = cells[3].get_text(strip=True)
                            
                            if first_name or last_name:
                                attorneys.append(Attorney(
                                    first_name=first_name,
                                    middle_name=middle_name,
                                    last_name=last_name,
                                    representing=representing
                                ))
        
        return attorneys
    
    def _extract_events(self, soup: BeautifulSoup) -> List[Event]:
        events: List[Event] = []
        events_tab = soup.find('div', id='events')
        
        if events_tab:
            events_table = events_tab.find('table')
            
            if events_table:
                tbody = events_table.find('tbody')
                
                if tbody:
                    rows = tbody.find_all('tr', role='row')
                    
                    for row in rows:
                        cells = row.find_all('td')
                        
                        if len(cells) >= 5:
                            file_date = cells[0].get_text(strip=True)
                            file_type = cells[1].get_text(strip=True)
                            filed_by = cells[2].get_text(strip=True)
                            comment = cells[3].get_text(strip=True)
                            documents_cell = cells[4]
                            has_documents = bool(documents_cell.find('a'))
                            
                            if file_date or file_type:
                                events.append(Event(
                                    file_date=self._normalize_date(file_date),
                                    file_type=file_type,
                                    filed_by=filed_by if filed_by else None,
                                    comment=comment if comment else None,
                                    has_documents=has_documents
                                ))
        
        return events

    def _extract_hearings(self, soup: BeautifulSoup) -> List[Hearing]:
        hearings: List[Hearing] = []
        hearings_tab = soup.find('div', id='hearings')
        
        if hearings_tab:
            hearings_table = hearings_tab.find('table')
            
            if hearings_table:
                tbody = hearings_table.find('tbody')
                
                if tbody:
                    rows = tbody.find_all('tr', role='row')
                    
                    for row in rows:
                        cells = row.find_all('td')
                        
                        if len(cells) >= 6:
                            department = cells[0].get_text(strip=True)
                            hearing_type = cells[1].get_text(strip=True)
                            date = cells[2].get_text(strip=True)
                            time = cells[3].get_text(strip=True)
                            result = cells[4].get_text(strip=True)
                            documents_cell = cells[5]
                            has_documents = bool(documents_cell.find('a'))
                            full_datetime = f"{date} {time}".strip()
                            
                            if date or hearing_type:
                                hearings.append(Hearing(
                                    date=self._normalize_date(date),
                                    time=time,
                                    datetime=full_datetime,
                                    type=hearing_type,
                                    department=department,
                                    result=result,
                                    has_documents=has_documents
                                ))

        return hearings
    
    def _normalize_date(self, date_str: str) -> Optional[str]:
        if not date_str:
            return None
        
        try:
            for fmt in ['%m/%d/%Y', '%m-%d-%Y', '%Y-%m-%d', '%Y/%m/%d']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            return date_str
        except Exception:
            return date_str
        
case_record_parser = CourtRecordParser()
