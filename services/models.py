from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime, timedelta
from enum import Enum

class FunnelStage(Enum):
    LEAD = "Lead"
    PROSPECT = "Prospect"
    OPPORTUNITY = "Opportunity"
    NEGOTIATION = "Negotiation"
    CLOSED_WON = "Closed Won"
    CLOSED_LOST = "Closed Lost"

@dataclass
class Deal:
    id: str
    name: str
    company: str
    value: float
    stage: FunnelStage
    created_at: str
    last_updated: str
    probability: float
    owner: str

@dataclass
class SalesFunnel:
    team_id: str
    deals: List[Deal]
    is_enterprise_plan: bool

    async def get_metrices(self) -> Dict:
        total_deals = len(self.deals)
        if total_deals == 0:
            return {"total": 0, "value": 0, "stages": {}}
        total_value = sum(deal.value for deal in self.deals)
        stage_count = {}
        for stage in FunnelStage:
            count = sum(1 for deal in self.deals if deal.stage == stage)
            if count > 0:
                stage_count[stage.value] = count
        return {"total": total_deals, "value": total_value, "stages": stage_count}
