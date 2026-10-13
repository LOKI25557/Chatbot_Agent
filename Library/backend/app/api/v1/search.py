from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.search import SearchRequest, SearchResponse
from app.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["Search"])


@router.post("", response_model=SearchResponse)
def search_catalogue(request: SearchRequest, db: Session = Depends(get_db)):
    """
    Intelligent library search endpoint.
    Extracts intent, queries real database records, determines availability,
    and returns verified grounded results with an AI conversational explanation.
    """
    return SearchService.execute_search(db=db, request=request)
