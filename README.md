# Japan Wrestling Pipeline Management System (WPMS)

A robust, high-performance hybrid ETL pipeline designed to extract, transform, and persist multi-year, multi-variable global wrestling data using a localized Medallion Architecture (Bronze and Silver layers).

---

## 🏗️ Architectural Overview & Data Topology
The structural foundation of this system is modeled on a local Medallion Architecture, establishing a disciplined, multi-layered data lakehouse configuration to manage the collection and normalization of competitive sports data.

                  ┌──────────────────────┐
                  │  Upstream Platforms  │
                  └──────────┬───────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
      [ Wikipedia Track ]             [ UWW Track ]
     HTML Parsing / Scraping      Direct API Interception
              │                             │
              ▼                             │
    ┌───────────────────┐                   │
    │    BRONZE ZONE    │                   │
    │ (Raw HTML Tables) │                   │
    └─────────┬─────────┘                   │
              │                             ▼
              │                   ┌───────────────────┐
              │                   │    BRONZE ZONE    │
              │                   │ (Raw JSON Splits) │
              │                   └─────────┬─────────┘
              ▼                             ▼
    ┌─────────────────────────────────────────────────┐
    │                   SILVER ZONE                   │
    │     (Unified, Vector-Joined Standard Schema)    │
    └─────────────────────────────────────────────────┘

### 🔄 The Asymmetric Pipeline Design
* **UWW Track (Consolidated API Stream):** The United World Wrestling pipeline leverages the fact that the platform delivers data via structured, server-side REST API endpoints. Because this source provides a predictable schema (JSON payloads) right at the boundary network layer, a decoupled staging setup is unnecessary.

    **The Implementation**: The pipeline extracts, validates, filters, and standardizes the records in memory within a single operational execution loop.

    **The Architecture**: It performs an atomic runtime pass. It writes the intermediate raw schema directly to the Bronze Zone for long-term historical audit trails, while simultaneously running vectorized array mutations to join, clean, and output the standardized master dataset straight into the Silver Zone. This completely eliminates unnecessary disk I/O bottlenecks.pass.

* **Wikipedia Track (Symmetric Batch Processing):** Unlike the UWW track, Wikipedia relies on loose HTML document styling. Capturing data here requires deep Document Object Model (DOM) traversal, targeting unstable `wikitable` classes and generic table data (`<td>`) tags that can change or break based on manual user edits.
  
  **The Implementation:** To enforce strict system reliability, this track uses a classic decoupled batch configuration following a Fail-Fast architecture.
  
  **The Architecture:**
  * **Stage 1 (Ingestion):** The web scraper pulls raw, messy textual strings directly from the live DOM layout and dumps them directly into the Bronze Zone as a localized snapshot. No parsing or cleaning happens here; the goal is simply data preservation.
  * **Stage 2 (Transformation):** A completely isolated, downstream execution script imports the raw data from disk and runs extensive Regular Expression (`re`) pattern matching to clean corrupted strings, filter outliers, map column types, and export a pristine dataset to the Silver Zone. If an upstream structural layout changes mid-season, only Stage 1 breaks—leaving your downstream historical transformations safely isolated.
---

## 🚀 Key Engineering & System Design Decisions

### 1. Shift from DOM Scraping to Backend API Interception
* **The Context:** Initial data sourcing strategies for the UWW pipeline focused on traditional front-end scraping. However, client-side rendering and volatile class naming conventions introduce structural fragility into long-term data pipelines.
* **The Value:** Initial data sourcing strategies for the UWW pipeline focused on traditional front-end scraping. However, client-side rendering and volatile class naming conventions introduce structural fragility into long-term data pipelines.

### 2. High-Performance Pandas Patterns
* **The Context:** Iteratively appending rows or expanding DataFrames inside nested loops (such as moving through multi-year blocks or ten distinct weight classes) forces memory reallocation at every iteration —a primary bottleneck in Python data pipelines.
* **The Value:** Raw normalized payloads are collected into a native Python list array inside execution loops. A single, vector-bound pd.concat() operation is triggered outside the loop, minimizing RAM fragmentation and optimizing memory allocation limits.

### 3. Defensive Programming & Memory Management
* **The Context:** Operational robustness in automated pipelines requires explicit guardrails against network failures and internal memory pointer bugs.
* **The Value:** * Fail-Fast Network Gating: Built with strict HTTP status handling using requests.models.Response.raise_for_status(), ensuring the orchestrator terminates immediately upon encounter with upstream server faults rather than injecting corrupt, truncated data downstream.

Memory Isolation: Utilized explicit data replication via .copy() when filtering slices of dataframes. This isolates memory pointers, completely eliminating pointer mutation risks and preventing SettingWithCopyWarning execution errors

---

## 📁 Data Lakehouse Organization (Medallion Layout)

* The physical directory structure mirrors the Medallion separation, using standardized naming conventions and explicit file partitioning:

```text
data/
├── uww_raw/                              <-- Bronze Zone: Raw JSON Extraction Splits
│   ├── uww_2024_57kg_raw_results.csv
│   ├── uww_2024_61kg_raw_results.csv
│   └── ...
├── raw/                                  <-- Bronze Zone: Raw HTML DOM Layout Tables
│   ├── olympic_wikipedia_2000_results.csv
│   ├── olympic_wikipedia_2004_results.csv
│   └── ...
└── silver/                               <-- Silver Zone: Cleaned, Consolidated Datasets
    ├── uww/
    │   ├── 2024_uww_clean_results.csv    <-- Vector-joined master file for the 2024 season
    │   └── ...
    └── wikipedia/
        ├── 2000_wikipedia_clean_results.csv
        └── ...
```
---

## ⚙️ Operational Profiles (CLI Execution)

* A user guide detailing how to spin up `main.py` and interact with the asymmetric operational terminal execution profiles.

```text
==============================================
   JAPAN WRESTLING PIPELINE MANAGEMENT SYSTEM 
==============================================
 [CONSOLIDATED PIPELINES (BRONZE + SILVER)]
  1 - Run UWW API Ingestion & Cleaning Loop
    
 [STAGED PIPELINES (BATCH EXTRACT / TRANSFORM)]
  2 - Extract Wikipedia Raw Data (Bronze)
  3 - Process & Clean Wikipedia Dataset (Silver)
    
 [SYSTEM CONTROL]
  0 - Exit Pipeline Environment
==============================================

```

**Profile 1**: Triggers the atomic UWW pipeline, querying multi-year targets via REST, backing up raw files to the Bronze zone, and mapping standard columns to a master Silver schema.

**Profiles 2 & 3**: Isolates the decoupled batch phases required for HTML-parsed data tables, allowing independent raw storage dumps or separate transformation routines.