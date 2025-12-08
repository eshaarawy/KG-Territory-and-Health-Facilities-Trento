import pandas as pd
import numpy as np
import re
import os

# Define the service to be excluded from the merged list
SERVICE_EXCLUSION = 'PSICOLOGIA CLINICA'

def normalize_key(s):
    """
    Normalizes address strings for reliable matching (removes spaces, punctuation, lowercases).
    """
    if pd.isna(s): return ""
    s = str(s).lower().strip()
    s = re.sub(r'[\s,\.\-]', '', s)
    return s

def join_services(series):
    """
    Joins unique service descriptions, filtering out the specified exclusion service.
    """
    # Filter out services that match the exclusion string (case insensitive)
    unique_services = series.dropna().astype(str).str.upper().unique()
    valid_services = [s for s in unique_services if SERVICE_EXCLUSION not in s]
    
    # Return services sorted and joined with original case (uppercase in source data)
    return ' | '.join(sorted(valid_services))

def main():
    # --- Configuration ---
    dtype_map = {
        'TELEFONO': str, 'CAP': str, 'COD_COMUNE': str, 'COD_ASL': str,
        'COD_OSP_OD': str, 'COD_STRUTTURA_OD': str
    }
    
    # Input/Output Files (All paths start with ./datasets/)
    FILE_OSP = './datasets/OSPEDALI001.csv'
    FILE_SAN = './datasets/SANSTRUT001.csv'
    FILES_EXCLUDE = [
        './datasets/ASSRESIDENZIALE001.csv', './datasets/ASSSEMIRESIDENZIALE001.csv',
        './datasets/FARM001.csv', './datasets/PARAFARM001.csv'
    ]
    FILE_OUTPUT = './datasets/Hospitals_Merged.csv'

    # --- 1. Load Data & Build Exclusion Blocklist ---
    try:
        df_osp = pd.read_csv(FILE_OSP, dtype=dtype_map)
        df_san = pd.read_csv(FILE_SAN, dtype=dtype_map)
    except FileNotFoundError as e:
        print(f"Error loading main files: {e}")
        return

    exclusion_ids = set()
    for f in FILES_EXCLUDE:
        try:
            temp_df = pd.read_csv(f, nrows=5)
            if 'COD_STRUTTURA_OD' in temp_df.columns:
                full_df = pd.read_csv(f, usecols=['COD_STRUTTURA_OD'])
                exclusion_ids.update(full_df['COD_STRUTTURA_OD'].unique())
        except Exception:
            pass

    # --- 2. Apply Filters (Scope Cleaning) ---
    blocklist_regex = r'RIAB|RSA\b|RESIDENZIALE|FARMACIA|PARAFARMACIA'
    
    df_osp_clean = df_osp[~df_osp['OSPEDALE'].str.contains(blocklist_regex, case=False, na=False)].copy()
    
    df_san_clean = df_san[~df_san['COD_STRUTTURA_OD'].isin(exclusion_ids)].copy()
    df_san_clean = df_san_clean[~df_san_clean['STRUTTURA'].str.contains(blocklist_regex, case=False, na=False)].copy()

    # --- 3. Match Keys & Aggregate SANSTRUT Data ---
    df_osp_clean['match_key'] = df_osp_clean['INDIRIZZO'].apply(normalize_key) + "_" + df_osp_clean['COD_COMUNE']
    df_san_clean['match_key'] = df_san_clean['INDIRIZZO'].apply(normalize_key) + "_" + df_san_clean['COD_COMUNE']

    san_agg_cols = ['ASSISTENZA', 'TIPO_RAPPORTO', 'COD_STRUTTURA_OD', 'STRUTTURA', 'INDIRIZZO', 
                    'COMUNE', 'CAP', 'TELEFONO', 'SITO_WEB', 'E_MAIL', 'LATITUDINE_P', 
                    'LONGITUDINE_P', 'COD_ASL', 'TIPO_STRUTTURA']
    
    agg_dict = {col: join_services if col == 'ASSISTENZA' else 'first' for col in san_agg_cols}
    san_agg = df_san_clean.groupby('match_key').agg(agg_dict).reset_index()

    # --- 4. Merge OSPEDALI with SANSTRUT ---
    # Suffixes are applied to overlapping columns like COMUNE, INDIRIZZO, etc.
    merged_df = pd.merge(df_osp_clean, san_agg, on='match_key', how='left', suffixes=('_OSP', '_SAN'))

    # --- 5. Find "Hidden" Hospitals in SANSTRUT (Unmatched) ---
    include_regex = r'OSPEDALE|CASA DI CURA|CLINICA|POLICLINICO|PRESIDIO'
    san_hospitals = df_san_clean[df_san_clean['STRUTTURA'].str.contains(include_regex, case=False, na=False)].copy()
    
    matched_keys = set(df_osp_clean['match_key'])
    san_unmatched = san_hospitals[~san_hospitals['match_key'].isin(matched_keys)].copy()
    san_unmatched_agg = san_unmatched.groupby('match_key').agg(agg_dict).reset_index()

    # --- 6. Map to Final Schema (Original Italian Headers) ---
    def map_row(row, source_type):
        data = {}
        # Columns must be listed in the desired final order
        target_cols = ['COD_STRUTTURA_OD', 'STRUTTURA', 'COMUNE', 'INDIRIZZO', 'CAP', 
                       'LATITUDINE_P', 'LONGITUDINE_P', 'TELEFONO', 'SITO_WEB', 
                       'E_MAIL', 'ASSISTENZA', 'COD_ASL', 'TIPO_STRUTTURA', 'TIPO_RAPPORTO']
        
        if source_type == 'OSPEDALI':
            data['COD_STRUTTURA_OD'] = row['COD_OSP_OD']
            data['STRUTTURA'] = row['OSPEDALE']
            data['COMUNE'] = row['COMUNE_OSP']
            data['INDIRIZZO'] = row['INDIRIZZO_OSP']
            data['CAP'] = row['CAP_OSP']
            data['LATITUDINE_P'] = row['LATITUDINE_P_OSP']
            data['LONGITUDINE_P'] = row['LONGITUDINE_P_OSP']
            data['TELEFONO'] = row['TELEFONO_OSP']
            data['SITO_WEB'] = row['SITO_WEB_OSP']
            data['E_MAIL'] = row['E_MAIL_OSP']
            data['COD_ASL'] = row['COD_ASL_OSP']
            data['TIPO_STRUTTURA'] = row['TIPO_OSP']
            
            # Merged fields (no suffix on ASSISTENZA/TIPO_RAPPORTO since they weren't in OSPEDALI)
            data['ASSISTENZA'] = row['ASSISTENZA']
            data['TIPO_RAPPORTO'] = row['TIPO_RAPPORTO']

        elif source_type == 'SANSTRUT':
            # Direct mapping from the aggregated SANSTRUT data
            for col in target_cols:
                if col in row:
                    data[col] = row[col]
            
        return pd.Series(data)[target_cols]

    # Apply Mapping
    df_part1 = merged_df.apply(lambda r: map_row(r, 'OSPEDALI'), axis=1)
    df_part2 = san_unmatched_agg.apply(lambda r: map_row(r, 'SANSTRUT'), axis=1)
    
    # Combine
    final_df = pd.concat([df_part1, df_part2], ignore_index=True)

    # --- 7. Final Formatting & Save ---
    final_df['LATITUDINE_P'] = pd.to_numeric(final_df['LATITUDINE_P'], errors='coerce')
    final_df['LONGITUDINE_P'] = pd.to_numeric(final_df['LONGITUDINE_P'], errors='coerce')

    final_df.to_csv(FILE_OUTPUT, index=False)
    
    print(f"Successfully processed {len(final_df)} hospitals.")
    print(f"File saved to: {FILE_OUTPUT}")
    print("\n--- Hospitals Merged Data Preview ---")
    print(final_df.head())