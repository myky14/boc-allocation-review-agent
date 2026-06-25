from boc_agent.runtime.context import RuntimeContext

class ResponseBuilder:
    def build_response(self, context: RuntimeContext, raw_result: str) -> str:
        """Converts the raw execution result into the final user-facing response string."""
        context.add_trace("ResponseBuilder: Packaging final response.")
        
        final_response = raw_result
        
        # If the intent requires grounding, ensure the grounding policy disclaimer is appended.
        if context.skill and context.intent == "rag":
            policy = context.skill.grounding_policy
            if policy.required_disclaimer and policy.required_disclaimer not in final_response:
                final_response += f"\n\n---\n{policy.required_disclaimer}"
                
            for protocol in getattr(policy, "omit_protocols", []):
                final_response = final_response.replace(protocol, "")
                
        context.add_trace("ResponseBuilder: Final response packaging complete.")
        return final_response
