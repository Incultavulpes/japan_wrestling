# Japan Wrestling Pipeline Management System (WPMS)

A robust, high-performance hybrid ETL pipeline designed to extract, transform, and persist multi-year, multi-variable global wrestling data using a localized Medallion Architecture (Bronze and Silver layers).

---

## 🏗️ Architectural Overview & Data Topology
* Detailed explanation of the core pipeline architecture.
* How the system handles differing upstream data models asynchronously.

### 🔄 The Asymmetric Pipeline Design
* **UWW Track (Consolidated API Stream):** Details on bypassing the frontend DOM to capture clean network payloads, combining extraction and normalization steps into an atomic runtime pass.
* **Wikipedia Track (Symmetric Batch Processing):** Details on the decoupled extraction (DOM parsing to Bronze) and separate cleaning phase (Regex parsing to Silver).

---

## 🚀 Key Engineering & System Design Decisions

### 1. Shift from DOM Scraping to Backend API Interception
* **The Context:** Moving away from traditional `<td>` and `wikitable` web scrapers.
* **The Value:** Why targeting internal REST endpoints minimized processing latency, network overhead, and layout-driven fragility.

### 2. High-Performance Pandas Patterns
* **The Context:** Bypassing iterative DataFrame appending inside loops.
* **The Value:** Explaining the List Accumulator pattern to minimize memory overhead by running a single, vector-bound `pd.concat()` operation outside execution loops.

### 3. Defensive Programming & Memory Management
* **The Context:** Data integrity guards.
* **The Value:** Explaining why explicit memory replication (`.copy()`) was implemented to eliminate pointer mutation risks (`SettingWithCopyWarning`) and why strict network gating (`raise_for_status()`) was chosen to enforce a Fail-Fast philosophy.

---

## 📁 Data Lakehouse Organization (Medallion Layout)
* A visual directory layout mapping out `data/uww_raw/` (Bronze raw partitions) and `data/silver/uww/` (Silver standardized outputs).

---

## ⚙️ Operational Profiles (CLI Execution)
* A user guide detailing how to spin up `main.py` and interact with the asymmetric operational terminal execution profiles.