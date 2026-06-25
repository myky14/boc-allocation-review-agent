from typing import Dict, Any, List
from boc_agent.skill.models import Skill, SkillMetadata, ToolDefinition, RefusalRule, GroundingPolicy

VALID_TOOL_NAMES = {"classification_tool", "eligibility_tool", "allocation_tool", "RAG_retriever", "rag_retriever"}

def validate_and_build_skill(frontmatter: Dict[str, Any], sections: Dict[str, Any]) -> Skill:
    """Validates required sections and structures raw dictionaries into a Skill model."""
    
    # 1. Validate required sections
    required_sections = [
        "Objectives",
        "Available Tools",
        "Routing Policies",
        "Refusal Policies",
        "Grounding & Citation Policies"
    ]
    for sec in required_sections:
        if sec not in sections:
            raise ValueError(f"Missing required section in SKILL.md: '{sec}'")

    # 2. Build Metadata
    meta_dict = {
        "name": frontmatter.get("name", ""),
        "version": frontmatter.get("version", ""),
        "description": frontmatter.get("description", ""),
        "role": frontmatter.get("role", "")
    }
    for k, v in meta_dict.items():
        if not v:
            raise ValueError(f"Missing metadata field in SKILL.md: '{k}'")
            
    metadata = SkillMetadata(**meta_dict)

    # 3. Build Tools
    tools_raw = sections.get("Available Tools")
    if not isinstance(tools_raw, list):
        raise ValueError("Section 'Available Tools' must be a YAML list in SKILL.md")
        
    tools: List[ToolDefinition] = []
    for idx, item in enumerate(tools_raw):
        if not isinstance(item, dict):
            raise ValueError(f"Invalid tool definition at index {idx} in SKILL.md")
        name = item.get("Name") or item.get("name")
        if not name:
            raise ValueError(f"Tool at index {idx} is missing a Name")
        if name not in VALID_TOOL_NAMES:
            raise ValueError(f"Invalid tool Name '{name}' in SKILL.md. Valid tools are: {VALID_TOOL_NAMES}")
            
        intents = item.get("Intents")
        if intents is None:
            intents = item.get("intents")
        if not isinstance(intents, list):
            raise ValueError(f"Tool '{name}' must specify a list of Intents")
            
        mutating = item.get("Mutating")
        if mutating is None:
            mutating = item.get("mutating")
        if mutating is None:
            mutating = False
        if mutating:
            raise ValueError(f"Tool '{name}' cannot have mutating=True. Mutating tools are prohibited.")
            
        req_df = item.get("RequiredDataframe")
        if req_df is None:
            req_df = item.get("required_dataframe")
        if req_df is None:
            req_df = True
            
        req_grounding = item.get("RequiredGrounding")
        if req_grounding is None:
            req_grounding = item.get("required_grounding")
        if req_grounding is None:
            req_grounding = False

        tools.append(ToolDefinition(
            name=name,
            intents=intents,
            mutating=mutating,
            required_dataframe=req_df,
            required_grounding=req_grounding
        ))

    # 4. Build Refusal Rules
    refusals_raw = sections.get("Refusal Policies")
    if not isinstance(refusals_raw, list):
        raise ValueError("Section 'Refusal Policies' must be a YAML list in SKILL.md")
        
    refusal_rules: List[RefusalRule] = []
    for idx, item in enumerate(refusals_raw):
        if not isinstance(item, dict):
            raise ValueError(f"Invalid refusal policy at index {idx} in SKILL.md")
        matches = item.get("Matches")
        if matches is None:
            matches = item.get("matches")
        if not isinstance(matches, list) or not matches:
            raise ValueError(f"Refusal policy at index {idx} must specify a list of Matches")
        resp = item.get("RefusalResponse")
        if resp is None:
            resp = item.get("refusal_response")
        if not resp:
            raise ValueError(f"Refusal policy at index {idx} must specify a RefusalResponse")
            
        refusal_rules.append(RefusalRule(
            matches=matches,
            refusal_response=resp
        ))

    # 5. Build Grounding Policy
    grounding_raw = sections.get("Grounding & Citation Policies")
    if not isinstance(grounding_raw, list) or not grounding_raw:
        raise ValueError("Section 'Grounding & Citation Policies' must be a list in SKILL.md")
        
    # Helper to merge grounding policy dicts if it is a list of single-key dicts
    gp_item = {}
    for item in grounding_raw:
        if isinstance(item, dict):
            gp_item.update(item)
        else:
            raise ValueError("Grounding policy item must be a dictionary in SKILL.md")
        
    strict_gr = gp_item.get("StrictGrounding")
    if strict_gr is None:
        strict_gr = gp_item.get("strict_grounding")
    if strict_gr is None:
        strict_gr = True
        
    omit_protocols = gp_item.get("OmitProtocols")
    if omit_protocols is None:
        omit_protocols = gp_item.get("omit_protocols")
    if omit_protocols is None:
        omit_protocols = []
    if not isinstance(omit_protocols, list):
        raise ValueError("OmitProtocols in Grounding policies must be a list of strings")
        
    path_style = gp_item.get("PathStyle")
    if path_style is None:
        path_style = gp_item.get("path_style")
    if path_style is None:
        path_style = "relative"

    disclaimer = gp_item.get("RequiredDisclaimer")
    if disclaimer is None:
        disclaimer = gp_item.get("required_disclaimer")
    if not disclaimer:
        raise ValueError("Grounding policies must specify a RequiredDisclaimer")

    grounding_policy = GroundingPolicy(
        strict_grounding=strict_gr,
        omit_protocols=omit_protocols,
        path_style=path_style,
        required_disclaimer=disclaimer
    )

    caps_raw = frontmatter.get("capabilities", [])
    capabilities = []
    for cap in caps_raw:
        if isinstance(cap, dict):
            capabilities.extend(cap.keys())
        elif isinstance(cap, str):
            capabilities.append(cap)
            
    non_caps_raw = frontmatter.get("non_capabilities", [])
    non_capabilities = []
    for cap in non_caps_raw:
        if isinstance(cap, dict):
            non_capabilities.extend(cap.keys())
        elif isinstance(cap, str):
            non_capabilities.append(cap)

    return Skill(
        metadata=metadata,
        capabilities=capabilities,
        non_capabilities=non_capabilities,
        tools=tools,
        refusal_rules=refusal_rules,
        grounding_policy=grounding_policy
    )
