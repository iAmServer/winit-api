import uvicorn
from typing import Optional
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone

from services.search import search_service
from models.schemas import SearchRequest, SearchResponse


app = FastAPI(
    title="Winit",
    description="production-ready API",
    version="1.0.0",
    docs_url="/docs",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get("/", response_model=dict)
def root():
    """ Basic health check """
    return {
        "status": "healthy",
        "service": "Winit",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/health", response_model=dict)
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "mode": search_service.get_mode(),
        "fixtures_available": search_service.has_fixtures(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.post(
    "/api/search",
    response_model=SearchResponse,
    responses={
        200: {"description": "Cases found successfully"},
        204: {"description": "No cases found"},
        400: {"description": "Invalid input"},
        404: {"description": "No matching records"},
        500: {"description": "Internal server error"}
    }
)
async def search_cases(body: SearchRequest, page: Optional[int] = Query(1), page_size: Optional[int] = Query(10)):
    """
    Search for court cases by party name.
    """
    try:
        result = await search_service.search(
            first_name=body.first_name,
            last_name=body.last_name,
            page=page,
            page_size=page_size
        )
        
        if not result.cases:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No cases found for {body.first_name} {body.last_name}"
            )
            
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your request: {str(e)}"
        )


@app.get("/api/case/{case_number}")
async def get_case_detail(case_number: str):
    """
    Get detailed information for a specific case.
    """ 
    try:
        result = await search_service.get_case_detail(case_number)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case {case_number} not found"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving case details: {str(e)}"
        )


if __name__ == "__main__":
    
    uvicorn.run(app, host="0.0.0.0", port=8000)