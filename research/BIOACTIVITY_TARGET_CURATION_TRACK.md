# Bioactivity target curation: a separate chemistry-and-biology research track

## What this work is

This is the research workflow behind roles that verify whether a bioactivity record is assigned to the correct protein. It connects a compound, an assay, its primary paper or patent, the tested biological material, and a stable protein identifier such as a UniProt accession. It is a strong chemistry/biochemistry/chemical-biology direction, adjacent to drug discovery and cheminformatics. It is not the same task as neuroscience simulation, although the shared foundations—scientific reading, statistics, Python, structured data, reproducibility, and honest boundaries—carry over.

Do not infer eligibility for a role with requirements such as current bench activity, a completed graduate degree, years of biotech/pharma/CRO experience, or hands-on SPR/TR-FRET/radioligand/kinase/GPCR assays. Those are experience requirements, not libraries someone can install. Until they are true, describe this as **self-learning bioactivity curation and database analysis**, not professional assay or target-validation experience.

## The canonical stack: learn in this order

| Layer | Learn | Why it matters | Current status / claim boundary |
|---|---|---|---|
| Scientific language | Protein/gene/isoform/complex, species, construct, mutation, assay format, agonist/antagonist/inhibitor/activator, affinity vs potency | A target name alone is too ambiguous to assign an accession correctly | Learning |
| Primary-source reading | PubMed, Europe PMC, patents, supplementary methods; extract what was actually tested | The paper is the evidence, not a database label | Learning |
| Protein identity | UniProtKB entries, accessions, reviewed status, organism, gene names, canonical sequence/isoforms, features, cross-references and ID mapping | Decide whether the assay material matches a proposed protein | Learning |
| Bioactivity databases | ChEMBL, BindingDB, PubChem BioAssay; assay descriptions, targets, activities, documents and provenance | Locate records and preserve database-specific identifiers | Learning |
| Assay reasoning | Binding vs functional vs cellular/phenotypic assay; SPR, TR-FRET, radioligand, kinase and GPCR assay concepts; IC50, Ki, Kd, EC50 and efficacy | A number has meaning only inside its assay, material, controls, units and mechanism | Learn concepts and read methods; do not claim bench experience |
| Chemistry identity | SMILES, InChIKey, salt/parent form, stereochemistry, units and concentration conversions | Avoid attaching the right protein to the wrong chemical entity or reading incompatible values as comparable | Learning |
| Computation | Python, pandas, `requests`, JSON/CSV, DuckDB/SQL, notebooks, Git and Biopython | Retrieve, join, audit and save a reproducible review table | Existing foundation / continue practicing |
| Cheminformatics | RDKit: parse structures, canonicalize cautiously, fingerprints, substructure checks, depiction | Useful after the table and provenance workflow are solid; not a substitute for assay reading | Later, project-gated |
| Sequence and structure context | NCBI Gene, InterPro/Pfam, sequence alignment/BLAST, PDB or AlphaFold DB | Resolve a family/domain/construct question when the source demands it | Later, question-gated |
| Evidence and review | A structured error taxonomy, confidence labels, peer review, disagreement log and audit trail | A correction must be inspectable and reversible | Build through practice |

**No additional language is required now.** Python plus SQL is the right core. Learn REST/JSON requests in Python before adding JavaScript, C++, R or a large ML stack. RDKit is the first optional specialized package, only when a selected curation question actually needs structure normalization or comparison.

### What this role adds to your existing science stack

The neuroscience workbench teaches equations and simulations. This branch teaches the other half of computational biology: whether the biological labels and measurements in a table mean what they appear to mean. The role does **not** require mastering all of computational chemistry before starting. Learn in this order:

1. Read one database record in its website interface, then locate its source document.
2. Identify the assay material and whether it supports a direct target claim.
3. Resolve protein identity in UniProt, including organism, sequence/construct and complex ambiguity.
4. Record the decision in a reproducible table and make uncertainty visible.
5. Automate retrieval only after you can make the decision manually.
6. Add chemistry structure checks only if the record needs them.

The role makes five concepts especially important: **target confidence**, direct-versus-indirect evidence, assay controls/counterscreens, potency versus affinity, and accession/organism/construct matching. ChEMBL separates assay, activity, target, target component and source-document records; a target can also be a complex, family or non-protein entity. A database label is a starting point for review, not the conclusion.

### Programs and sources: use, do not collect

| Use now | Purpose | First task |
|---|---|---|
| UniProt web interface and REST API | Stable protein entry, organism, gene, sequence and features | Make one identity dossier manually, then retrieve the same fields with Python |
| ChEMBL interface and API | Activity, assay, target, component and source-document records | Trace one activity back to its assay and document |
| BindingDB interface/downloads | Binding measurements, source links and target-focused records | Compare one Ki or Kd record with its paper |
| PubChem BioAssay and PUG-REST | Assay descriptions, targets and rows | Identify whether an assay actually defines a protein target |
| PubMed / Europe PMC / patent source | Primary methods, supplementary material and claims | Cite the exact location supporting or weakening an assignment |
| Python, pandas, requests, DuckDB and Jupyter | Evidence table, API receipt and repeatable audit | Save original IDs, retrieval date and a decision ledger |

| Add only when a project needs it | Why later |
|---|---|
| Biopython, NCBI Gene, InterPro/Pfam, BLAST | Sequence/domain questions and construct mapping |
| RDKit | Chemical identity, salts, stereochemistry and structure comparisons |
| PDB / AlphaFold DB | Structural context; a predicted structure is not binding evidence |
| Docking, molecular dynamics, OpenMM, large ML models | Separate modeling projects, not prerequisites for target-record curation |

Do not treat reading about SPR, TR-FRET, radioligand, kinase or GPCR assays as performing them. The goal at this stage is to read an assay paper accurately enough to tell what it establishes and what it does not.

## What to inspect for every proposed target assignment

1. **Record identity:** database record ID, source document, compound identity, assay type, endpoint and reported value/unit.
2. **Biological material:** organism, gene/protein name, isoform, domain/construct boundaries, mutation, tags, cell line, purified protein or whole-cell system.
3. **Assay logic:** direct binding versus functional/cellular/phenotypic readout; primary versus confirmatory assay; controls and counterscreens; what an IC50, Ki, Kd, EC50 or percent effect actually means in that protocol.
4. **Identifier match:** proposed UniProt accession, organism, sequence/construct compatibility, isoform ambiguity, protein complex/subunit issues and non-protein targets.
5. **Decision:** supported, incorrect with proposed replacement, ambiguous/needs review, or not a direct protein assignment. Cite the exact evidence and state uncertainty.

Never turn a phenotypic or cell-line assay into a direct single-protein binding claim merely because a pathway or gene is discussed in the paper. Likewise, a gene symbol is not enough when species, paralogs, isoforms, constructs or a protein complex make the identity ambiguous.

## Starter error taxonomy

Use these labels in a future review sheet. They are working labels, not Mercor's private taxonomy.

| Code | Meaning | Example review question |
|---|---|---|
| `SPECIES_MISMATCH` | Accession belongs to the wrong organism | Was human protein assigned when the paper used a rodent ortholog? |
| `PARALOG_MISMATCH` | Related but different gene/protein | Does the assay name collapse two similar family members? |
| `ISOFORM_OR_CONSTRUCT` | Canonical accession may not describe tested isoform/domain/mutant | Is the tested kinase domain or splice isoform identifiable? |
| `COMPLEX_OR_SUBUNIT` | A component was assigned where the assay required a complex | Is binding to a heteromer being represented as one subunit? |
| `INDIRECT_OR_PHENOTYPIC` | No direct molecular target established by this assay | Was a cellular viability or reporter readout overinterpreted? |
| `NON_PROTEIN_TARGET` | Target is nucleic acid, lipid, organism, tissue or undefined material | Is a UniProt ID inappropriate altogether? |
| `DOCUMENT_OR_ASSAY_LINK` | The record/document/assay linkage is wrong or insufficient | Does the cited source describe a different construct or measurement? |
| `AMBIGUOUS_NEEDS_REVIEW` | Evidence does not support a confident correction | What missing construct/species/sequence detail prevents resolution? |

## Four portfolio-quality learning projects

Do these sequentially. Do not present any of them as work for Mercor, ChEMBL, BindingDB, or a biomedical employer.

1. **UniProt identity dossier (10 proteins):** select well-documented proteins across at least three families. For each, record accession, organism, gene names, reviewed status, canonical/isoform note, function, relevant domain/features, and the source link. Include one deliberate paralog trap and explain it. Output: a versioned Markdown report plus CSV/JSON ledger.
2. **Assay-method annotation set (10 public papers):** extract assay class, material, endpoint, value type, unit, directness of target evidence, controls and source location. Include binding and functional assays, and preserve an ambiguous/phenotypic case. Output: evidence table; no invented target corrections.
3. **Database-to-paper reconciliation (20 public records):** choose a narrow, tractable target family and source the record through ChEMBL/BindingDB/PubChem to its paper. Independently verify the proposed accession or classify it as ambiguous. A second-pass reviewer—human mentor, instructor, or domain expert—should audit a sample before publishing any result. Output: reproducible notebook, source receipt, decision ledger, disagreement log and explicit no-claim boundary.
4. **Small curation QA tool:** use Python/pandas/DuckDB to flag missing organism, accession/species conflicts, duplicated documents, impossible/mixed units, and target names mapping to multiple candidate accessions. The tool flags review candidates; it does not autonomously correct scientific databases. Output: tests using synthetic fixtures plus a small manually reviewed public example.

5. **Assay semantics notebook:** take a small, fully public set of binding and functional records and make a data dictionary for `Ki`, `Kd`, `IC50`, `EC50`, percent inhibition and the units/conditions that make them interpretable. Include examples where values must **not** be compared. This can follow project 2; it should not invent a conversion between potency and affinity.

For every project use: question → data/source provenance → extraction rule → comparison → decision → uncertainty → what would change the decision. Keep raw source identifiers and quoted locations separate from your interpretation. Save an exact date because database annotations change.

## Official starting points

- [UniProt entry help](https://www.uniprot.org/help/entry), [canonical sequence and isoforms](https://www.uniprot.org/help/canonical_and_isoforms), and [sequence features](https://www.uniprot.org/help/sequence_annotation): understand accession, organism, isoforms and construct-relevant annotations before ID mapping.
- [ChEMBL web-service documentation](https://chembl.gitbook.io/chembl-interface-documentation/web-services/chembl-data-web-services): programmatic access is useful after you can read the record in the web interface.
- [BindingDB target data](https://www.bindingdb.org/rwd/bind/ByTargetNames.jsp) and [BindingDB 2024 paper](https://www.bindingdb.org/rwd/bind/gkae1075.pdf): BindingDB target names are linked to UniProt and its records carry affinity context.
- [PubChem PUG-REST BioAssay tutorial](https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest-tutorial): assay descriptions, targets and activity rows can be retrieved programmatically; not every assay defines a protein or gene target.
- [RDKit documentation](https://www.rdkit.org/docs/): use only after a chemistry-identity question demands it.
- [UniProt programmatic access](https://www.uniprot.org/help/api) and [Biopython documentation](https://biopython.org/docs/latest/): use after manual record reading establishes what fields you need.
- [PubMed](https://pubmed.ncbi.nlm.nih.gov/) and [Europe PMC](https://europepmc.org/): primary-document search and access routes. Patents can be primary sources too, but must be read for the actual experimental material and method rather than treated as simple target labels.

## Relationship to your main science route

The first overlap with the neuroscience workbench is the reaction-network lesson, then a careful binding/affinity mini-project. Do not add a molecular drug-target module to the ketamine notebook before you have a paper-backed reaction/assay question and a separate evidence ledger. The bioactivity track can become a serious chemistry/biophysics research direction, but it does not require abandoning the math-and-modeling path.

## When the stack is enough to apply for junior data/curation-adjacent work

You should be able to take a public record, retrieve the original source, distinguish direct binding from functional evidence, identify at least one genuine ambiguity, document a conservative decision, write a small query to reproduce the table, and explain every column. That demonstrates hands-on project use. It still does not substitute for the specific bench-active or years-of-industry requirements in the listing above.
