import json, subprocess, statistics as st, re
def load(p):
    r=subprocess.run(['git','show',f'main:{p}'],capture_output=True,text=True)
    return json.loads(r.stdout) if r.returncode==0 and r.stdout.strip() else None
print("===== 유방 ERBB2 spatial floor (v2) =====")
d=load('experiments/kkkim/angle_A_spatial_erbb2/spatial_erbb2_floor_v2.json')
pp=d['per_patient']; theta=[p['theta_overlap'] for p in pp]
print(f"n_patients={len(pp)} (원고 8)")
print(f"theta: {[round(t,3) for t in theta]}")
print(f"  median={st.median(theta):.4f} (원고 0.158) | range=[{min(theta):.3f},{max(theta):.3f}] (원고 .023-.424)")
print(f"  CI 0배제: {sum(1 for p in pp if p['theta_ci95'][0]>0)}/{len(pp)} (원고 8/8)")
int_has=[p for p in pp if p.get('n_interior_ref',0)>0]
int_pos=sum(1 for p in int_has if p.get('theta_interior',0)>0)
depth_pos=sum(1 for p in pp if p.get('theta_depth_cond',0)>0)
print(f"  kill-test interior>0: {int_pos}/{len(int_has)} (interior_ref>0 케이스만; 원고 interior 7/8)")
print(f"  kill-test depth_cond>0: {depth_pos}/{len(pp)} (원고 depth 3/3?)")
for p in pp:
    print(f"    {p['patient']}: th={p['theta_overlap']:.3f} CI{p['theta_ci95']} int={p.get('theta_interior')}(nref={p.get('n_interior_ref')}) depth={p.get('theta_depth_cond')}")
print("\n===== 대장 ST =====")
for f in ['experiments/crosscancer/COLORECTAL/ST/msi_immune_colocation.json',
          'experiments/crosscancer/COLORECTAL/ST_IMC/su_imc_msi_colocation.json']:
    j=load(f)
    if not j: print(f"  {f}: 없음"); continue
    print(f"  {f.split('/')[-1]}: keys={list(j.keys())[:12]}")
    s=json.dumps(j,ensure_ascii=False)
    for kw in ['rho','p_val','pval','abundance','claim_level','critic_status','n_patients','n_msi','auc']:
        m=re.search(rf'"[^"]*{kw}[^"]*"\s*:\s*("?[^,{{}}\[]+"?)', s, re.I)
        if m: print("    "+m.group(0)[:90])
