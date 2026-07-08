from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.mysql import get_db
from app.models.strategy import ShorteningStrategy
from app.schemas.strategy_schema import StrategyCreate, StrategyResponse

router = APIRouter(prefix="/api/v1/strategies", tags=["Shortening Strategies"])


@router.post("", response_model=StrategyResponse, status_code=status.HTTP_201_CREATED)
def create_strategy(payload: StrategyCreate, db: Session = Depends(get_db)) -> ShorteningStrategy:
    strategy = ShorteningStrategy(
        name=payload.name,
        output_length=payload.output_length,
        description=payload.description,
    )
    db.add(strategy)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="strategy name already exists") from exc
    db.refresh(strategy)
    return strategy


@router.get("", response_model=list[StrategyResponse])
def list_strategies(db: Session = Depends(get_db)) -> list[ShorteningStrategy]:
    return db.query(ShorteningStrategy).order_by(ShorteningStrategy.created_at.desc()).all()
