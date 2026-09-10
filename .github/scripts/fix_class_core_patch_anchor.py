from pathlib import Path

p = Path('.github/scripts/apply_class_cores_rarity.py')
t = p.read_text()
old1 = "            starting:true, hardMode: !!hardMode };"
new1 = "            eventHistory:[], starting:true, hardMode: !!hardMode };"
old2 = "            starting:true, classRelicsGranted:0, hardMode: !!hardMode };"
new2 = "            eventHistory:[], starting:true, classRelicsGranted:0, hardMode: !!hardMode };"
if old1 not in t:
    raise SystemExit('old startRun anchor not found in patch script')
if old2 not in t:
    raise SystemExit('new startRun anchor not found in patch script')
t = t.replace(old1, new1, 1)
t = t.replace(old2, new2, 1)
p.write_text(t)
print('Fixed class relic startRun anchor')
