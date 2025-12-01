import pandas as pd
import numpy as np
import pickle
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_models():
    with open('models/ts_pct_model.pkl', 'rb') as f:
        m_ts = pickle.load(f)
    with open('models/ppg_per75_model.pkl', 'rb') as f:
        m_ppg = pickle.load(f)
    with open('models/ast_pct_model.pkl', 'rb') as f:
        m_ast = pickle.load(f)
    with open('models/model_metadata.pkl', 'rb') as f:
        meta = pickle.load(f)
    return m_ts, m_ppg, m_ast, meta

def prepare_features_for_prediction(row, target_metric):
    rs_metric = row[f'rs_{target_metric}']
    dcs = row['opp_def_context_score']
    usg = row['rs_usg_pct']
    interaction = rs_metric * dcs
    
    # Match training order: [metric, dcs, usg, interaction]
    return np.array([[rs_metric, dcs, usg, interaction]])

def main():
    try:
        model_ts, model_ppg, model_ast, metadata = load_models()
    except FileNotFoundError:
        logger.error("Models not found. Train first.")
        return

    df = pd.read_csv('data/training_dataset.csv')
    
    # Filter out small sample sizes (garbage time)
    # We apply the same filter as training to ensure scores are meaningful
    initial_len = len(df)
    df = df[df['po_minutes_total'] >= 50]
    logger.info(f"Filtered small samples (<50 mins) for scoring: {initial_len} -> {len(df)} rows")
    
    results = []
    
    for _, row in df.iterrows():
        # TS%
        f_ts = prepare_features_for_prediction(row, 'ts_pct')
        exp_ts = model_ts.predict(f_ts)[0]
        z_ts = (row['po_ts_pct'] - exp_ts) / metadata['ts_pct_rmse']
        
        # PPG
        f_ppg = prepare_features_for_prediction(row, 'ppg_per75')
        exp_ppg = model_ppg.predict(f_ppg)[0]
        z_ppg = (row['po_ppg_per75'] - exp_ppg) / metadata['ppg_per75_rmse']
        
        # AST%
        f_ast = prepare_features_for_prediction(row, 'ast_pct')
        exp_ast = model_ast.predict(f_ast)[0]
        z_ast = (row['po_ast_pct'] - exp_ast) / metadata['ast_pct_rmse']
        
        # Composite (35% Eff, 25% Vol, 25% Cre, 15% Stab - Stab is 0 for now)
        composite = (0.35 * z_ts) + (0.25 * z_ppg) + (0.25 * z_ast)
        
        results.append({
            'PLAYER_ID': row['PLAYER_ID'],
            'PLAYER_NAME': row['PLAYER_NAME'],
            'SEASON': row['SEASON'],
            'OPPONENT': row['OPPONENT_ABBREV'],
            'RS_TS': row['rs_ts_pct'],
            'PO_TS': row['po_ts_pct'],
            'EXP_TS': exp_ts,
            'Z_EFF': z_ts,
            'Z_VOL': z_ppg,
            'Z_CRE': z_ast,
            'RESILIENCE_SCORE': composite
        })
        
    res_df = pd.DataFrame(results).sort_values('RESILIENCE_SCORE', ascending=False)
    Path("results").mkdir(exist_ok=True)
    res_df.to_csv('results/resilience_scores_all.csv', index=False)
    
    logger.info(f"✅ Scores calculated for {len(res_df)} records.")
    print(res_df.head(10))

if __name__ == "__main__":
    main()
