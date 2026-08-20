#!/usr/bin/env python3
"""shuffle-null 20-seed 강건성 재확인 (BIOP02-123 조율 #11974).
봉인 5-seed 스크립트/결과 무손상 — sh_robustness_5seed의 SEEDS만 오버라이드, 별도 출력.
헤드라인: 두경부 HPV × 3 FM(virchow2 경계 0.9199/0.9234) + egfr_amp(허위PASS 위험) 대칭 재확인.
"""
import sys, os, argparse
CC = "/home/kkkim/project/BioProject02/experiments/crosscancer"
sys.path.insert(0, CC)
import sh_robustness_5seed as sh

OUT = os.path.dirname(os.path.abspath(__file__))
SEEDS20 = [42] + list(range(1, 20))   # 20 seeds, 42 first (real=seed42 관례 유지)

ap = argparse.ArgumentParser()
ap.add_argument("--seeds", type=int, default=20)
ap.add_argument("--fms", default="uni,uni2h,virchow2")
ap.add_argument("--endpoints", default="hpv_pos,egfr_amp")
ap.add_argument("--cancer", default="HEADNECK_HNSC")
ap.add_argument("--device", default="cuda:0")
a = ap.parse_args()
sh.SEEDS = SEEDS20[:a.seeds]
print(f"SEEDS({len(sh.SEEDS)})={sh.SEEDS}", flush=True)

for fm in a.fms.split(","):
    outf = f"{OUT}/{a.cancer.lower()}_{a.seeds}seed_{fm}.json"
    sys.argv = ["sh", "--cancer", a.cancer, "--endpoints", a.endpoints,
                "--fm", fm, "--device", a.device, "--out", outf]
    print(f"\n===== FM {fm} → {outf} =====", flush=True)
    sh.main()
