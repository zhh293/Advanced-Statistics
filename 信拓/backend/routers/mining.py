"""关联规则挖掘 API"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from models import AssociationRule
from services.mining_engine import run_apriori
from schemas import MiningParams, RuleOut

router = APIRouter(prefix="/api/mining", tags=["关联规则挖掘"])


@router.post("/run")
def execute_mining(params: MiningParams, db: Session = Depends(get_db)):
    """执行 Apriori 关联规则挖掘"""
    rules = run_apriori(db, params.min_support, params.min_confidence)
    return {
        "message": f"挖掘完成，生成 {len(rules)} 条规则",
        "count": len(rules),
        "rules": rules,
    }


@router.get("/rules")
def list_rules(
    sort_by: str = Query("lift", description="排序字段: lift/confidence/support"),
    limit: int = Query(50, ge=1, le=200),
    keyword: str = Query(None, description="过滤含关键词的规则"),
    db: Session = Depends(get_db),
):
    """查询已缓存的关联规则"""
    q = db.query(AssociationRule)

    if keyword:
        q = q.filter(
            (AssociationRule.antecedents.contains(keyword)) |
            (AssociationRule.consequents.contains(keyword))
        )

    sort_col = getattr(AssociationRule, sort_by, AssociationRule.lift)
    rules = q.order_by(sort_col.desc()).limit(limit).all()

    return [RuleOut.model_validate(r) for r in rules]


@router.get("/rules/latest-params")
def get_latest_params(db: Session = Depends(get_db)):
    """获取最近一次挖掘使用的参数"""
    latest = db.query(AssociationRule).order_by(
        AssociationRule.calc_time.desc()
    ).first()
    if latest:
        return {"params": latest.params, "calc_time": latest.calc_time}
    return {"params": None, "calc_time": None}
