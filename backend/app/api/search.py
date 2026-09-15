from fastapi import (
    APIRouter,
    HTTPException,
)

from backend.app.schemas.search import (
    ContractSearchRequest,
)

from backend.app.services.vector_search import (
    vector_search,
)


router = APIRouter(
    prefix="/api/search",
    tags=["Semantic Search"],
)


@router.post("")
def search_contract(
    request: ContractSearchRequest,
):
    try:
        results = vector_search.search(
            query=request.query,
            contract_id=request.contract_id,
            top_k=request.top_k,
        )

        return {
            "contract_id":
                request.contract_id,

            "query":
                request.query,

            "result_count":
                len(results),

            "results":
                results,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )