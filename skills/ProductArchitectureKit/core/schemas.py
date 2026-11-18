"""
schemas.py — Strict Pydantic IPO models for the 6-Phase Execution Pipeline
and Layer 0 Deterministic Design & Typography Governance (`v1.1.0`).
Part of ProductArchitectureKit skill.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

# ============================================================================
# LAYER 0 DESIGN STATE, RULE & TYPOGRAPHY GOVERNANCE CONTRACTS (v1.1.0)
# ============================================================================


class DesignElement(BaseModel):
    """Canonical UI node representation for mechanical Layer 0 inspection."""

    model_config = ConfigDict(extra="allow")

    id: str
    type: str
    props: dict[str, Any] = Field(default_factory=dict)
    styles: dict[str, Any] = Field(default_factory=dict)
    classes: list[str] = Field(default_factory=list)
    font_size_px: float | None = None
    font_family: str | None = None
    allow_mono: bool = False
    children: list[str] = Field(default_factory=list)


class TypographyGovernanceContract(BaseModel):
    """Deterministic typography governance contract (`SPEC-TYPOGRAPHY-001`)."""

    max_font_families: int = 3
    max_scale_steps: int = 8
    min_font_size_px: float = 11.0
    font_families: list[str] = Field(default_factory=list)
    scale_steps_px: list[float] = Field(default_factory=list)
    arbitrary_size_classes: list[str] = Field(default_factory=list)
    mono_button_violations: list[str] = Field(default_factory=list)


class DesignState(BaseModel):
    """Aggregate UI design state evaluated by `Layer0Validator`."""

    model_config = ConfigDict(extra="allow")

    elements: dict[str, DesignElement] = Field(default_factory=dict)
    tokens: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    typography: TypographyGovernanceContract | None = None


class Layer0Rule(BaseModel):
    """Declarative Layer 0 invariant rule evaluated against `DesignState`."""

    id: str
    description: str
    condition: str = "True"
    severity: Literal["ERROR", "WARNING"] = "ERROR"
    law_layer: str = "Layer 0.3 (Micro)"


class Layer0ValidationResult(BaseModel):
    """Result record emitted by `Layer0Validator`."""

    rule_id: str
    passed: bool
    message: str
    severity: Literal["ERROR", "WARNING"] = "ERROR"


# ============================================================================
# PHASE 1: STRATEGIC PRIORITIZATION (BMC ALIGNMENT) — Domain 5: Outcomes
# ============================================================================


class BMCRiskMapOutput(BaseModel):
    bleeding_block: str = Field(
        ...,
        description="Target block of the 9 BMC blocks (e.g., Key Activities, Value Proposition)",
    )
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(
        ..., description="Risk severity"
    )
    affected_stakeholders: list[str] = Field(default_factory=list)
    rationale: str = Field(
        ..., description="Empirical rationale for why this block is bleeding"
    )


class CapabilityDeltaOutput(BaseModel):
    as_is_workflow: str = Field(
        ..., description="Current operational/software workflow"
    )
    to_be_workflow: str = Field(
        ..., description="Target software workflow closing the BMC gap"
    )
    capability_code: str = Field(
        ..., description="Unique capability code, e.g. CAP-TYCRM-042"
    )
    missing_features: list[str] = Field(default_factory=list)


class BaselineDataSheetOutput(BaseModel):
    capability_code: str
    metrics: dict[str, float] = Field(
        default_factory=dict,
        description="Quantitative baselines (drop-off, cost, error rate)",
    )
    sql_queries_used: list[str] = Field(default_factory=list)


class PrioritizedTargetOutput(BaseModel):
    target_id: str
    impact_score: float = Field(..., ge=1.0, le=10.0)
    effort_score: float = Field(..., ge=1.0, le=10.0)
    wsjf_score: float = Field(..., description="Weighted Shortest Job First score")
    selected_target: str


class Tollgate1CharterOutput(BaseModel):
    charter_id: str
    target_capability: str
    cost_of_delay_per_day: float = Field(
        ..., description="Calculated daily financial loss if delayed"
    )
    is_executive_override: bool = False
    status: Literal["SIGNED_CHARTER", "SIGNED_RISK_WAIVER", "REJECTED"]
    signoff_actor: str


class Phase1TruthOutput(BaseModel):
    bmc_risk_map: BMCRiskMapOutput
    capability_delta: CapabilityDeltaOutput
    baseline_data: BaselineDataSheetOutput
    prioritized_target: PrioritizedTargetOutput
    tollgate: Tollgate1CharterOutput


# ============================================================================
# PHASE 2: MARKET FORENSICS & STRUCTURAL AUTOPSY — Domain 1: Truth
# ============================================================================


class EcologicalMappingOutput(BaseModel):
    direct_competitors: list[str] = Field(..., min_length=2, max_length=2)
    adjacent_solutions: list[str] = Field(..., min_length=2, max_length=2)
    graveyard_attempt: str = Field(
        ..., description="Failed historical execution attempt"
    )


class StructuralAutopsyOutput(BaseModel):
    purged_flowcharts: dict[str, list[str]] = Field(default_factory=dict)
    competitor_step_counts: dict[str, int] = Field(default_factory=dict)
    chesterton_fence_notes: list[str] = Field(default_factory=list)
    competitor_tech_debt_identified: list[str] = Field(default_factory=list)


class StandardVsInnovationOutput(BaseModel):
    market_standards_to_adopt: list[str] = Field(default_factory=list)
    innovation_wedge_steps: list[str] = Field(default_factory=list)
    friction_eliminated: list[str] = Field(default_factory=list)


class Tollgate2MarketThesisOutput(BaseModel):
    thesis_id: str
    adopted_market_logic: list[str] = Field(default_factory=list)
    amputated_steps: list[str] = Field(default_factory=list)
    innovation_hypothesis: str
    status: Literal["APPROVED", "REVISE"]


class Phase2MarketForensicsOutput(BaseModel):
    ecological_mapping: EcologicalMappingOutput
    structural_autopsy: StructuralAutopsyOutput
    standard_vs_innovation: StandardVsInnovationOutput
    tollgate: Tollgate2MarketThesisOutput


# ============================================================================
# PHASE 3: CAPABILITY ARCHITECTURE & LOGIC LOCK — Domain 2: Logic
# ============================================================================


class EBQCTelemetrySnapshot(BaseModel):
    """Empirical EBQC telemetry link for an Architectural Decision Record (SPEC-1)."""

    run_id: str = Field(
        ..., min_length=1, description="Originating dream/eval run identifier"
    )
    ebqc_score: float = Field(
        ..., ge=0.0, le=1.0, description="Empirical quality score in [0.0, 1.0]"
    )
    defect_density: float = Field(
        default=0.0, ge=0.0, description="Observed defect rate"
    )
    verified_at: str = Field(..., description="ISO-8601 verification timestamp")


class ADRVersionedRecord(BaseModel):
    """SPEC-1: Versioned Architecture Decision Record schema with EBQC telemetry link (Domain 2: Logic).

    Enforces MECE boundary: ProductArchitectureKit defines pure Pydantic governance schemas
    and delegates Git/DB transport to WorkspaceStateManager.
    """

    adr_id: str = Field(
        ...,
        pattern=r"^ADR-\d{3,5}$",
        description="Canonical ADR identifier, e.g. ADR-0042",
    )
    title: str = Field(..., min_length=5, max_length=200)
    semver: str = Field(
        ..., pattern=r"^\d+\.\d+\.\d+$", description="Semantic version X.Y.Z"
    )
    status: Literal["PROPOSED", "ACCEPTED", "DEPRECATED", "SUPERSEDED"] = Field(
        default="PROPOSED"
    )
    domain: Literal["TRUTH", "LOGIC", "PERCEPTION", "REALITY", "OUTCOMES"] = Field(
        default="LOGIC"
    )
    supersedes_adr_id: str | None = Field(default=None, pattern=r"^ADR-\d{3,5}$")
    ebqc_telemetry: EBQCTelemetrySnapshot | None = Field(
        default=None, description="Linked empirical EBQC telemetry snapshot"
    )


class SystemIATreeOutput(BaseModel):
    ia_hierarchy: dict[str, Any] = Field(default_factory=dict)
    max_depth: int = Field(
        ..., le=3, description="Layer 0.1 limit: <= 3 system decisions"
    )
    ontology_version: str


class MasterLogicFlowOutput(BaseModel):
    flow_steps: list[str] = Field(default_factory=list)
    total_decision_steps: int = Field(
        ..., le=3, description="Layer 0.1 friction budget"
    )
    reversibility_routes: dict[str, str] = Field(
        default_factory=dict, description="Every destructive step mapped to undo/escape"
    )
    state_persistence_mechanic: str = Field(
        ..., description="LocalStorage / URL hash / DB draft session"
    )


class ShatterRequest(BaseModel):
    request_id: str
    screen_id: str
    reason: str
    expert_persona: str
    approved: bool = False
    approver: str | None = None


class LowFiBlueprintsOutput(BaseModel):
    wireframe_ids: list[str] = Field(default_factory=list)
    miller_groups_per_screen: dict[str, int] = Field(
        default_factory=dict, description="Max 7±2 groups"
    )
    primary_ctas_per_screen: dict[str, int] = Field(
        default_factory=dict, description="Max 1 primary CTA"
    )
    shatter_requests: list[ShatterRequest] = Field(default_factory=list)


class Tollgate3LogicLockOutput(BaseModel):
    tier_1_apex_ux: str = Field(..., description="Apex UX with complex backend API")
    tier_2_compromise_ux: str = Field(..., description="Compromise UX with cached data")
    tier_3_fallback_ux: str = Field(
        ..., description="Fallback UX using existing schema"
    )
    agreed_tier: Literal["TIER_1", "TIER_2", "TIER_3"]
    lead_backend_signature: str
    status: Literal["SIGNED_LOCK", "RENEGOTIATE"]


class Phase3LogicArchitectureOutput(BaseModel):
    ia_tree: SystemIATreeOutput
    logic_flow: MasterLogicFlowOutput
    blueprints: LowFiBlueprintsOutput
    tollgate: Tollgate3LogicLockOutput


# ============================================================================
# PHASE 4: SURFACE CRAFT & FRICTION ENGINEERING — Domain 3: Perception
# ============================================================================


class StaticUIScreensOutput(BaseModel):
    screen_assets: list[str] = Field(default_factory=list)
    grid_unit_px: int = 8
    primary_semantic_colors: dict[str, str] = Field(default_factory=dict)


class MicrocopyInteractionOutput(BaseModel):
    semantic_strings: dict[str, str] = Field(
        default_factory=dict, description="Max 60 chars per reading line"
    )
    interaction_states: list[str] = Field(default_factory=list)
    feedback_latency_sla_ms: int = Field(default=100, le=100)


class Tollgate4FrictionReportOutput(BaseModel):
    prototype_url: str
    tested_step_count: int
    competitor_benchmark_step_count: int
    friction_delta: int = Field(
        ..., description="Steps eliminated vs competitor benchmark"
    )
    layer0_compliance: bool = True
    status: Literal["PASS", "FAIL"]


class Phase4SurfaceCraftOutput(BaseModel):
    screens: StaticUIScreensOutput
    microcopy: MicrocopyInteractionOutput
    tollgate: Tollgate4FrictionReportOutput


# ============================================================================
# PHASE 5: REALITY CONSTRAINTS & ENGINEERING CONVERGENCE — Domain 4: Reality
# ============================================================================


class EdgeCaseUILibraryOutput(BaseModel):
    zero_data_empty_states: list[str] = Field(default_factory=list)
    api_timeout_screens: list[str] = Field(default_factory=list)
    truncation_specs: list[str] = Field(default_factory=list)
    endpoints_with_skeleton_loaders: list[str] = Field(
        default_factory=list, description="All endpoints > 400ms"
    )


class WCAGComplianceOutput(BaseModel):
    contrast_ratios_passed: bool = True
    aria_tagging_complete: bool = True
    tab_index_valid: bool = True
    audit_score: float = Field(..., ge=0.98)


class Tollgate5DevAcceptedOutput(BaseModel):
    master_figma_handoff_uri: str
    accepted_sprint_ticket_ids: list[str] = Field(default_factory=list)
    engineering_lead_signature: str
    status: Literal["ACCEPTED", "REJECTED"]


class Phase5RealityConstraintsOutput(BaseModel):
    edge_cases: EdgeCaseUILibraryOutput
    wcag: WCAGComplianceOutput
    tollgate: Tollgate5DevAcceptedOutput


# ============================================================================
# PHASE 6: VALUE REALIZATION & BMC CALIBRATION — Domain 5: Outcomes
# ============================================================================


class ThirtyDayDatasetOutput(BaseModel):
    capability_code: str
    post_launch_metrics: dict[str, float] = Field(default_factory=dict)
    sample_size: int


class BMCDeltaReportOutput(BaseModel):
    targeted_bmc_block: str
    baseline_value: float
    post_launch_value: float
    mathematical_delta_pct: float
    gap_stabilized: bool = True


class Tollgate6ProjectClosedOutput(BaseModel):
    roi_percentage: float
    attributed_fallbacks: list[str] = Field(default_factory=list)
    status: Literal["PROJECT_CLOSED", "REOPEN_ITERATION"]


class Phase6ValidationOutput(BaseModel):
    thirty_day_dataset: ThirtyDayDatasetOutput
    bmc_delta_report: BMCDeltaReportOutput
    tollgate: Tollgate6ProjectClosedOutput
