import pandas as pd
import os

# ==========================================
# 1. SETUP & LOADING
# ==========================================

file_pharmacy = './datasets/FARM001.csv'
file_parapharmacy = './datasets/PARAFARM001.csv'
output_file = 'Dispensary_Merged.csv'

def load_dataset(path):
    try:
        # Load with standard comma separator and utf-8
        return pd.read_csv(path, sep=',', encoding='utf-8')
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return pd.DataFrame()

print("Loading datasets...")
df_farm = load_dataset(file_pharmacy)
df_parafarm = load_dataset(file_parapharmacy)

# ==========================================
# 2. ALIGNMENT & DISCRIMINATOR
# ==========================================

# 2a. Process Pharmacies
if not df_farm.empty:
    df_farm['dispensaryType'] = 'Pharmacy'

# 2b. Process Parapharmacies
if not df_parafarm.empty:
    df_parafarm['dispensaryType'] = 'Parapharmacy'
    
    # ALIGNMENT: Rename Parapharmacy columns to match Pharmacy columns 
    # specifically mapping the _OD code this time.
    df_parafarm.rename(columns={
        'COD_PARAFARMACIA_OD': 'COD_FARMACIA_OD', # Align Open Data ID
        'PARAFARMACIA': 'FARMACIA'              # Align Name
    }, inplace=True)

# ==========================================
# 3. MERGE
# ==========================================

df_final = pd.concat([df_farm, df_parafarm], ignore_index=True)

# ==========================================
# 4. ADD MISSING COLUMNS
# ==========================================

# Create empty placeholders for requested attributes not in source files
missing_cols = ['TELEFONO', 'SITO_WEB', 'EMAIL', 'ASSISTENZA'] 
for col in missing_cols:
    df_final[col] = None

# ==========================================
# 5. FILTERING (KEEPING REQUESTED INFO)
# ==========================================

# Updated list using COD_FARMACIA_OD
cols_to_keep = [
    'COD_FARMACIA_OD',  # structureCode
    'FARMACIA',         # name
    'INDIRIZZO',        # address
    'CAP',              # CAP
    'LATITUDINE_P',     # latitude
    'LONGITUDINE_P',    # longitude
    'TELEFONO',         # phone (Empty)
    'SITO_WEB',         # website (Empty)
    'EMAIL',            # email (Empty)
    'ASSISTENZA',         # serviceName (Empty)
    'dispensaryType',   # dispensaryType (Created)
    'IVA'               # IVA
]

# Select only existing columns
final_cols = [c for c in cols_to_keep if c in df_final.columns]
df_final = df_final[final_cols]

# ==========================================
# 6. SAVING
# ==========================================

df_final.to_csv(output_file, index=False, encoding='utf-8', sep=',')

print(f"\nSUCCESS: Merged {len(df_final)} rows.")
print(f"Kept columns: {df_final.columns.tolist()}")
print(f"Saved to '{output_file}'")