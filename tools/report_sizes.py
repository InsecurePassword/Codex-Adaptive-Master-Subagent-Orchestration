#!/usr/bin/env python3
"""Compare the current AMS package with the immediately preceding working candidate."""
from __future__ import annotations
import argparse,csv,hashlib,io,json
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'verification/fixtures/baseline-install-manifest-pr44-pre-corrections.txt'
CURRENT=ROOT/'install-manifest.txt'
BASE_LABEL='PR44 head f7f572d229efa6f93662b7239b1984985d02e4fb before required corrections'
EXTENSIONS=(ROOT/'extensions/ams-app-task-lane',ROOT/'extensions/ams-runtime-observation')

def manifest(path:Path)->dict[str,dict[str,Any]]:
    lines=path.read_text(encoding='utf-8').splitlines()
    if len(lines)<2 or lines[0]!='ams-install-manifest-v1' or not lines[1].startswith('version\t'): raise ValueError(path)
    out={}
    for line in lines[2:]:
        digest,length,repo_path=line.split('\t'); out[repo_path]={'sha256':digest,'bytes':int(length)}
    return out

def rec(path:Path)->dict[str,Any]:
    data=path.read_bytes(); return {'path':path.relative_to(ROOT).as_posix(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}

def build()->dict[str,Any]:
    before,after=manifest(BASE),manifest(CURRENT); rows=[]
    for path in sorted(set(before)|set(after)):
        b,a=before.get(path),after.get(path); bb=b['bytes'] if b else 0; ab=a['bytes'] if a else 0
        status='added' if b is None else 'removed' if a is None else 'unchanged' if b['sha256']==a['sha256'] else 'modified'
        rows.append({'path':path,'status':status,'baseline_bytes':bb,'candidate_bytes':ab,'delta_bytes':ab-bb,'baseline_sha256':b['sha256'] if b else None,'candidate_sha256':a['sha256'] if a else None})
    companions={}
    for ext in EXTENSIONS:
        items=[rec(p) for p in sorted(ext.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
        companions[ext.name]={'file_count':len(items),'bytes':sum(x['bytes'] for x in items),'files':items}
    bt=sum(x['bytes'] for x in before.values()); at=sum(x['bytes'] for x in after.values())
    return {'comparison_baseline':{'label':BASE_LABEL,'file_count':len(before),'bytes':bt},'candidate':{'version':'4.0','file_count':len(after),'bytes':at},'core_delta':{'file_count':len(after)-len(before),'bytes':at-bt,'percent':round((at-bt)*100/bt,4)},'core_files':rows,'companions':companions}

def csv_text(rows):
    h=io.StringIO(newline=''); fields=('path','status','baseline_bytes','candidate_bytes','delta_bytes','baseline_sha256','candidate_sha256'); w=csv.DictWriter(h,fieldnames=fields,lineterminator='\n'); w.writeheader(); w.writerows(rows); return h.getvalue()

def md_text(r):
    lines=['# AMS current-update bloat assessment','',f"- Working baseline: **{r['comparison_baseline']['bytes']:,} bytes / {r['comparison_baseline']['file_count']} files** (`{r['comparison_baseline']['label']}`).",f"- Current update: **{r['candidate']['bytes']:,} bytes / {r['candidate']['file_count']} files**.",f"- Delta: **{r['core_delta']['bytes']:+,} bytes / {r['core_delta']['file_count']:+d} files ({r['core_delta']['percent']:+.2f}%)**.",'','| File | Status | Baseline | Update | Delta |','|---|---:|---:|---:|---:|']
    for x in r['core_files']: lines.append(f"| `{x['path']}` | {x['status']} | {x['baseline_bytes']:,} | {x['candidate_bytes']:,} | {x['delta_bytes']:+,} |")
    lines+=['','## Separate companions','']
    for n,x in r['companions'].items(): lines.append(f"- `{n}`: **{x['bytes']:,} bytes / {x['file_count']} files**, excluded from core.")
    return '\n'.join(lines)+'\n'

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--format',choices=('json','csv','md','summary'),default='summary'); ap.add_argument('--output'); args=ap.parse_args(); r=build()
    text=json.dumps(r,indent=2,sort_keys=True)+'\n' if args.format=='json' else csv_text(r['core_files']) if args.format=='csv' else md_text(r) if args.format=='md' else f"Core package: {r['comparison_baseline']['bytes']} -> {r['candidate']['bytes']} ({r['core_delta']['bytes']:+d})\n"
    if args.output: Path(args.output).write_text(text,encoding='utf-8',newline='\n')
    else: print(text,end='')
    return 0
if __name__=='__main__': raise SystemExit(main())
