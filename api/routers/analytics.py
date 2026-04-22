from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from schemas import CategoryStat, TypeDistribution, GenerationStats
from services.analytics_service import (
    get_category_analysis,
    get_type_distribution,
    get_stat_ranges,
    get_generation_stats,
)

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/categories", response_model=list[CategoryStat])
def categories(
    group_by: str = Query("type", enum=["type", "color", "generation", "habitat", "shape", "growth_rate"]),
    db: Session = Depends(get_db),
):
    return get_category_analysis(db, group_by)


@router.get("/type-distribution", response_model=list[TypeDistribution])
def type_distribution(db: Session = Depends(get_db)):
    return get_type_distribution(db)


@router.get("/stat-ranges")
def stat_ranges(db: Session = Depends(get_db)):
    return get_stat_ranges(db)


@router.get("/generation-stats", response_model=list[GenerationStats])
def generation_stats(db: Session = Depends(get_db)):
    return get_generation_stats(db)