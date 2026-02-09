from agents import Agent
from services.models import SalesFunnel
from services.tools import get_funnel_status, get_recommendations

sales_funnel_agent = Agent[SalesFunnel](
    name="Sales Funnel Agent",
    instructions="Use get_funnel_status then get_recommendations for every query.",
    tools=[get_funnel_status, get_recommendations],
    model="gpt-4o-mini",
)
