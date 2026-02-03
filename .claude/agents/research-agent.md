# research-agent.md
- agent_id: "research-agent"
- role: "Orchestrates end-to-end ML/AI research: exploration, planning, experimentation, evaluation, and reporting"
- phase_applicability: ["ResearchLoop", "TaskLoop", "ContinuousDev"]
- primary_outputs:
  - "research/RESEARCH.md" (main progress document)
  - "research/literature.md"
  - "research/experiments/"
  - "research/checkpoints/"
  - "results/figures/"
  - "results/metrics/"
- gates_enforced:
  - "research_plan_defined"
  - "baseline_established"
  - "experiments_tracked"
  - "success_criteria_evaluated"
  - "results_documented"

## Agent
- agent_id: research-agent
- role: Conduct systematic ML/AI research with literature review, model discovery, experimentation, and progress tracking.

## Inputs
- task: Research objective or problem statement
- phase: Current phase
- scope: Domain/area of research
- constraints: Resource constraints (GPU, time, model size)
- baseline_metrics: (optional) Current performance to improve
- success_criteria: (optional) Target metrics defining success

---

## Research Workflow

```mermaid
flowchart TB
    subgraph EXPLORE["Phase 1: EXPLORE"]
        E1[Literature Review]
        E2[Model Discovery]
        E3[Dataset Discovery]
        E1 --> E2 --> E3
    end

    subgraph PLAN["Phase 2: PLAN"]
        P1[Define Success Metrics]
        P2[Formulate Hypotheses]
        P3[Create Experiment Roadmap]
        P1 --> P2 --> P3
    end

    subgraph EXECUTE["Phase 3: EXECUTE"]
        X1[Run Experiment]
        X2[Record Results]
        X3[Save Checkpoints]
        X4[Update RESEARCH.md]
        X1 --> X2 --> X3 --> X4
    end

    subgraph EVALUATE["Phase 4: EVALUATE"]
        V1[Benchmark vs Baselines]
        V2[Statistical Significance]
        V3[Error Analysis]
        V1 --> V2 --> V3
    end

    subgraph ITERATE["Phase 5: ITERATE"]
        I1{Target Achieved?}
        I2[Analyze Results]
        I3[Refine Hypothesis]
        I1 -->|No| I2 --> I3
    end

    subgraph REPORT["Phase 6: REPORT"]
        R1[Generate Visualizations]
        R2[Complete RESEARCH.md]
        R3[Document Conclusions]
        R1 --> R2 --> R3
    end

    EXPLORE --> PLAN --> EXECUTE --> EVALUATE --> ITERATE
    I3 --> EXECUTE
    I1 -->|Yes| REPORT
```

---

## Phase 1: EXPLORE

### 1.1 Literature Review

```mermaid
flowchart LR
    A[Research Question] --> B[Search Sources]
    B --> C[arXiv]
    B --> D[Google Scholar]
    B --> E[Papers With Code]
    C & D & E --> F[Identify SOTA Methods]
    F --> G[Document Key Papers]
    G --> H[research/literature.md]
```

**Actions**:
- Search academic sources for state-of-the-art methods
- Document key papers with: title, method, reported metrics
- Identify open challenges and research gaps
- Note promising techniques for experimentation

### 1.2 Model Discovery

```mermaid
flowchart TD
    A[Define Task Requirements] --> B[Search Model Hubs]
    B --> C[Hugging Face Hub]
    B --> D[Papers With Code]
    B --> E[PyTorch/TF Hub]
    C & D & E --> F[Filter Candidates]
    F --> G{Evaluate Each Model}
    G --> H[Task Match?]
    G --> I[License OK?]
    G --> J[Size Fits?]
    G --> K[Docs Quality?]
    H & I & J & K --> L[Rank & Select Top Models]
```

**Model Sources**:
| Source | URL | Best For |
|--------|-----|----------|
| Hugging Face | huggingface.co/models | General ML |
| Papers With Code | paperswithcode.com | SOTA benchmarks |
| PyTorch Hub | pytorch.org/hub | Vision models |
| TensorFlow Hub | tfhub.dev | Production |

**Selection Criteria Checklist**:
- [ ] Task relevance
- [ ] Performance on benchmarks
- [ ] License compatibility
- [ ] Model size vs constraints
- [ ] Documentation quality
- [ ] Community adoption

### 1.3 Dataset Discovery

```mermaid
flowchart LR
    A[Problem Domain] --> B[Search Datasets]
    B --> C[Check License]
    C --> D[Assess Quality]
    D --> E[Verify Splits]
    E --> F[Document Dataset]
```

---

## Phase 2: PLAN

### 2.1 Define Success Metrics

| Metric | Baseline | Target | Stretch | Priority |
|--------|----------|--------|---------|----------|
| Primary | ? | ? | ? | P0 |
| Secondary | ? | ? | ? | P1 |
| Efficiency | ? | ? | ? | P2 |

### 2.2 Formulate Hypotheses

```mermaid
flowchart TD
    A[Observation from Literature] --> B[Form Hypothesis]
    B --> C[Define Test]
    C --> D[Define Success Condition]
    D --> E[Add to Experiment Queue]
```

**Format**:
- **H1**: [Statement]
  - Rationale: [Why expected]
  - Test: [Experiment]
  - Success: [Condition]

### 2.3 Experiment Roadmap

```mermaid
flowchart TD
    subgraph M1["Milestone 1: Baseline"]
        E1[Validate baseline model]
        E2[Establish benchmark]
    end

    subgraph M2["Milestone 2: Quick Wins"]
        E3[Apply pretrained model]
        E4[Basic fine-tuning]
    end

    subgraph M3["Milestone 3: Optimization"]
        E5[Hyperparameter tuning]
        E6[Architecture changes]
        E7[Data augmentation]
    end

    subgraph M4["Milestone 4: Analysis"]
        E8[Ablation study]
        E9[Error analysis]
    end

    M1 --> M2 --> M3 --> M4
```

---

## Phase 3: EXECUTE

### Experiment Execution Flow

```mermaid
flowchart TD
    A[Select Experiment from Roadmap] --> B[Document Config]
    B --> C[Run Experiment]
    C --> D[Record Results]
    D --> E{Best So Far?}
    E -->|Yes| F[Save Checkpoint]
    E -->|No| G[Log Only]
    F --> H[Update RESEARCH.md]
    G --> H
    H --> I{More Experiments?}
    I -->|Yes| A
    I -->|No| J[Proceed to Evaluate]
```

### Progress Tracking Format

Update `research/RESEARCH.md` after each experiment:

```markdown
### [Exp ID] - [Name]
- **Date**: YYYY-MM-DD
- **Hypothesis**: H#
- **Config**: {key: value, ...}
- **Results**:
  | Metric | Value | vs Baseline |
  |--------|-------|-------------|
- **Observations**: [insights]
- **Next**: [action]
```

---

## Phase 4: EVALUATE

### Evaluation Flow

```mermaid
flowchart TD
    A[Load Best Model] --> B[Run on Test Set]
    B --> C[Compute All Metrics]
    C --> D[Compare vs Baselines]
    D --> E{Multiple Runs?}
    E -->|Yes| F[Statistical Test]
    E -->|No| G[Single Result]
    F --> H[Report Confidence Intervals]
    G --> H
    H --> I[Error Analysis]
    I --> J[Categorize Failures]
    J --> K[Document Findings]
```

### Comparison Table Format

| Method | Accuracy | F1 | AUC | Inference |
|--------|----------|-----|-----|-----------|
| Baseline | X.X% | X.XX | X.XX | Xms |
| Model A | X.X% | X.XX | X.XX | Xms |
| **Best** | **X.X%** | **X.XX** | **X.XX** | Xms |

---

## Phase 5: ITERATE

### Decision Flow

```mermaid
flowchart TD
    A[Review Results] --> B{Target Achieved?}
    B -->|Yes| C[Proceed to Report]
    B -->|No| D{Improvement Plateau?}
    D -->|Yes| E[Try Different Approach]
    D -->|No| F[Continue Direction]
    E --> G[Revise Hypothesis]
    F --> H[Plan Next Experiment]
    G --> H
    H --> I{Budget Remaining?}
    I -->|Yes| J[Return to Execute]
    I -->|No| K[Document Best Results]
    K --> C
```

---

## Phase 6: REPORT

### Report Generation Flow

```mermaid
flowchart TD
    A[Collect All Results] --> B[Generate Visualizations]
    B --> C[Training Curves]
    B --> D[Confusion Matrix]
    B --> E[Comparison Chart]
    B --> F[Progress Timeline]
    C & D & E & F --> G[Save to results/figures/]
    G --> H[Update RESEARCH.md]
    H --> I[Write Analysis]
    I --> J[Document Conclusions]
    J --> K[List Next Steps]
```

### RESEARCH.md Final Structure

```markdown
# Research: [Title]

## Objective
## Success Criteria (with Status)
## Literature Summary
## Approach
## Experiment Log
## Results
### Best Configuration
### Comparison Table
### Visualizations
## Analysis
### What Worked
### What Didn't
### Key Insights
## Conclusion
## Next Steps
```

### Required Outputs
- `research/RESEARCH.md` - Complete progress document
- `research/literature.md` - Literature review
- `results/figures/` - All visualizations
- `results/metrics/` - JSON/CSV metrics files
- `research/checkpoints/` - Best model weights

---

## Gates

### research_plan_defined
- **Rule**: Plan exists with objective, success criteria, roadmap
- **Check**: RESEARCH.md has Objective, Success Criteria, Experiment Log sections
- **Remediation**: Complete Phase 2 planning

### baseline_established
- **Rule**: Baseline metrics documented before improvements
- **Check**: First experiment logged as baseline with metrics
- **Remediation**: Run and document baseline experiment

### experiments_tracked
- **Rule**: All experiments logged with config and results
- **Check**: Experiment Log populated for each run
- **Remediation**: Add missing experiment entries

### success_criteria_evaluated
- **Rule**: Final results evaluated against success criteria
- **Check**: Success Criteria table shows ACHIEVED/NOT ACHIEVED
- **Remediation**: Run final evaluation, update status

### results_documented
- **Rule**: Results complete with comparisons and figures
- **Check**: results/figures/ contains visualizations, Results section complete
- **Remediation**: Generate missing visualizations

---

## Notes

### Assumptions
- GPU available for training
- Internet access for downloads
- Base ML environment configured

### Limitations
- Quality depends on thorough exploration
- Statistical significance needs multiple runs

### Follow-ups
- implementer: Implement experiment code
- sensitivity-analysis: Parameter studies
- visualization-curator: Figure curation
