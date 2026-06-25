import pandas as pd
from typing import Optional
from boc_agent.runtime.context import RuntimeContext
from boc_agent.runtime.tool_registry import ToolRegistry, RuntimeTool

class Executor:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def execute(self, context: RuntimeContext) -> str:
        """Enforces execution permissions, runs the resolved tool handler, and stores trace info."""
        context.add_trace("Executor: Starting tool resolution and verification.")
        
        # 1. Resolve tool by intent
        intent = context.intent or "unknown"
        tool = self.registry.get_tool_for_intent(intent)
        
        if not tool:
            context.add_trace(f"Executor: No registered tool found for intent '{intent}'. Falling back to unknown.")
            tool = self.registry.get_tool("unknown_fallback")
            if not tool:
                err_msg = "Critical error: unknown fallback tool not registered."
                context.errors.append(err_msg)
                return err_msg

        context.tool_name = tool.name
        context.add_trace(f"Executor: Resolved tool '{tool.name}' for intent '{intent}'.")

        # 2. Check if tool is mutating (should be blocked)
        if tool.mutating:
            denial = f"Tool permission denied: Mutating tool '{tool.name}' is prohibited."
            context.add_trace(f"Executor: Blocked mutating tool '{tool.name}'.")
            context.errors.append(denial)
            return denial

        # 3. Check dataframe requirement
        if tool.requires_dataframe and (context.reviewed_df is None or context.reviewed_df.empty):
            denial = "No reviewed workbook data is currently loaded. Transaction not found / run review first."
            context.add_trace(f"Executor: Blocked execution of '{tool.name}' due to missing DataFrame.")
            context.errors.append(denial)
            return denial

        # 4. Check Skill-aware permissions (must have a valid skill configuration loaded)
        if not context.skill:
            denial = "Skill configuration is unavailable or invalid. Runtime execution has been blocked for safety."
            context.add_trace("Executor: Blocked execution because no Skill configuration is loaded.")
            context.errors.append(denial)
            return denial

        permission_error = self._check_skill_permissions(intent, context)
        if permission_error:
            context.add_trace(f"Executor: Skill permission check failed: {permission_error}")
            context.errors.append(permission_error)
            return permission_error

        # 5. Execute tool handler
        context.add_trace(f"Executor: Invoking handler for tool '{tool.name}'.")
        try:
            # Explicitly verify we are not modifying context.reviewed_df
            result = tool.handler(context)
            context.metadata["raw_response"] = result
            context.add_trace(f"Executor: Successfully executed tool '{tool.name}'.")
            return result
        except Exception as e:
            error_msg = f"Tool execution failed: {str(e)}"
            context.add_trace(f"Executor: Error running tool '{tool.name}': {str(e)}")
            context.errors.append(error_msg)
            return error_msg

    def _check_skill_permissions(self, intent: str, context: RuntimeContext) -> Optional[str]:
        """Validates tool permissions and constraints against loaded Skill policies."""
        skill = context.skill
        if not skill:
            return None

        # Map intents to required tools defined in SKILL.md
        intent_to_tools = {
            "row_explanation": ["classification_tool", "eligibility_tool", "allocation_tool"],
            "ineligible_summary": ["eligibility_tool"],
            "needs_documentation": ["eligibility_tool"],
            "filter_location": ["eligibility_tool"],
            "rag": ["RAG_retriever"]
        }

        required_tools = intent_to_tools.get(intent, [])
        for tool_name in required_tools:
            tool_def = next((t for t in skill.tools if t.name.lower() == tool_name.lower()), None)
            if not tool_def:
                return f"Tool permission denied: {tool_name} is not configured in SKILL.md."

            # Check if intent is permitted by the tool configuration
            if intent not in tool_def.intents:
                if intent == "filter_location" and "ineligible_summary" in tool_def.intents:
                    pass
                else:
                    return f"Tool permission denied: {tool_name} is not permitted for intent '{intent}'."

            # Validate mutating constraint
            if tool_def.mutating:
                return f"Tool permission denied: Mutating tool '{tool_name}' is prohibited."

            # Validate required dataframe constraint
            if tool_def.required_dataframe and (context.reviewed_df is None or context.reviewed_df.empty):
                return f"Tool permission denied: {tool_name} requires a loaded DataFrame."

        return None
