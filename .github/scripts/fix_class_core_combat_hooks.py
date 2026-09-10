from pathlib import Path

p=Path('index.html')
t=p.read_text()

# Remove modifiers accidentally attached to Solo Killshot.
wrong="""      if(P._chromeMetalDividend) base += P.cyberware.length;
      if(P._rockerStagePresence) base += Math.floor((P.cool||0)*0.25);
      if(P._rockerFullAutoChorus && P.weapon.baseId==='smg') base += i;
"""
if wrong not in t:
    raise SystemExit('misplaced modifier block not found')
t=t.replace(wrong,'',1)

# Add those modifiers to the normal weapon-hit loop.
old="""      let base = rnd(...P.weapon.dmg) + P.dmgBonus + (P.weapon.tech?P.tech:0);
      if(P._ballisticMastery && P.weapon.tag==='ballistic') base += P._ballisticMastery;
      if(affinity){
"""
new="""      let base = rnd(...P.weapon.dmg) + P.dmgBonus + (P.weapon.tech?P.tech:0);
      if(P._ballisticMastery && P.weapon.tag==='ballistic') base += P._ballisticMastery;
      if(P._chromeMetalDividend) base += P.cyberware.length;
      if(P._rockerStagePresence) base += Math.floor((P.cool||0)*0.25);
      if(P._rockerFullAutoChorus && P.weapon.baseId==='smg') base += i;
      if(affinity){
"""
# Choose the remaining occurrence, which is now the normal loop.
if old not in t:
    raise SystemExit('normal weapon base block not found')
t=t.replace(old,new,1)

old2="""      if(P._juryRigPrimed) classMult += P._nomadJuryRig||0;
      if(blackhandProc) classMult += 0.50;
"""
new2="""      if(P._juryRigPrimed) classMult += P._nomadJuryRig||0;
      if(P._guardAttackPrimed) classMult += P._soloCoverDiscipline||0;
      if(blackhandProc) classMult += 0.50;
"""
if old2 not in t:
    raise SystemExit('class multiplier block not found')
t=t.replace(old2,new2,1)

old3="""    if(P._juryRigPrimed) P._juryRigPrimed=false;
    if(P._stillWaterPrimed) P._stillWaterPrimed=false;
"""
new3="""    if(P._juryRigPrimed) P._juryRigPrimed=false;
    if(P._guardAttackPrimed) P._guardAttackPrimed=false;
    if(P._stillWaterPrimed) P._stillWaterPrimed=false;
"""
if old3 not in t:
    raise SystemExit('attack prime cleanup block not found')
t=t.replace(old3,new3,1)

# Add rarity badges to in-combat weapon switching and salvage prompts.
old4="""    sub:`${w.dmg[0]}-${w.dmg[1]} dmg, crit ${Math.round(w.crit*100)}%${w.mutation?' ⟨'+w.mutation.name+'⟩':''}`,
"""
new4="""    sub:`${rarityBadge(w.rarity||weaponRarityFromTier(w.tier||0))} ${w.dmg[0]}-${w.dmg[1]} dmg, crit ${Math.round(w.crit*100)}%${w.mutation?' ⟨'+w.mutation.name+'⟩':''}`,
"""
if old4 not in t:
    raise SystemExit('switch rarity block not found')
t=t.replace(old4,new4,1)

old5="""      print(`<span class=\"tag loot\">SALVAGE</span> Looted <b>${w.name}</b>.`);
"""
new5="""      print(`<span class=\"tag loot\">SALVAGE</span> ${rarityBadge(w.rarity||weaponRarityFromTier(w.tier||0))} Looted <b>${w.name}</b>.`);
"""
if old5 not in t:
    raise SystemExit('weapon salvage rarity block not found')
t=t.replace(old5,new5,1)

old6="""          { label:`Install ${cw.name}`, sub:cw.desc+` (-${cw.hum} Humanity)`, cls:'gold', fn:()=>{ installCyberware(P,cw,false); divider(); advance(); } },
"""
new6="""          { label:`Install ${cw.name}`, sub:`${rarityBadge(cyberwareRarity(cw))} ${cw.desc} (-${cw.hum} Humanity)`, cls:'gold', fn:()=>{ installCyberware(P,cw,false); divider(); advance(); } },
"""
if old6 not in t:
    raise SystemExit('chrome salvage rarity block not found')
t=t.replace(old6,new6,1)

p.write_text(t)
print('Fixed class core combat hooks and remaining rarity labels')
