"""Independent audit of actual SQL cohorts, held-out scores and shipped weights.
Runs against real data/artifacts; does not retrain or substitute model predictions.
"""
from pathlib import Path
import hashlib
import json
import sqlite3
import sys
import zipfile
import numpy as np
import pandas as pd
import torch
from sklearn.metrics import roc_auc_score, average_precision_score, precision_recall_curve

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.ml.network import build_model


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def close(a, b, tolerance=1e-10):
    np.testing.assert_allclose(a, b, atol=tolerance, rtol=tolerance)


def measured(y, score, threshold):
    predicted = score >= threshold
    tn = int(((y == 0) & ~predicted).sum())
    fp = int(((y == 0) & predicted).sum())
    fn = int(((y == 1) & ~predicted).sum())
    tp = int(((y == 1) & predicted).sum())
    return dict(n=len(y), positive=int(y.sum()), prevalence=float(y.mean()),
        roc_auc=roc_auc_score(y, score), average_precision=average_precision_score(y, score),
        precision=tp/max(tp+fp, 1), sensitivity=tp/max(tp+fn, 1), specificity=tn/max(tn+fp, 1),
        f1=2*tp/max(2*tp+fp+fn, 1), accuracy=(tn+tp)/len(y),
        brier=float(np.mean((score.astype(float)-y)**2)), confusion_matrix=[[tn,fp],[fn,tp]])


def audit():
    folder = ROOT/'results/benchmark/full'
    record = json.loads((folder/'benchmark-results.json').read_text())
    manifest = json.loads((ROOT/'results/benchmark/database-manifest.json').read_text())
    assert len(record['runs']) == 72
    assert len({(r['dataset'],r['model_id'],r['seed']) for r in record['runs']}) == 72
    arrays, cohort_checks = {}, []
    connection = sqlite3.connect(ROOT/'data/database/diabetes.sqlite3')
    for dataset, metadata in manifest.items():
        names = metadata['features']
        prepared = pd.read_sql_query('SELECT * FROM prepared_'+dataset+' ORDER BY sample_id',connection)
        source = pd.read_sql_query('SELECT * FROM raw_'+dataset+' ORDER BY rowid',connection)
        assert sha(ROOT/'data/raw'/f'{dataset}.csv') == metadata['source_csv_sha256']
        assert len(source) == metadata['raw_rows'] and len(prepared) == metadata['clean_rows']
        assert not {'patient_nbr','encounter_id'}.intersection(names)
        if dataset == 'hospital':
            original = source.loc[source.gender.isin(['Female','Male'])].copy()
            original['Gender'] = original.gender.map({'Female':0,'Male':1})
            original['AgeGroup'] = original.age.str.extract(r'\[(\d+)-')[0].astype(int)//10+1
            target = (original.readmitted == '<30').astype(int)
            groups = [set(original.patient_nbr.to_numpy()[prepared.split.to_numpy()==s]) for s in ['train','val','test']]
            assert not (groups[0]&groups[1] or groups[0]&groups[2] or groups[1]&groups[2])
        else:
            original = source.copy()
            if dataset == 'early':
                original['Gender'] = original.Gender.map({'Female':0,'Male':1})
                for name in names[2:]: original[name] = original[name].map({'No':0,'Yes':1})
                original['class'] = original['class'].map({'Negative':0,'Positive':1})
            target_name = {'cdc':'Diabetes_binary','pima':'Outcome','early':'class'}[dataset]
            # Exact feature grouping is independent of the production hash grouping.
            conflicting = original.groupby(names,dropna=False)[target_name].transform('nunique')>1
            original = original.loc[~conflicting].drop_duplicates(names)
            target = original[target_name]
            assert not prepared.duplicated(names).any()
        np.testing.assert_array_equal(original[names].to_numpy(dtype=float), prepared[names].to_numpy(dtype=float))
        np.testing.assert_array_equal(target.to_numpy(), prepared.target.to_numpy())
        assert prepared.groupby('group_token').split.nunique().max() == 1
        prep = metadata['preprocessing']
        data = prepared[names].to_numpy(float,copy=True)
        for name in prep['zero_as_missing']: data[data[:,names.index(name)]==0,names.index(name)] = np.nan
        train = data[prepared.split.to_numpy()=='train']
        median = np.nanmedian(train,axis=0)
        filled = np.where(np.isnan(train),median,train)
        mean, scale = filled.mean(axis=0), filled.std(axis=0)
        scale[scale<1e-8]=1
        close(median,prep['median']);close(mean,prep['mean']);close(scale,prep['scale'])
        arrays[dataset] = {}
        for split in ['val','test']:
            frame = prepared.loc[prepared.split==split].sort_values('split_order')
            raw = frame[names].to_numpy(float,copy=True)
            for name in prep['zero_as_missing']: raw[raw[:,names.index(name)]==0,names.index(name)] = np.nan
            # Forward parity uses the recorded scaler after independent train-only checks above.
            x = np.ascontiguousarray(((np.where(np.isnan(raw),prep['median'],raw)-prep['mean'])/prep['scale']).astype(np.float32))
            arrays[dataset][split] = (x, frame.target.to_numpy(int))
        cohort_checks.append({'dataset':dataset,'clean_rows':len(prepared),'source_rows':len(source),
            'exact_source_preparation':'passed','group_disjoint':'passed','train_only_preprocessing':'passed'})
    connection.close()
    run_checks, neural_checks = [], 0
    for row in record['runs']:
        path = ROOT/row['prediction_file']; assert sha(path) == row['prediction_sha256']
        with np.load(path) as p:
            for split, key, metric_key in [('val','validation_score','validation'),('test','test_score','test')]:
                x,y = arrays[row['dataset']][split]; score = p[key]
                np.testing.assert_array_equal(y,p['y_'+split])
                assert np.isfinite(score).all() and ((score>=0)&(score<=1)).all()
                observed = measured(y,score,row[metric_key]['threshold'])
                for metric,value in observed.items(): close(value,row[metric_key][metric],1e-7)
            pv,rv,tv = precision_recall_curve(p['y_val'],p['validation_score'])
            f = 2*pv[:-1]*rv[:-1]/np.maximum(pv[:-1]+rv[:-1],1e-12)
            assert row['validation']['threshold'] == row['test']['threshold'] == float(tv[np.argmax(f)])
            if row['model_family']=='deep_learning':
                best,epoch=-1.,0
                for item in row['history']:
                    if item['val_roc_auc']>best+1e-5: best,epoch=item['val_roc_auc'],item['epoch']
                assert row['best_epoch']==epoch
                close(best,row['validation']['roc_auc'])
                weights=ROOT/row['weights'];assert sha(weights)==row['weights_sha256']
                xt,yt = arrays[row['dataset']]['test']
                model=build_model(xt.shape[1],row['model_id'])
                model.load_state_dict(torch.load(weights,map_location='cpu',weights_only=True));model.eval()
                with torch.inference_mode(): fresh=torch.sigmoid(model(torch.from_numpy(xt))).numpy()
                np.testing.assert_array_equal(fresh,p['test_score']);neural_checks+=1
        run_checks.append({'dataset':row['dataset'],'model':row['model_id'],'seed':row['seed'],'all_metrics':'passed','validation_threshold':'passed'})
    summary=pd.read_csv(folder/'summary.csv')
    assert len(summary)==24
    for row in summary.to_dict('records'):
        runs=[r for r in record['runs'] if r['dataset']==row['dataset'] and r['model_id']==row['model_id']]
        assert len(runs)==3
        for metric in ['roc_auc','average_precision','f1','precision','sensitivity','specificity','accuracy','brier','train_and_evaluate_seconds']:
            values=[r[metric] if metric=='train_and_evaluate_seconds' else r['test'][metric] for r in runs]
            close(np.mean(values),row[metric+'_mean']);close(np.std(values,ddof=1),row[metric+'_std'])
    for dataset in ['pima','early']:
        candidates=[r for r in record['runs'] if r['dataset']==dataset and r['model_family']=='deep_learning']
        best=max(candidates,key=lambda r:r['validation']['roc_auc'])
        metadata=json.loads((ROOT/'models'/dataset/'metadata.json').read_text())
        assert (metadata['model_id'],metadata['seed'])==(best['model_id'],best['seed'])
        assert sha(ROOT/'models'/dataset/'model.pt')==best['weights_sha256']
    legacy=json.loads((ROOT/'results/benchmark/legacy-preservation.json').read_text())['files']
    backup=Path('/work/upgrade-261106/project01-before-upgrade.zip')
    with zipfile.ZipFile(backup) as z:
        for item in legacy:
            current=sha(ROOT/item['path']);assert current==item['sha256']
            name=next(n for n in z.namelist() if n.endswith('/'+item['path']))
            assert hashlib.sha256(z.read(name)).hexdigest()==current
    result={'status':'passed','scope':'independent recomputation from real SQL and score/weight artifacts',
        'cohorts':cohort_checks,'runs':run_checks,'neural_weight_forward_checks':neural_checks,
        'summary_groups_checked':24,'legacy_files_compared_to_original_zip':len(legacy),
        'serving_selection_validation_only':'passed','limitations':['Tree ensembles not shipped, so tree prediction artifacts checked for metrics but not refitted.','Seed SD on fixed split does not estimate sampling uncertainty.']}
    target=ROOT/'results/benchmark/full/independent-audit.json'
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print({k:v for k,v in result.items() if k not in {'runs','cohorts','limitations'}})


if __name__=='__main__': audit()
