#!/usr/bin/env python3
"""Integration tests for install_package.py using only the Python standard library."""
from __future__ import annotations
import contextlib, importlib.util, io, json, os, shutil, socket, subprocess, sys, tempfile, time, tomllib
from pathlib import Path
from types import ModuleType

sys.dont_write_bytecode = True
ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'scripts'/'install_package.py'
PLUGIN=json.loads((ROOT/'.codex-plugin/plugin.json').read_text(encoding='utf-8'))['name']
PACKAGE_OPTION_LABEL=(ROOT/'PACKAGE-OPTION').read_text(encoding='utf-8').strip()
OPTION=PACKAGE_OPTION_LABEL.split()[1]
MANAGED='# managed-by: adaptive-master-subagent-orchestration'
sys.path.insert(0,str(ROOT/'scripts'))
from process_utils import run_bounded
TIMEOUT=60
ALL_PLUGIN_NAMES={
'adaptive-master-subagent-orchestration-option-a-two-skill',
'adaptive-master-subagent-orchestration-option-b-unified',
'adaptive-master-subagent-orchestration-option-c-installer-required',
'adaptive-master-subagent-orchestration-option-a-modular',
'adaptive-master-subagent-orchestration-option-c-lean',
'adaptive-master-subagent-orchestration',
}

def require(condition: bool, message: str)->None:
    if not condition: raise AssertionError(message)

def command(home: Path,*args:str)->list[str]:
    return [sys.executable,'-B','-E','-s','-S',str(SCRIPT),'--home',str(home),*args]

def run(home: Path,*args:str,env:dict[str,str]|None=None,expect:int=0)->str:
    merged=dict(os.environ); merged['CODEX_HOME']=str(home/'.codex')
    if env: merged.update(env)
    try:
        result=run_bounded(command(home,*args),timeout=TIMEOUT,text=True,capture_output=True,check=False,env=merged,stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired as exc:
        raise AssertionError(f'installer timed out: {args}') from exc
    out=(result.stdout or '')+(result.stderr or '')
    if result.returncode!=expect:
        raise AssertionError(f'installer returned {result.returncode}, expected {expect}: {args}\n{out}')
    return out

def market(home:Path)->dict[str,object]:
    return json.loads((home/'.agents/plugins/marketplace.json').read_text(encoding='utf-8'))

def active(home:Path)->list[str]:
    p=home/'.agents/plugins/plugins'
    return sorted(x.name for x in p.iterdir() if x.name in ALL_PLUGIN_NAMES) if p.is_dir() else []

def load_module()->ModuleType:
    spec=importlib.util.spec_from_file_location(f'install_under_test_{OPTION}',SCRIPT)
    if spec is None or spec.loader is None: raise AssertionError('cannot load installer')
    module=importlib.util.module_from_spec(spec); sys.modules[spec.name]=module; spec.loader.exec_module(module); return module

def test_manifest_strict(base:Path)->None:
    module=load_module()
    module.validate_manifest(ROOT)
    extra=ROOT/'unexpected-audit-file.tmp'
    extra.write_text('x',encoding='utf-8')
    try:
        try: module.validate_manifest(ROOT)
        except SystemExit as exc: require('unlisted' in str(exc),'unlisted file error unclear')
        else: raise AssertionError('unlisted file was accepted')
    finally: extra.unlink()
    generated=ROOT/'scripts/__pycache__/unexpected.pyc'
    generated.parent.mkdir(exist_ok=True)
    generated.write_bytes(b'generated')
    try:
        try: module.validate_manifest(ROOT)
        except SystemExit as exc: require('generated Python artifact' in str(exc),'generated-artifact error unclear')
        else: raise AssertionError('generated artifact was accepted')
    finally:
        generated.unlink()
        generated.parent.rmdir()

def test_rollback(base:Path)->None:
    module=load_module(); home=base/'rollback'; args=module.parse_args(['--home',str(home),'--exclude-spark','--upgrade-managed'])
    original=module.run_bootstrap; calls=0
    def failing(*a,**kw):
        nonlocal calls
        calls+=1
        if kw.get('dry_run'): return original(*a,**kw)
        raise SystemExit('injected profile failure')
    module.run_bootstrap=failing
    try:
        try: module.install(args)
        except SystemExit as exc: require('injected profile failure' in str(exc),'wrong rollback failure')
        else: raise AssertionError('rollback injection did not fail')
    finally: module.run_bootstrap=original
    require(active(home)==[],'rollback left active plugin')
    mp=home/'.agents/plugins/marketplace.json'
    require(not mp.exists(),'rollback left marketplace')
    require(not (home/'.codex/ams-orchestration.toml').exists(),'rollback left config')
    agents=home/'.codex/agents'
    require(not agents.exists() or not list(agents.glob('ams_*.toml')),'rollback left profiles')


def test_rollback_reports_backup_restage_failure(base:Path)->None:
    module=load_module(); home=base/'rollback-restage'
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        module.install(module.parse_args(['--home',str(home),'--exclude-spark','--upgrade-managed']))
    installed=home/'.agents/plugins/plugins'/PLUGIN
    (installed/'README.md').write_text('locally changed installed copy\n',encoding='utf-8')
    original_bootstrap=module.run_bootstrap; original_replace=module.os.replace
    def failing_bootstrap(*a,**kw):
        if kw.get('dry_run'): return original_bootstrap(*a,**kw)
        raise SystemExit('injected profile failure after plugin backup')
    def failing_replace(src,dst):
        src_path=Path(src); dst_path=Path(dst)
        if src_path.parent.name=='backups' and '.ams-transaction-' in str(dst_path) and 'old-plugins' in dst_path.parts:
            raise OSError('injected backup restage failure')
        return original_replace(src,dst)
    module.run_bootstrap=failing_bootstrap; module.os.replace=failing_replace
    try:
        try: module.install(module.parse_args(['--home',str(home),'--exclude-spark','--upgrade-managed']))
        except SystemExit as exc:
            text=str(exc); require('rollback also reported' in text and 'restage plugin backup' in text,'backup restage failure was hidden')
        else: raise AssertionError('backup restage failure test did not fail')
    finally:
        module.run_bootstrap=original_bootstrap; module.os.replace=original_replace
    backups=home/'.agents/plugins/backups'
    require(backups.is_dir() and list(backups.iterdir()),'failed restage did not preserve recoverable backup')

def test_lock(base:Path)->None:
    home=base/'lock'; root=home/'.agents/plugins'; root.mkdir(parents=True)
    lock=root/'.ams-install.lock'; lock.write_text(json.dumps({'pid':os.getpid(),'host':socket.gethostname()})+'\n',encoding='utf-8')
    old=time.time()-3*60*60; os.utime(lock,(old,old))
    out=run(home,'--exclude-spark',expect=1); require('appears to be active' in out,'live lock not enforced'); require(lock.exists(),'live lock removed')
    lock.write_text(json.dumps({'pid':99999999,'host':socket.gethostname()})+'\n',encoding='utf-8'); os.utime(lock,(old,old))
    run(home,'--exclude-spark'); require(not lock.exists(),'dead stale lock not removed')
    lock.mkdir()
    out=run(home,'--exclude-spark',expect=1); require('not a regular file' in out,'non-file install lock error was unclear')
    lock.rmdir()
    lock.write_text('{malformed',encoding='utf-8'); os.utime(lock,(old,old))
    run(home,'--exclude-spark'); require(not lock.exists(),'malformed stale install lock was not recovered')
    if hasattr(os,'symlink'):
        target=root/'install-lock-target'; target.write_text('target',encoding='utf-8')
        try: lock.symlink_to(target)
        except OSError: pass
        else:
            out=run(home,'--exclude-spark',expect=1); require('not a regular file' in out,'install lock symlink error was unclear'); lock.unlink()
    module=load_module(); permission_root=base/'permission-install-lock'; permission_lock=permission_root/'.ams-install.lock'
    original_open=module.os.open
    def denied_open(path,*args,**kwargs):
        if Path(path)==permission_lock: raise PermissionError('injected install lock creation denial')
        return original_open(path,*args,**kwargs)
    module.os.open=denied_open
    try:
        try:
            with module.install_lock(permission_root): pass
        except SystemExit as exc: require('Unable to create install lock path' in str(exc),f'install lock creation denial was unclear: {exc}')
        else: raise AssertionError('install lock creation denial was not reported')
    finally: module.os.open=original_open
    permission_root.mkdir(parents=True,exist_ok=True); permission_lock.write_text('{}\n',encoding='utf-8')
    original_lstat=module.Path.lstat
    def denied_lstat(self,*args,**kwargs):
        if self==permission_lock: raise PermissionError('injected install lock inspection denial')
        return original_lstat(self,*args,**kwargs)
    module.Path.lstat=denied_lstat
    try:
        try:
            with module.install_lock(permission_root): pass
        except SystemExit as exc: require('Unable to inspect install lock path' in str(exc),f'install lock inspection denial was unclear: {exc}')
        else: raise AssertionError('install lock inspection denial was not reported')
    finally:
        module.Path.lstat=original_lstat; permission_lock.unlink(missing_ok=True)
    cleanup_root=base/'cleanup-install-lock'; cleanup_lock=cleanup_root/'.ams-install.lock'
    try:
        with module.install_lock(cleanup_root):
            require(cleanup_lock.exists(),'install lock was not created'); raise RuntimeError('injected install operation failure')
    except RuntimeError: pass
    require(not cleanup_lock.exists(),'install lock was not cleaned after failure')

def main()->int:
    with tempfile.TemporaryDirectory(prefix=f'ams-install-{OPTION}-') as tmp:
        base=Path(tmp)
        test_manifest_strict(base)
        home=base/'home'
        out=run(home,'--dry-run','--exclude-spark','--intensity','heavy')
        require('would-install plugin' in out,'dry-run output unclear'); require(not (home/'.agents').exists(),'dry-run mutated home')
        run(home,'--exclude-spark','--intensity','heavy','--upgrade-managed')
        require(active(home)==[PLUGIN],'install did not activate only selected plugin')
        plugins=[x['name'] for x in market(home)['plugins'] if isinstance(x,dict) and x.get('name') in ALL_PLUGIN_NAMES]
        require(plugins==[PLUGIN],'marketplace registration wrong')
        config_path=home/'.codex/ams-orchestration.toml'
        config_text=config_path.read_text(encoding='utf-8')
        config=tomllib.loads(config_text); require(config['intensity']=='heavy','intensity not written')
        require(MANAGED in config_text,'new user config was not marked as package-managed')
        require(len(list((home/'.codex/agents').glob('*.toml')))==15,'exclude-spark count wrong')
        run(home,'--exclude-spark','--intensity','extreme','--upgrade-managed')
        config=tomllib.loads((home/'.codex/ams-orchestration.toml').read_text(encoding='utf-8')); require(config['intensity']=='heavy','existing config was overwritten')
        require(not list((home/'.agents/plugins/plugins'/PLUGIN).rglob('__pycache__')),'installed plugin contains bytecode cache')

        legacy=base/'legacy'; (legacy/'.codex').mkdir(parents=True); (legacy/'.codex/ams-orchestration.toml').write_text('schema_version = 1\\nintensity = "moderate"\\n',encoding='utf-8')
        run(legacy,'--exclude-spark'); require(tomllib.loads((legacy/'.codex/ams-orchestration.toml').read_text())['intensity']=='moderate','legacy newline config not repaired')

        user_config_home=base/'user-config'; (user_config_home/'.codex').mkdir(parents=True)
        user_config=user_config_home/'.codex/ams-orchestration.toml'
        user_config_text='schema_version = 1\nintensity = "moderate"\n'
        user_config.write_text(user_config_text,encoding='utf-8')
        run(user_config_home,'--exclude-spark','--upgrade-managed')
        require(user_config.read_text(encoding='utf-8')==user_config_text,'install changed a pre-existing user config')
        run(user_config_home,'--uninstall','--yes')
        require(user_config.read_text(encoding='utf-8')==user_config_text,'uninstall removed a pre-existing user config')

        marker_value_home=base/'marker-value-config'; (marker_value_home/'.codex').mkdir(parents=True)
        marker_value_config=marker_value_home/'.codex/ams-orchestration.toml'
        marker_value_text=(
            'schema_version = 1\n'
            'intensity = "moderate"\n'
            'note = "# managed-by: adaptive-master-subagent-orchestration"\n'
        )
        marker_value_config.write_text(marker_value_text,encoding='utf-8')
        run(marker_value_home,'--exclude-spark','--upgrade-managed')
        require(marker_value_config.read_text(encoding='utf-8')==marker_value_text,'marker text inside a TOML value was misclassified during install')
        run(marker_value_home,'--uninstall','--yes')
        require(marker_value_config.read_text(encoding='utf-8')==marker_value_text,'marker text inside a TOML value was misclassified as package ownership during uninstall')

        indented_marker_home=base/'indented-marker-config'; (indented_marker_home/'.codex').mkdir(parents=True)
        indented_marker_config=indented_marker_home/'.codex/ams-orchestration.toml'
        indented_marker_text=(
            '  # managed-by: adaptive-master-subagent-orchestration\n'
            'schema_version = 1\n'
            'intensity = "moderate"\n'
        )
        indented_marker_config.write_text(indented_marker_text,encoding='utf-8')
        run(indented_marker_home,'--exclude-spark','--upgrade-managed')
        require(indented_marker_config.read_text(encoding='utf-8')==indented_marker_text,'noncanonical marker comment was misclassified during install')
        run(indented_marker_home,'--uninstall','--yes')
        require(indented_marker_config.read_text(encoding='utf-8')==indented_marker_text,'noncanonical marker comment was misclassified as package ownership during uninstall')

        malformed=base/'malformed'; mp=malformed/'.agents/plugins/marketplace.json'; mp.parent.mkdir(parents=True); mp.write_text('{bad',encoding='utf-8')
        out=run(malformed,'--exclude-spark',expect=1); require('Cannot parse existing marketplace' in out,'malformed marketplace error unclear'); require(active(malformed)==[],'malformed state partially installed')

        if OPTION=='C':
            out=run(base/'skip','--skip-profiles',expect=1); require('requires profile installation' in out,'Option C skip rejection unclear')
        else:
            skip=base/'skip'; run(skip,'--skip-profiles'); require(not (skip/'.codex/agents').exists(),'skip-profiles installed profiles')

        out=run(base/'badtimeout','--exclude-spark',env={'AMS_PROFILE_TIMEOUT_SECONDS':'0'},expect=1); require('positive integer' in out,'invalid timeout error unclear')
        test_rollback(base); test_rollback_reports_backup_restage_failure(base); test_lock(base)

        unrelated=home/'.agents/plugins/plugins/unrelated'; unrelated.mkdir(); (unrelated/'keep').write_text('keep',encoding='utf-8')
        data=market(home); data['plugins'].append({'name':'unrelated','source':{'source':'local','path':'./plugins/unrelated'}}); (home/'.agents/plugins/marketplace.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
        run(home,'--uninstall','--yes')
        require(active(home)==[],'uninstall left AMS plugin'); require((unrelated/'keep').exists(),'uninstall removed unrelated plugin')
        require(not list((home/'.codex/agents').glob('ams_*.toml')),'uninstall left managed profiles')
        require(not config_path.exists(),'uninstall left a package-managed user config')
        run(home,'--uninstall','--yes')
    print(f'INSTALLATION TESTS PASSED: option {OPTION}')
    return 0
if __name__=='__main__': raise SystemExit(main())
