from fastapi import APIRouter

from app.schemas import NewsParseRequest, NewsParseResponse
from app.services.news_parser import NewsParser

router = APIRouter()


@router.post("/news/parse", response_model=NewsParseResponse)
def parse_news(request: NewsParseRequest) -> NewsParseResponse:
    return NewsParser().parse(request)
