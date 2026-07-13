"""Japan Wrestling Pipeline Management System (WPMS) Orchestrator.

This module serves as the centralized Command Line Interface (CLI) controller 
and execution engine for the data lakehouse. It exposes explicit operational 
profiles to manage asymmetric data tracks, routing control flows to 
platform-specific extraction and transformation modules.

Operational Topologies:
    - Track 1 (UWW): Consolidated, inline network ingestion and normalization.
    - Track 2 (Wikipedia): Decoupled batch extraction and secondary disk transforms.

Supported Platforms:
    - United World Wrestling (UWW) Internal REST API via `test_request`
    - Wikipedia HTML DOM Tables via `test_parsing`
    - Standardized Silver-layer schemas via `clean_master`
"""

import test_request
import test_parsing as wikipedia_scraper
import clean_master


def execute_orchestrator_loop() -> None:
    """Runs the continuous CLI execution loop for the data pipelines.
    
    This function blocks execution using an infinite operational loop, processing
    user input selection strings to trigger atomic pipelines, isolated batch 
    ingestions, or downstream cleaning routines.
    
    Returns:
        None
    """
    while True:
        print("==============================================")
        print("   JAPAN WRESTLING PIPELINE MANAGEMENT SYSTEM ")
        print("==============================================")
        print(" [CONSOLIDATED PIPELINES (BRONZE + SILVER)]")
        print("  1 - Run UWW API Ingestion & Cleaning Loop")
        
        print("\n [STAGED PIPELINES (BATCH EXTRACT / TRANSFORM)]")
        print("  2 - Extract Wikipedia Raw Data (Bronze)")
        print("  3 - Process & Clean Wikipedia Dataset (Silver)")
        
        print("\n [SYSTEM CONTROL]")
        print("  0 - Exit Pipeline Environment")
        print("==============================================")
            
        choice = input("\nSelect operational execution profile: ").strip()
        print("----------------------------------------------")

        if choice == "1":
            # Profile 1: Atomic runtime optimization pass.
            # Executes the network boundary layer request and commits the records
            # simultaneously to the Bronze and Silver disk storage tiers.
            test_request.get_provisional_weight_class()
            
        elif choice == "2":
            # Profile 2: Isolated Ingestion Stage.
            # Triggers DOM traversal to harvest raw layout tables from live 
            # web endpoints without mutation, backing them up directly to Bronze storage.
            wikipedia_scraper.wikipedia_main_scraper_block()
            
        elif choice == "3":
            # Profile 3: Isolated Transformation Stage.
            # Invokes the unified cleaning master module to run RegEx parsers,
            # map column schemas, and compile the final master dataset to the Silver tier.
            file_type = "wikipedia"
            clean_master.execution_flow_clean_master(file_type)
            
        elif choice == "0":
            print("👋 Shutting down pipeline execution environment. Goodbye!")
            break
            
        else:
            # Defensive validation fallback to prevent unhandled operational states.
            print("❌ Invalid entry selection. Please choose a valid profile.")


if __name__ == "__main__":
    execute_orchestrator_loop()