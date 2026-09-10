from pathlib import Path

p=Path('index.html')
t=p.read_text()

solo_old="""    else if(abilityId==='solo_killshot'){
      const affinity = getClassWeaponAffinity(P);
      let base = rnd(...P.weapon.dmg) + P.dmgBonus + (P.weapon.tech?P.tech:0);
      if(P._ballisticMastery && P.weapon.tag==='ballistic') base += P._ballisticMastery;
      if(P._chromeMetalDividend) base += P.cyberware.length;
      if(P._rockerStagePresence) base += Math.floor((P.cool||0)*0.25);
      if(P._rockerFullAutoChorus && P.weapon.baseId==='smg') base += i;
      if(affinity){
"""
solo_new="""    else if(abilityId==='solo_killshot'){
      const affinity = getClassWeaponAffinity(P);
      let base = rnd(...P.weapon.dmg) + P.dmgBonus + (P.weapon.tech?P.tech:0);
      if(P._ballisticMastery && P.weapon.tag==='ballistic') base += P._ballisticMastery;
      if(affinity){
"""
if solo_old not in t:
    raise SystemExit('precise solo killshot block not found')
t=t.replace(solo_old,solo_new,1)

loop_old="""    for(let i=0;i<hits;i++){
      let base = rnd(...P.weapon.dmg) + P.dmgBonus + (P.weapon.tech?P.tech:0);
      if(P._ballisticMastery && P.weapon.tag==='ballistic') base += P._ballisticMastery;
      if(affinity){
"""
loop_new="""    for(let i=0;i<hits;i++){
      let base = rnd(...P.weapon.dmg) + P.dmgBonus + (P.weapon.tech?P.tech:0);
      if(P._ballisticMastery && P.weapon.tag==='ballistic') base += P._ballisticMastery;
      if(P._chromeMetalDividend) base += P.cyberware.length;
      if(P._rockerStagePresence) base += Math.floor((P.cool||0)*0.25);
      if(P._rockerFullAutoChorus && P.weapon.baseId==='smg') base += i;
      if(affinity){
"""
if loop_old not in t:
    raise SystemExit('precise normal weapon loop not found')
t=t.replace(loop_old,loop_new,1)

p.write_text(t)
print('Precisely placed Chrome/Rocker weapon modifiers')
