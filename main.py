import uww_scraper as uww_scraper
import test_parsing as wikipedia_scraper
import clean_master as clean_master

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
    clean_master.execution_flow_clean_master()
elif choice == "4":
    clean_master.execution_flow_clean_master()
else:
    print("❌ Invalid entry selection. Shutting down pipeline execution environment.")