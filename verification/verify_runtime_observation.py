#!/usr/bin/env python3
"""Adversarial fixtures for the optional AMS runtime-observation companion."""
from __future__ import annotations
import json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'extensions/ams-runtime-observation/tools/inspect-agent-runtime.py'
ID='11111111-1111-7111-8111-111111111111'

def write(path,model='gpt-5.6-terra',effort='high'):
    path.parent.mkdir(parents=True,exist_ok=True)
    records=[{'type':'response_item','payload':{'prompt':'DO_NOT_LEAK'}},{'type':'session_meta','payload':{'id':ID,'parent_thread_id':'00000000-0000-7000-8000-000000000000','agent_role':'ams_terra_high','agent_path':'/root/a','model_provider':'openai'}},{'type':'turn_context','payload':{'model':model,'effort':effort,'sandbox_policy':{'type':'danger-full-access'},'permission_profile':{'type':'disabled'},'cwd':'/fixture'}}]
    path.write_text(''.join(json.dumps(x)+'\n' for x in records),encoding='utf-8')

def run(root): return subprocess.run([sys.executable,str(SCRIPT),ID,'--sessions-dir',str(root)],text=True,capture_output=True)
class Observation(unittest.TestCase):
    def test_valid_allowlist_and_no_prompt(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/f'2026/08/03/rollout-x-{ID}.jsonl'; write(p); r=run(Path(td)); self.assertEqual(r.returncode,0,r.stderr); self.assertNotIn('DO_NOT_LEAK',r.stdout); data=json.loads(r.stdout); self.assertEqual(data['model'],'gpt-5.6-terra'); self.assertEqual(set(data),{'thread_id','parent_thread_id','agent_role','agent_path','model_provider','model','effort','sandbox_policy_type','permission_profile_type','cwd'})
    def test_duplicate_match_fails(self):
        with tempfile.TemporaryDirectory() as td:
            write(Path(td)/f'a/rollout-x-{ID}.jsonl'); write(Path(td)/f'b/rollout-y-{ID}.jsonl'); self.assertNotEqual(run(Path(td)).returncode,0)
    @unittest.skipIf(os.name=='nt','symlink fixture uses Unix semantics')
    def test_exact_symlink_match_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); target=root/'target.jsonl'; write(target); link=root/f'rollout-x-{ID}.jsonl'; link.symlink_to(target); r=run(root); self.assertNotEqual(r.returncode,0); self.assertIn('redirected',r.stderr)
    def test_invalid_json_fails_without_disclosure(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/f'rollout-x-{ID}.jsonl'; p.write_text('{"prompt":"SECRET"\n'); r=run(Path(td)); self.assertNotEqual(r.returncode,0); self.assertNotIn('SECRET',r.stderr+r.stdout)
    def test_conflicting_model_fails(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/f'rollout-x-{ID}.jsonl'; write(p); with_more={'type':'turn_context','payload':{'model':'gpt-5.6-sol','effort':'high','sandbox_policy':{'type':'danger-full-access'},'permission_profile':{'type':'disabled'},'cwd':'/fixture'}}; p.write_text(p.read_text()+json.dumps(with_more)+'\n'); self.assertNotEqual(run(Path(td)).returncode,0)
    def test_invalid_id_fails(self):
        r=subprocess.run([sys.executable,str(SCRIPT),'invalid','--sessions-dir',str(ROOT)],text=True,capture_output=True); self.assertNotEqual(r.returncode,0)
if __name__=='__main__': unittest.main()
