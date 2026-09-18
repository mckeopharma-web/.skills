# Neo4j contract

## Identity

Every node has a stable globally unique string `id`.

Recommended IDs:

```text
program:<slug>
module:<program-slug>:M01
unit:<program-slug>:M01:U001
objective:<hash-or-curated-slug>
competency:<hash-or-curated-slug>
resource:<canonical-id>
assessment:<program-slug>:M01:U001:A01
```

## Core Cypher

```cypher
MERGE (p:Program {id: $program.id})
SET p.title = $program.title,
    p.target_hours = $program.target_hours,
    p.schema_version = $program.schema_version;

UNWIND $modules AS row
MERGE (m:Module {id: row.id})
SET m.title = row.title,
    m.order = row.order,
    m.allocated_hours = row.allocated_hours
MERGE (p)-[:HAS_MODULE]->(m);
```

Learning units are merged on id and attached using `HAS_UNIT`.

## Invariants

### Duplicate IDs

```cypher
MATCH (n)
WITH n.id AS id, count(*) AS c
WHERE id IS NOT NULL AND c > 1
RETURN id, c
```

Expected rows: 0.

### Orphan units

```cypher
MATCH (u:LearningUnit)
WHERE NOT (:Module)-[:HAS_UNIT]->(u)
RETURN u.id
```

Expected rows: 0.

### Unassessed competencies

```cypher
MATCH (c:Competency)<-[:BUILDS_COMPETENCY]-(u:LearningUnit)
WHERE NOT (u)-[:ASSESSED_BY]->(:Assessment)
RETURN DISTINCT c.id
```

Expected rows: 0 unless an explicit exemption node/qualifier exists.

### Duration reconciliation

```cypher
MATCH (p:Program)-[:HAS_MODULE]->(:Module)-[:HAS_UNIT]->(u:LearningUnit)
WITH p, sum(u.duration_hours) AS hours
RETURN p.id, p.target_hours, hours, round((p.target_hours-hours)*100)/100 AS delta
```

Expected delta: 0.

### Prerequisite cycles

Use a bounded path check over `PRECEDES|REQUIRES` and reject any path returning to its origin.
