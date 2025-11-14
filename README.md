# Winit Take Home Test - Rest API

A FastAPI service for searching and retrieving court records from the Santa Clara County Superior Court public portal.

## Overview

This API provides structured JSON access to court case information:

- Case details
- Party information
- Hearing schedules
- Attorney details
- Source metadata and timestamps

**Note:** Financial information is not included; no data was available in the portal.

## Features

- RESTful API with FastAPI
- Fixture-based mode for testing
- Docker-ready for deployment
- Input validation with Pydantic
- Auto-generated Swagger UI documentation
- Health check endpoints
- CORS support
- Integrated testing with pytest

## Access & Anti-Bot Strategy (Legal and Operational)

### Legal Compliance Assessment

Based on the suggestion in the test intructions recieved I reviewed following to ensure legal compliance:

**Robots.txt Review:**

- Examined `https://santaclara.courts.ca.gov/robots.txt` to identify crawl permissions and I could see all search paths were disallowed.

```
Disallow: /search*search=*
Disallow: /search*search_api_fulltext=*
```

**Terms of Use:**

- Reviewed the terms of use page `https://courts.ca.gov/about/terms-use?` and under section 'Restrictions on Access and Use' and point (ii) it prohibits data mining or use of bots which made it impossible to scrap or try bypassing captcha protections.
  ("Your access to and use of this Website and the Content may be terminated at any time without notice. You may not do any of the following: engage in any data mining, or use "bots" or similar data gathering and extraction tools or methods in connection with this Website or the Content;")

**Public Records Status:**

- Court records are public information by law
- Access is legally permissible for legitimate purposes
- No proprietary or confidential data is being accessed

### Current Access Limitations

The Santa Clara County Superior Court portal implements **CAPTCHA protection on every search type which is tied to user sessions**, which hindered me from implementing live searching capabilities without violating legal and ethical boundaries but I was able to manually collect fixtures for demonstration purposes. No geographic restrictions were bypassed. All access was performed from standard locations without VPNs or proxies.

### Current Mode

- **Fixture Mode (Default)**: `USE_FIXTURES=true`
  Uses manually collected HTML fixtures to simulate search and case detail results.

- **Live Mode (Not implemented)**: `USE_FIXTURES=false`
  Requires legal authorization and CAPTCHA handling to run safely.

### Security Protections - Compliance Statement

**I affirm that:**

1. No security protections were bypassed or defeated
2. No CAPTCHA circumvention techniques were employed
3. No web application firewall (WAF) evasion was attempted
4. No rate limiting or access controls were circumvented
5. All fixture data was collected through legitimate manual access
6. The implementation respects all technical and legal boundaries

### Summary

I didn't violate any legal or ethical boundaries implementing this solution. The fixture-based approach proves data can extracted, parsed, and structured effectively.

## Quick Start

### With Docker

```bash
git clone git@github.com:iAmServer/winit-api.git
cd winit-api
docker-compose up --build
# Access API at http://localhost:8000
```

### Locally

```bash
git clone git@github.com:iAmServer/winit-api.git
cd winit-api
poetry install
python main.py
```

### Test Requests

```bash
curl http://localhost:8000/health

curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"first_name": "John", "last_name": "Smith"}'
```

## API Endpoints

### `GET /` - Root

Returns basic service status.

### `GET /health` - Health Check

Returns mode, fixture availability, and timestamp.

### `POST /api/search` - Search Cases

Search by first and last name. Supports pagination with `page` and `page_size`.

**Example Request:**

```json
{
  "first_name": "John",
  "last_name": "Smith"
}
```

**Example Response:**

```json
{
  "query": { "first_name": "John", "last_name": "Smith" },
  "total_results": 100,
  "cases": [
    {
      "case_number": "25TR080266",
      "filing_date": "11/5/2025",
      "case_type": "Adult Traffic",
      "status": "Closed",
      "metadata": { "fixture_available": true }
    }
  ]
}
```

### `GET /api/case/{case_number}` - Case Detail

Retrieve details for a specific case by `case_number`.

**Response Example:**

```json
{
  "case_number": "C2502897",
  "case_caption": "THE PEOPLE OF THE STATE OF CALIFORNIA vs. GARCIA, JOSE LUIS",
  "filing_date": "2025-02-26",
  "case_type": "Complaint - Misdemeanor",
  "status": "Sentenced",
  "court_location": "Hall of Justice",
  "parties": [
    { "first_name": "JOSE", "last_name": "GARCIA", "role": "Defendant" }
  ],
  "attorneys": [
    { "last_name": "Public Defender", "representing": "JOSE LUIS GARCIA" }
  ]
}
```

## Testing

Run tests locally or in Docker:

```bash
# Docker
docker-compose exec api python -m pytest -v

# Local
pytest -v
```

Tests cover:

- API endpoints
- Input validation
- Schema validation

## Project Structure

```
winit/
├── main.py
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── models/schemas.py
├── services/search.py
├── utils/parser.py
├── tests/test_api.py
└── fixtures/
```

## Adding New Fixtures

1. Visit https://portal.scscourt.org/search
2. Complete CAPTCHA
3. Search for name
4. Inspect -> Copy -> Outer HTML
5. Save to fixtures/firstname_lastname_search.html
6. Click on case link
7. Inspect -> Copy -> Outer HTML
8. Save to fixtures/case_CASENUMBER.html

## Future Enhancements

- Database integration for historical data
- Filtering and sorting
- PDF/CSV export
- Rate limiting
- Background jobs

## Author

**Joshua Egbeyemi**
GitHub: [iAmServer](https://github.com/iAmServer)
