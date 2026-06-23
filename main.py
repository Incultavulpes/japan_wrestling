import uww_scraper
import test_parsing as wikipedia_scraper
import clean_master

print("==============================================")
print("   JAPAN WRESTLING PIPELINE MANAGEMENT SYSTEM ")
print("==============================================")
print(" [INGESTION LAYER / RAW ZONE]")
print("  1 - Run UWW Live Web Scraper")
print("  2 - Run Wikipedia Live Web Scraper")
print("\n [TRANSFORMATION LAYER / SILVER ZONE]")
print("  3 - Process & Clean Saved UWW Dataset")
print("  4 - Process & Clean Saved Wikipedia Dataset")
print("==============================================")
    
choice = input("\nSelect operational execution profile: ").strip()
print("----------------------------------------------")

if choice == "1":
    uww_scraper.uww_main_scraper_block()
elif choice == "2":
    wikipedia_scraper.wikipedia_main_scraper_block()
elif choice == "3":
    file_type = "uww"
    clean_master.execution_flow_clean_master(file_type)
elif choice == "4":
    file_type = "wikipedia"
    clean_master.execution_flow_clean_master(file_type)
else:
    print("❌ Invalid entry selection. Shutting down pipeline execution environment.")