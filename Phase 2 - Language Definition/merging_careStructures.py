import pandas as pd
import os

# ==========================================
# 1. SETUP & LOADING
# ==========================================

file_residential = './datasets/ASSRESIDENZIALE001.csv'
file_semi_residential = './datasets/ASSSEMIRESIDENZIALE001.csv'
file_master_list = './datasets/SANSTRUT001.csv'
output_file = 'CareStructure_Merged.csv'

def load_dataset(path):
    try:
        # Load with standard comma separator and utf-8
        return pd.read_csv(path, sep=',', encoding='utf-8')
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return pd.DataFrame()

print("Loading datasets...")
df_res = load_dataset(file_residential)
df_semi = load_dataset(file_semi_residential)
df_master = load_dataset(file_master_list)

# ==========================================
# 2. PREPARE CARE STRUCTURE DATA
# ==========================================

# 2a. Residential
if not df_res.empty:
    df_res['CareType'] = 'Residential'
    if 'NUM_GG_ASSISTENZA' in df_res.columns:
        df_res['NumAssistanceDays'] = df_res['NUM_GG_ASSISTENZA']

# 2b. Semi-Residential
if not df_semi.empty:
    df_semi['CareType'] = 'Semi-Residential'
    if 'NUM_GIORNATE' in df_semi.columns:
        df_semi['NumAssistanceDays'] = df_semi['NUM_GIORNATE']

# 2c. Merge the two care datasets
df_care = pd.concat([df_res, df_semi], ignore_index=True)

# Filter valid IDs
if 'COD_STRUTTURA' in df_care.columns:
    df_care = df_care[df_care['COD_STRUTTURA'].notna()]
    # Ensure ID is the same type (int) for joining
    df_care['COD_STRUTTURA'] = df_care['COD_STRUTTURA'].astype(int)
else:
    print("Error: 'COD_STRUTTURA' missing in care files.")

# ==========================================
# 3. PREPARE MASTER LIST DATA
# ==========================================

# We only need the location/contact info from the master list
if not df_master.empty and 'COD_STRUTTURA' in df_master.columns:
    # Ensure ID is int
    df_master = df_master[df_master['COD_STRUTTURA'].notna()]
    df_master['COD_STRUTTURA'] = df_master['COD_STRUTTURA'].astype(int)
    
    # Select columns to bring over
    cols_to_join = [
        'COD_STRUTTURA', 
        'INDIRIZZO',      # Address
        'CAP',            # Postal Code
        'COMUNE',         # Municipality
        'TELEFONO',       # Phone
        'E_MAIL',         # Email
        'SITO_WEB',       # Website
        'LATITUDINE_P',   # Latitude
        'LONGITUDINE_P',  # Longitude
        'COMUNE'          # Municipality
    ]
    
    # Filter master list to just these columns
    # Use intersection to avoid errors if a column is missing
    valid_cols = [c for c in cols_to_join if c in df_master.columns]
    df_master_subset = df_master[valid_cols]
    
    # ==========================================
    # 4. JOIN (MERGE) DATASETS
    # ==========================================
    
    # Perform a LEFT JOIN on 'COD_STRUTTURA'
    # We want all CareStructures, and matching info from Master if available
    df_final = pd.merge(df_care, df_master_subset, on='COD_STRUTTURA', how='left')

    # Drop redundant columns
    cols_to_drop = ['NUM_GG_ASSISTENZA', 'NUM_GIORNATE', 'COD_STRUTTURA', 'COD_TIPO_ASSISTENZA', 'COD_TIPO_RAPPORTO', 'TIPO_STRUTTURA', 'ANNO']
    df_final.drop(columns=[c for c in cols_to_drop if c in df_care.columns], inplace=True)
    
    # ==========================================
    # 5. SAVE
    # ==========================================
    
    df_final.to_csv(output_file, index=False, encoding='utf-8', sep=',')
    
    print(f"\nSUCCESS: Joined Care Data with Master List.")
    print(f"Total rows: {len(df_final)}")
    print(f"Columns included: {df_final.columns.tolist()}")
    print(f"Saved to '{output_file}'")

else:
    print("Error: Master list is empty or missing 'COD_STRUTTURA'. Cannot join.")