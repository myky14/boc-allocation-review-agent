from boc_agent.runtime.context import RuntimeContext

class ResponseBuilder:
    def build_response(self, context: RuntimeContext, raw_result: str) -> str:
        """Converts the raw execution result into the final user-facing response string."""
        context.trace_builder.start_stage("formatter")
        context.add_trace("ResponseBuilder: Packaging final response.")

        # Add reasoning step for formatting
        context.trace_builder.add_reasoning_step(
            stage="Formatter",
            action="Apply Formatting Templates",
            note=f"Formatting raw result of length {len(raw_result)} chars"
        )

        final_response = raw_result

        # If the intent requires grounding, ensure the grounding policy disclaimer is appended.
        if context.skill and context.intent == "rag":
            policy = context.skill.grounding_policy
            if policy.required_disclaimer and policy.required_disclaimer not in final_response:
                final_response += f"\n\n---\n{policy.required_disclaimer}"

            for protocol in getattr(policy, "omit_protocols", []):
                final_response = final_response.replace(protocol, "")

        # Add final confidence snapshot
        context.trace_builder.add_confidence_snapshot(
            stage="Formatter",
            confidence=1.00,
            note="Formatting complete and finalized response ready"
        )

        context.add_trace("ResponseBuilder: Final response packaging complete.")
        context.trace_builder.end_stage("formatter")
        return final_response
