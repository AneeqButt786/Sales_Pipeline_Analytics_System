from agents import function_tool
from .models import SalesFunnel

@function_tool
async def get_funnel_status(context: SalesFunnel) -> str:
    metrices = await context.get_metrices()
    result = f"Sales Funnel Status:\nTotal Deals: {metrices['total']}\nTotal Value: {metrices['value']:,.2f}\n\n"
    if metrices['stages']:
        for stage, count in metrices['stages'].items():
            result += f"- {stage}: {count} deals\n"
    return result

@function_tool
async def get_recommendations(context: SalesFunnel) -> str:
    metrics = await context.get_metrices()
    if context.is_enterprise_plan:
        return f"Enterprise: {metrics['total']} deals. Focus on high-value opportunities."
    return f"Basic: {metrics['total']} deals. Focus on quick wins."
