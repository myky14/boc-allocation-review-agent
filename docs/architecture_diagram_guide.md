# Architecture Diagram Guide

This document details the recommended structure, visual styles, and Mermaid diagram code for representing the decoupled ADK-inspired agent runtime architecture.

---

## 🗺️ Mermaid Diagram Code

You can render the core architecture flow directly in markdown using the following code block:

```mermaid
graph TD
    classDef primary fill:#4F46E5,stroke:#4F46E5,color:#FFFFFF,stroke-width:2px;
    classDef secondary fill:#06B6D4,stroke:#06B6D4,color:#FFFFFF,stroke-width:2px;
    classDef safety fill:#EF4444,stroke:#EF4444,color:#FFFFFF,stroke-width:2px;
    classDef storage fill:#0F172A,stroke:#334155,color:#F8FAFC,stroke-width:1px;

    %% Data Inputs
    A["General Ledger (data/synthetic/)"] --> B["Workbook Loader"];
    class A,B storage;

    %% Agent Loop
    B --> C["BOCReviewAgent.run"];
    class C primary;

    subgraph Runtime ["ADK-Inspired Agent Runtime (boc_agent/runtime/)"]
        C --> D["Planner (planner.py)"];
        D -->|Intent Capability Routing| E["Executor (executor.py)"];
        E -->|Tool Execution Context| F["Tool Registry (registry.py)"];
        class D,E,F secondary;
    end

    %% Tools Layer
    subgraph Tools ["Tools Layer (boc_agent/tools/)"]
        F --> G["Security Guardrail Tool"];
        F --> H["Classification Tool"];
        F --> I["Eligibility Tool"];
        F --> J["Allocation Wrapper"];
        class G safety;
        class H,I,J secondary;
    end

    %% Deterministic Core Rules
    J -->|Direct Delegation| K["Deterministic Rules (allocation_tool.py)"];
    class K safety;

    %% Trace Observability
    E -->|Structured Logs| L["RuntimeTrace Exporter"];
    L --> M["Local JSON Traces"];
    class L primary;
    class M storage;

    %% Outputs & Dashboard
    E --> N["Workbook Exporter"];
    N --> O["Reviewed Ledger"];
    class N primary;
    class O storage;

    O --> P["Streamlit Dashboard (app.py)"];
    class P primary;
```

---

## 🎨 Visual Style Design Recommendations

For presentations, portfolios, or external layout editors:

### draw.io Setup
- **Theme**: Dark Mode.
- **Node Colors**: Slate Grey (`#1E293B`) for boxes, with borders matching HSL tailored Indigo (`#6366F1`) and HSL tailored Cyan (`#06B6D4`).
- **Connection Style**: Orthogonal curved lines with `1pt` thickness, using cyan fill arrows to represent logic transitions.
- **Font**: Use **Helvetica** or **Inter** at `11pt` or `12pt`.

### Excalidraw Styling
- **Stroke**: Hand-drawn style with Medium roughness to give a friendly, sketch-based developer prototype aesthetic.
- **Fill**: Light translucent fill patterns (e.g. crosshatch for database/files, solid tint for primary orchestrator nodes).
- **Font**: Hand-drawn standard or Code font for variables and filenames.
- **Color Palette**: Dark Slate background with glowing pastel blue and indigo strokes.
