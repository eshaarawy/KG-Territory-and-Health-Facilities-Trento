# KG Territory and Health Facilities — Trentino

A Knowledge Graph (KG) built using the **iTelos methodology** that organizes and provides
access to information about healthcare facilities and geographical features across the
**Trentino region**, Italy.

Built at the **KnowDive Group**, Department of Information Engineering and Computer Science,
University of Trento (2025).

**Authors:** Mohamed Elshaarawy, Hassan Faour

---

## Overview

The KG functions as a centralized knowledge hub connecting citizens, public health planners,
and emergency services to critical information about the location, specialization, availability,
and accessibility of healthcare resources across Trentino.

![Visual Graph in GraphDB](<Phase 4 - Entity Definition/visual.png>)

---

## Use Cases

The KG was designed around four real-world personas and scenarios:

- **Emergency proximity** — find the nearest hospital from GPS coordinates
- **Local specialized care** — find elderly care facilities within a municipality
- **Service gap analysis** — identify municipalities with no psychiatric services
- **Capacity planning** — aggregate bed counts by geographical area

---

## Data Sources

All datasets sourced from the [Open Data Trentino](https://dati.trentino.it/) portal:

| Dataset | Description |
|---|---|
| `OSPEDALI001` | Hospitals in Trentino |
| `FARM001` | Pharmacies |
| `PARAFARM001` | Para-pharmacies |
| `SANSTRUT001` | General health structures |
| `RIASTRUT001` | Rehabilitation structures |
| `ASSRESIDENZIALE001` | Residential care facilities |
| `ASSSEMIRESIDENZIALE001` | Semi-residential care facilities |

---

## Knowledge Graph Design

### Entity Types (Etypes)

![Entity Relationship Diagram](<Phase 1 - Purpose Definition/ERD.png>)

| Entity | Category | Schema.org Alignment |
|---|---|---|
| `HealthFacility` | Core (superclass) | `schema:MedicalOrganization` |
| `Hospital` | Core | `schema:Hospital` |
| `Dispensary` | Core | `schema:Pharmacy` |
| `CareStructure` | Core | New class |
| `RehabilitationStructure` | Core | New class |
| `Municipality` | Common | `schema:AdministrativeArea` |

### Ontology

![Ontology Language Definition](<Phase 2 - Language Definition/kg_labeled.png>)

---

## Data Processing

Raw CSV datasets were cleaned and merged using Python scripts:

- `merging_careStructures.py` — merges residential and semi-residential datasets
- `merging_dispensaries.py` — combines pharmacies and para-pharmacies into a single
  `Dispensary` entity with a `DISPENSARY_TYPE` attribute
- `merging_hospitals.py` — merges `OSPEDALI001` with hospital entries from `SANSTRUT001`
- `cleaning_healthFacilities.py` — filters remaining general health structures

---

## Knowledge Graph Construction

Entities were mapped to ontological properties using **Karma Data Integration** and exported
as **Turtle (.ttl)** format. Each entity was assigned a unique IRI:
http://knowdive.disi.unitn.it/etype#<EntityName>

![Entity Definition in Karma](<Phase 4 - Entity Definition/karma.png>)

The KG was loaded and validated in **GraphDB**:

![Class Relationships in GraphDB](<Phase 4 - Entity Definition/dependencies-HealthFacility.png>)

![Class Hierarchy in GraphDB](<Phase 4 - Entity Definition/class-hierarchy-HealthFacility.png>)

---

## Methodology

This project follows the **iTelos methodology** for Knowledge Graph construction, structured
across four phases:

1. **Purpose Definition** — personas, scenarios, competency questions, ER model
2. **Language Definition** — ontology alignment with Schema.org, data layer cleaning
3. **Knowledge Definition** — formal teleontology with IRIs, domains, ranges, and XSD datatypes
4. **Entity Definition** — Karma mapping, IRI assignment, GraphDB validation

---

## Tech Stack

`Python` · `Karma Data Integration` · `GraphDB` · `SPARQL` · `OWL/RDF` · `Turtle (.ttl)` · `Schema.org`