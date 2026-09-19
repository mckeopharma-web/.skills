---
name: workbook-llm-judge
description: Evaluate every /site product workbook against the canonical curriculum-workbook contract using deterministic fail-closed gates plus an LLM-as-a-Judge qualitative review, then project verdicts and findings into Neo4j.
---

# Workbook LLM Judge

Use this skill whenever a product workbook/curriculum is created, edited, regenerated or promoted.

Canonical sources in WBNK:
- graph/judge/policy.json
- graph/judge/rubric.json
- graph/judge/site-products.json
- graph/judge/judge-prompt.md
- graph/judge/llm-judgments.json
- graph/judge/llm-requests.jsonl
- graph/judge/evaluations.json
- graph/neo4j/workbook-judge.cypher

Reference curriculum architecture:
- curricula/desci-140h

## Required execution order

1. Run deterministic structural checks first.
2. Never ask the LLM to override a deterministic hard blocker.
3. For structurally valid curricula, inspect the evidence scope listed in llm-requests.jsonl.
4. Apply judge-prompt.md exactly.
5. Write only the compact judgment: verdict, qualitative_score, confidence, rationale and findings.
6. Preserve reviewed_at_commit and evidence_scope_path.
7. Rebuild the judge projection.
8. Require the workbook-llm-judge CI workflow to pass.

## Fail-closed invariants

A product cannot PASS when:
- no workbook/curriculum is mapped;
- metadata/program.json is absent or not curriculum-workbook;
- target_hours is not exactly 140;
- module/unit durations do not reconcile to 140;
- objective or competency coverage is incomplete;
- assessment coverage is incomplete;
- exercise/evidence coverage is incomplete;
- prerequisites are broken or cyclic;
- a previously valid LLM judgment is stale because evidence under its scope changed.

## LLM qualitative check

The LLM judges only the residual semantic questions:
- coherent progression;
- domain specialization rather than generic cloning;
- meaningful explanatory content;
- guided and independent practice;
- meaningful learner outputs;
- assessment/rubric alignment;
- evidence sufficiency for the planned hours;
- provenance honesty.

The qualitative contribution is 5/100. Structural evidence contributes 95/100. This intentionally prevents prose quality from masking structural incompleteness.

## Neo4j graph contract

Nodes:
- LLMJudge
- JudgeRun
- JudgeCriterion
- SiteProduct
- WorkbookEvaluation
- LLMJudgment
- JudgeFinding
- Program

Relations:
- EXECUTED_AS
- USES_CRITERION
- HAS_EVALUATION
- EVALUATES_PRODUCT
- EVALUATES_CURRICULUM
- HAS_CURRICULUM
- HAS_LLM_JUDGMENT
- HAS_FINDING

## Population

The judge covers every leaf route under /ressources/produits/ in the canonical site registry. Do not silently drop a product because WBNK lacks a corresponding aggregate. Missing workbooks must remain explicit FAIL findings until materialized or explicitly exempted by policy.
