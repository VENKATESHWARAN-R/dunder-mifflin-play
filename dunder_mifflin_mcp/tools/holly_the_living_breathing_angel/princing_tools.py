"""
This module will contain the tools for Holly, the living breathing angel.
"""

from typing import Dict, Any

from dunder_mifflin_mcp.db.client import ORMDBClient
from dunder_mifflin_mcp.db.models import Agent, ModelPricing
from dunder_mifflin_mcp.config import settings


class PricingTools:
    """
    A class that provides tools for managing agent hierarchy and pricing information.
    """

    @staticmethod
    def get_agent_hierarchy(parent_agent_name: str) -> Dict[str, Any]:
        """
        Retrieve the given agent and all its direct sub-agents.
        """
        try:
            with ORMDBClient(settings.common.agents_database_url) as db:
                rows = db.list(Agent, parent_agent_name=parent_agent_name)
                results = [
                    {
                        "id": a.id,
                        "name": a.name,
                        "parent_agent_name": a.parent_agent_name,
                        "model": a.model,
                        "is_agent": a.is_agent,
                        "created_at": a.created_at.isoformat(),
                        "updated_at": a.updated_at.isoformat(),
                    }
                    for a in rows
                ]
            return {
                "status": "success",
                "message": f"{len(results)} agents found",
                "results": results,
            }
        except Exception as e:
            return {"status": "error", "message": str(e), "results": []}

    @staticmethod
    def get_model_pricing(model_name: str) -> Dict[str, Any]:
        """
        Retrieve pricing info for a given model.
        """
        try:
            with ORMDBClient(settings.common.agents_database_url) as db:
                mp = db.get(ModelPricing, model_name)
                if not mp:
                    return {"status": "error", "message": "Model not found", "results": {}}
                res = {
                    "model": mp.model,
                    "optimized_for": mp.optimized_for,
                    "text_input_price": float(mp.text_input_price),
                    "text_output_price": float(mp.text_output_price),
                }
            return {"status": "success", "message": "Pricing retrieved", "results": res}
        except Exception as e:
            return {"status": "error", "message": str(e), "results": {}}

    @staticmethod
    def list_available_models() -> Dict[str, Any]:
        """
        List all currently defined models.
        """
        try:
            with ORMDBClient(settings.common.agents_database_url) as db:
                all_models = db.list(ModelPricing)
                results = [
                    {
                        "model": m.model,
                        "optimized_for": m.optimized_for,
                        "text_input_price": float(m.text_input_price),
                        "text_output_price": float(m.text_output_price),
                    }
                    for m in all_models
                ]
            return {
                "status": "success",
                "message": f"{len(results)} models found",
                "results": results,
            }
        except Exception as e:
            return {"status": "error", "message": str(e), "results": []}

    @staticmethod
    def compare_model_cost(
        agent_name: str, new_model: str, sample_tokens: int
    ) -> Dict[str, Any]:
        """
        Compare the cost of the agent's current model vs. a new one over a sample token usage.
        """
        try:
            with ORMDBClient(settings.common.agents_database_url) as db:
                agent = db.session.query(Agent).filter_by(name=agent_name).one_or_none()
                if not agent:
                    return {"status": "error", "message": "Agent not found", "results": {}}

                current = db.get(ModelPricing, agent.model)
                candidate = db.get(ModelPricing, new_model)
                if not current or not candidate:
                    return {
                        "status": "error",
                        "message": "Model(s) not found",
                        "results": {},
                    }

                # cost per 1K tokens
                current_cost = float(
                    (current.text_input_price + current.text_output_price)
                    * (sample_tokens / 1000)
                )
                new_cost = float(
                    (candidate.text_input_price + candidate.text_output_price)
                    * (sample_tokens / 1000)
                )
                diff = new_cost - current_cost

            return {
                "status": "success",
                "message": "Comparison complete",
                "results": {
                    "current_model": current.model,
                    "new_model": candidate.model,
                    "current_cost": current_cost,
                    "new_cost": new_cost,
                    "difference": diff,
                },
            }
        except Exception as e:
            return {"status": "error", "message": str(e), "results": {}}
        
    @staticmethod
    def get_agent_info(name: str) -> Dict[str, Any]:
        """
        Retrieve a single agent's full record by its name.
        
        Args:
            name: the exact agent name (e.g. "michael_the_magic").
        
        Returns:
            {
            "status": "success" | "error",
            "message": str,
            "results": {
                "id": int,
                "name": str,
                "parent_agent_name": str,
                "model": str,
                "is_agent": bool,
                "created_at": str,
                "updated_at": str
            } | {}
            }
        """
        try:
            with ORMDBClient(settings.common.agents_database_url) as db:
                agent = db.session.query(Agent).filter_by(name=name).one_or_none()
                if not agent:
                    return {"status": "error", "message": "Agent not found", "results": {}}
                res = {
                    "id": agent.id,
                    "name": agent.name,
                    "parent_agent_name": agent.parent_agent_name,
                    "model": agent.model,
                    "is_agent": agent.is_agent,
                    "created_at": agent.created_at.isoformat(),
                    "updated_at": agent.updated_at.isoformat()
                }
            return {"status": "success", "message": "Agent retrieved", "results": res}
        except Exception as e:
            return {"status": "error", "message": str(e), "results": {}}
