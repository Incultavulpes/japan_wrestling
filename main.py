import test_request
import test_parsing as wikipedia_scraper
import clean_master

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
        # This single execution now drops files into both data/uww_raw and data/silver/uww
        test_request.get_provisional_weight_class()
    elif choice == "2":
        wikipedia_scraper.wikipedia_main_scraper_block()
    elif choice == "3":
        file_type = "wikipedia"
        clean_master.execution_flow_clean_master(file_type)
    elif choice == "0":
        print("👋 Shutting down pipeline execution environment. Goodbye!")
        break
    else:
        print("❌ Invalid entry selection. Please choose a valid profile.")