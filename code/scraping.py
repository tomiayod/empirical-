import pandas as pd
from bs4 import BeautifulSoup, Comment
import undetected_chromedriver as uc
import time

# Setup Chrome options
options = uc.ChromeOptions()
#options.add_argument("--headless")  # Optional: run headless
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# URL for Mohamed Salah's page
url = "https://fbref.com/en/players/e342ad68/Mohamed-Salah"

# List of table IDs we want to extract
table_ids = [
    'stats_standard_dom_lg',
    'stats_shooting_dom_lg',
    'stats_passing_dom_lg',
    'stats_gca_dom_lg',
    'stats_defense_dom_lg',
    'stats_possession_dom_lg',
    'stats_misc_dom_lg',
    'scout_full_AM',
    'stats_player_summary_e342ad68'
]

try:
    # Launch driver using undetected_chromedriver
    print(f"Launching Chrome and navigating to {url}")
    driver = uc.Chrome(options=options)
    driver.get(url)
    time.sleep(5)  # Give the page time to fully load

    # Get full HTML (including comments)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")

    # Extract comments from page (FBref often wraps tables in comments)
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    
    extracted_tables = {}
    
    # First check visible tables (not in comments)
    for table_id in table_ids:
        print(f"🔍 Looking for table: {table_id}")
        table = soup.find("table", id=table_id)
        
        if table:
            print(f"✅ Found {table_id} directly in the page, parsing...")
            df = pd.read_html(str(table))[0]
            df.to_csv(f"salah_{table_id}.csv", index=False)
            extracted_tables[table_id] = df
            print(f"💾 Saved to salah_{table_id}.csv")
            continue
            
        # If not found directly, look in comments
        found = False
        for comment in comments:
            comment_soup = BeautifulSoup(comment, "html.parser")
            table = comment_soup.find("table", id=table_id)
            
            if table:
                print(f"✅ Found {table_id} in comments, parsing...")
                df = pd.read_html(str(table))[0]
                df.to_csv(f"salah_{table_id}.csv", index=False)
                extracted_tables[table_id] = df
                print(f"💾 Saved to salah_{table_id}.csv")
                found = True
                break
                
        if not found:
            print(f"❌ Table {table_id} not found")

    # Find all tables inside comments to help identify available tables
    all_found_tables = []
    for comment in comments:
        comment_soup = BeautifulSoup(comment, "html.parser")
        for table in comment_soup.find_all("table"):
            if table.get("id"):
                all_found_tables.append(table.get("id"))
    
    print("\n🧾 Available table IDs found in comments:")
    print(all_found_tables)

finally:
    driver.quit()
    print("🚪 Browser closed")

print("✅ All done!")