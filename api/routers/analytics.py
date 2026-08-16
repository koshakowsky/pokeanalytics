from typing import Literal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from auth import require_tier
from database import get_db
from schemas import CategoryStat, TypeDistribution, GenerationStats
from services.analytics_service import (
    get_category_analysis,
    get_type_distribution,
    get_stat_ranges,
    get_generation_stats,
)

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

# The analytical dashboards are premium; declared per-route so stat-ranges can
# stay public (the search-filter sliders on the public page depend on it).
premium = Depends(require_tier("premium"))


# Literal, not Query(enum=...): the latter only decorates the OpenAPI schema and
# lets any string through, which silently grouped by color instead (BUG-005).
GroupBy = Literal["type", "color", "generation", "habitat", "shape", "growth_rate"]


@router.get("/categories", response_model=list[CategoryStat], dependencies=[premium])
def categories(
    group_by: GroupBy = "type",
    db: Session = Depends(get_db),
):
    return get_category_analysis(db, group_by)


@router.get("/type-distribution", response_model=list[TypeDistribution], dependencies=[premium])
def type_distribution(db: Session = Depends(get_db)):
    return get_type_distribution(db)


@router.get("/stat-ranges")
def stat_ranges(db: Session = Depends(get_db)):
    # Public: feeds the min/max slider bounds on the public search page.
    return get_stat_ranges(db)


@router.get("/generation-stats", response_model=list[GenerationStats], dependencies=[premium])
def generation_stats(db: Session = Depends(get_db)):
    return get_generation_stats(db)