from typing import Generic, TypeVar, List, Dict, Any, Optional
from pydantic import BaseModel

T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Paginated response model with metadata
    """
    items: List[T]
    total: int
    page: int
    size: int
    pages: int


def paginate(
    items: List[Any],
    total: int,
    page: int = 1,
    size: int = 10
) -> Dict[str, Any]:
    """
    Create a paginated response with metadata
    """
    pages = (total + size - 1) // size  # Ceiling division
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": pages
    }


def get_pagination_params(
    page: int = 1,
    size: int = 10
) -> Dict[str, int]:
    """
    Get skip and limit parameters for pagination
    """
    if page < 1:
        page = 1
    if size < 1:
        size = 10
    if size > 100:
        size = 100
        
    skip = (page - 1) * size
    
    return {
        "skip": skip,
        "limit": size
    }
