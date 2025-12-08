import pandas as pd
import os

# ==========================================
# 1. SETUP FILES
# ==========================================

file_care = 'CareStructure_Merged.csv'
file_hosp = 'Hospitals_Merged.csv'
file_master = './datasets/SANSTRUT001.csv'
output_file = 'HealthFacilities_Cleaned.csv'

def load_dataset(path):
    try:
        # Load with standard comma separator and utf-8
        return pd.read_csv(path, sep=',', encoding='utf-8')
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return pd.DataFrame()

print("Loading datasets...")
df_care = load_dataset(file_care)
df_hosp = load_dataset(file_hosp)
df_master = load_dataset(file_master)

# ==========================================
# 2. IDENTIFY IDS TO REMOVE
# ==========================================

# We want to remove any structure appearing in the specific lists from the master list
ids_to_remove = set()

# Get IDs from Care Structures
if 'COD_STRUTTURA_OD' in df_care.columns:
    care_ids = df_care['COD_STRUTTURA_OD'].unique()
    ids_to_remove.update(care_ids)
    print(f"Found {len(care_ids)} Care Structure IDs to remove.")

# Get IDs from Hospitals
if 'COD_STRUTTURA_OD' in df_hosp.columns:
    hosp_ids = df_hosp['COD_STRUTTURA_OD'].unique()
    ids_to_remove.update(hosp_ids)
    print(f"Found {len(hosp_ids)} Hospital IDs to remove.")

print(f"Total unique IDs to remove from Master List: {len(ids_to_remove)}")

# ==========================================
# 3. FILTER MASTER LIST
# ==========================================

if not df_master.empty and 'COD_STRUTTURA_OD' in df_master.columns:
    initial_count = len(df_master)
    
    # Keep rows where ID is NOT in the removal list
    # The ~ operator inverts the boolean mask (Not IsIn)
    df_filtered = df_master[~df_master['COD_STRUTTURA_OD'].isin(ids_to_remove)]
    
    final_count = len(df_filtered)
    removed_count = initial_count - final_count
    
    print(f"\nFiltering Complete.")
    print(f"Original Master List count: {initial_count}")
    print(f"Rows removed: {removed_count}")
    print(f"Final Master List count: {final_count}")
    
    # Save to new file
    df_filtered.to_csv(output_file, index=False, encoding='utf-8', sep=',')
    print(f"\nSUCCESS: Filtered master list saved to '{output_file}'")
    
else:
    print("Error: Master list empty or missing 'COD_STRUTTURA_OD'.")