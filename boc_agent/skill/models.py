from typing import List, Dict, Optional, Union
from pydantic import BaseModel, Field

class SkillMetadata(BaseModel):
    name: str
    version: str
    description: str
    role: str

class ToolDefinition(BaseModel):
    name: str
    intents: List[str]
    mutating: bool = False
    required_dataframe: bool = True
    required_grounding: bool = False

class RefusalRule(BaseModel):
    matches: List[str]
    refusal_response: str

class GroundingPolicy(BaseModel):
    strict_grounding: bool = True
    omit_protocols: List[str] = Field(default_factory=list)
    path_style: str = "relative"
    required_disclaimer: str

class Skill(BaseModel):
    metadata: SkillMetadata
    capabilities: List[Union[str, Dict[str, str]]] = Field(default_factory=list)
    non_capabilities: List[Union[str, Dict[str, str]]] = Field(default_factory=list)
    tools: List[ToolDefinition] = Field(default_factory=list)
    refusal_rules: List[RefusalRule] = Field(default_factory=list)
    grounding_policy: GroundingPolicy
