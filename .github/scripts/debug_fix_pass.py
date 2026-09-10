from pathlib import Path

p = Path('index.html')
t = p.read_text()

def rep(old,new,label):
    global t
    if old not in t:
        raise SystemExit(f'missing patch target: {label}')
    t=t.replace(old,new,1)

# CSS: remove stray brace after header block.
rep("""  z-index:5;
}
  }
  #hdr .title""", """  z-index:5;
}
  #hdr .title""", 'stray CSS brace')

# Inventory overflow: never leave the equipped weapon as a ghost reference outside inventory.
rep(
"function addToInventory(P, w){ P.inventory.push(w); const cap=P.inventoryCap||6; if(P.inventory.length>cap) P.inventory.shift(); }",
"""function addToInventory(P, w){
  P.inventory.push(w);
  const cap=P.inventoryCap||6;
  if(P.inventory.length>cap){
    const dropIndex=P.inventory.findIndex(item=>item!==P.weapon);
    P.inventory.splice(dropIndex>=0?dropIndex:0,1);
  }
}""",
'inventory overflow'
)

# Full Conversion preview helper.
rep(
"""function installCyberware(P, cw, risky){
  P.cyberware.push(cw);""",
"""function displayedCyberwareHumanityCost(P,cw){
  return P._fullConversion ? Math.max(1,Math.ceil(cw.hum*0.5)) : cw.hum;
}

function installCyberware(P, cw, risky){
  P.cyberware.push(cw);""",
'full conversion preview helper'
)

# Shop should not sell duplicate installed chrome when all current chrome is owned.
rep(
"""  const cwChoices = cyberwarePool().filter(c=>!P.cyberware.includes(c));
  stock.push({ kind:'cyber', item: pick(cwChoices.length?cwChoices:cyberwarePool()), price: Math.round(rnd(50,90)*disc) });
  stock.push({ kind:'stim', item:{name:'Combat Stim (+heal mid-fight)'}, price: Math.round(25*disc) });""",
"""  const cwChoices = cyberwarePool().filter(c=>!P.cyberware.includes(c));
  if(cwChoices.length){
    stock.push({ kind:'cyber', item: pick(cwChoices), price: Math.round(rnd(50,90)*disc) });
  }
  stock.push({ kind:'stim', item:{name:'Combat Stim (+heal mid-fight)'}, price: Math.round(25*disc) });""",
'duplicate chrome shop offer'
)

rep(
"""      else if(s.kind==='cyber'){ label=`Install: ${s.item.name}`; sub=`${rarityBadge(cyberwareRarity(s.item))} ${s.item.desc} (${s.item.slot}) — ${s.price}e, -${s.item.hum} Humanity`; }""",
"""      else if(s.kind==='cyber'){
        const shownHum=displayedCyberwareHumanityCost(P,s.item);
        label=`Install: ${s.item.name}`;
        sub=`${rarityBadge(cyberwareRarity(s.item))} ${s.item.desc} (${s.item.slot}) — ${s.price}e, -${shownHum} Humanity${P._fullConversion?' [FULL CONVERSION]':''}`;
      }""",
'shop full conversion preview'
)

rep(
"""          { label:`Install ${cw.name}`, sub:`${rarityBadge(cyberwareRarity(cw))} ${cw.desc} (-${cw.hum} Humanity)`, cls:'gold', fn:()=>{ installCyberware(P,cw,false); divider(); advance(); } },""",
"""          { label:`Install ${cw.name}`, sub:`${rarityBadge(cyberwareRarity(cw))} ${cw.desc} (-${displayedCyberwareHumanityCost(P,cw)} Humanity${P._fullConversion?' · FULL CONVERSION':''})`, cls:'gold', fn:()=>{ installCyberware(P,cw,false); divider(); advance(); } },""",
'salvage full conversion preview'
)

# Samurai cores should trigger on the first Katana attack, not only if Katana was the first weapon used.
rep(
"""  const firstWeaponAttack = !useAbility && !c._classFirstWeaponUsed;
  if(!useAbility){
    c._classFirstWeaponUsed = true;
    P._weaponAttackCount = (P._weaponAttackCount||0)+1;
  }""",
"""  const firstWeaponAttack = !useAbility && !c._classFirstWeaponUsed;
  const firstKatanaAttack = !useAbility && P.weapon.baseId==='katana' && !c._firstKatanaUsed;
  if(!useAbility){
    c._classFirstWeaponUsed = true;
    if(P.weapon.baseId==='katana') c._firstKatanaUsed = true;
    P._weaponAttackCount = (P._weaponAttackCount||0)+1;
  }""",
'first katana tracker'
)
rep("if(firstWeaponAttack && P._samuraiNoSecondStrike && P.weapon.baseId==='katana')", "if(firstKatanaAttack && P._samuraiNoSecondStrike)", 'samurai legendary first katana')
rep("if((firstWeaponAttack && P._samuraiPerfectDraw && P.weapon.baseId==='katana') || P._stillWaterPrimed || blackhandProc)", "if((firstKatanaAttack && P._samuraiPerfectDraw) || P._stillWaterPrimed || blackhandProc)", 'samurai perfect draw first katana')

# Rally Cry: avoid permanent stat stacking and make advertised duration match player turns.
rep(
"""    else if(abilityId==='rocker_rally'){
      P.dmgBonus += 2;
      P.def += 1;
      P.cool += 2;
      c.rallyTurns = 3 + (P._rockerEncore||0) + (P._rockerFeedbackLoop||0);
      print(`<span class=\"tag hack\">RALLY CRY</span> Adrenaline and distortion pedals. <span class=\"good\">+2 dmg, +1 def, +2 cool for ${c.rallyTurns} turns.</span>`);
    }""",
"""    else if(abilityId==='rocker_rally'){
      const duration = 3 + (P._rockerEncore||0) + (P._rockerFeedbackLoop||0);
      const alreadyActive = !!c.rallyTurns;
      if(!alreadyActive){
        P.dmgBonus += 2;
        P.def += 1;
        P.cool += 2;
      }
      c.rallyTurns = duration;
      c.rallyFresh = true;
      print(`<span class=\"tag hack\">RALLY CRY</span> Adrenaline and distortion pedals. <span class=\"good\">${alreadyActive?'Buff refreshed':' +2 dmg, +1 def, +2 cool'} for ${duration} player turns.</span>`);
    }""",
'rally stacking and duration setup'
)
rep(
"""  if(c.rallyTurns){ c.rallyTurns--; if(c.rallyTurns<=0){ P.dmgBonus-=2; P.def-=1; P.cool-=2; c.rallyTurns=null; print('Rally Cry fades.', 'flavor'); } }""",
"""  if(c.rallyTurns){
    if(c.rallyFresh){
      c.rallyFresh=false;
    } else {
      c.rallyTurns--;
      if(c.rallyTurns<=0){
        P.dmgBonus-=2; P.def-=1; P.cool-=2;
        c.rallyTurns=null;
        print('Rally Cry fades.', 'flavor');
      }
    }
  }""",
'rally duration countdown'
)

# Boss phase helper: transition as soon as Smasher crosses 50%, not only during win resolution.
phase_helper = """
function checkBossPhase(){
  const c=S.run?.combat;
  if(!c?.boss || !c.enemy || c.enemy.phase!==1 || c.enemy.hp<=0 || c.enemy.hp>c.enemy.maxHp*0.5) return false;
  c.enemy.phase=2;
  c.enemy.dmg=[c.enemy.dmg[0]+3,c.enemy.dmg[1]+4];
  print(`<span class=\"tag boss\">PHASE 2</span> Smasher's chassis vents smoke. \"Now we're talking.\" <span class=\"bad\">His attacks hit harder.</span>`);
  refreshStatus();
  return true;
}

"""
rep("function playerAttack(useAbility){", phase_helper + "function playerAttack(useAbility){", 'boss phase helper')

rep(
"""  refreshStatus();
  if(c.enemy.hp <= 0) return winCombat();
  enemyTurn();
}""",
"""  refreshStatus();
  if(c.enemy.hp <= 0) return winCombat();
  checkBossPhase();
  enemyTurn();
}""",
'phase check after player action'
)

rep(
"""    refreshStatus();
    if(c.enemy.hp<=0) return winCombat();
  }

  if(c.enemyStunned){""",
"""    refreshStatus();
    if(c.enemy.hp<=0) return winCombat();
    checkBossPhase();
  }

  if(c.enemyStunned){""",
'phase check after bleed'
)

rep(
"""  if(checkDeath()) return;
  if(c.enemy.hp<=0) return winCombat();
  combatMenu();""",
"""  if(checkDeath()) return;
  if(c.enemy.hp<=0) return winCombat();
  checkBossPhase();
  combatMenu();""",
'phase check after enemy/riposte'
)

# Hard mode must also increase Smasher's damage.
rep(
"""    name:'Adam Smasher', maxHp: Math.round(150*heatBonus*hardBonus), hp: Math.round(150*heatBonus*hardBonus),
    dmg:[10,16], def:6, phase:1, elite:true, boss:true""",
"""    name:'Adam Smasher', maxHp: Math.round(150*heatBonus*hardBonus), hp: Math.round(150*heatBonus*hardBonus),
    dmg:[Math.round(10*hardBonus),Math.round(16*hardBonus)], def:6, phase:1, elite:true, boss:true""",
'smasher hard damage'
)

# Handle final boss directly inside winCombat and remove reassignment wrapper.
rep(
"""function winCombat(){
  const P = S.run.player; const c = S.run.combat;
  S.run.kills++;""",
"""function winCombat(){
  const P = S.run.player; const c = S.run.combat;
  if(c.boss){
    S.run.kills++;
    S.run.eliteKills++;
    print(`<span class=\"tag boss\">FLATLINE — CONFIRMED</span> <span class=\"good\">Adam Smasher hits the floor. For one silent second, Night City feels almost survivable.</span>`);
    refreshStatus();
    return endRun(true);
  }
  S.run.kills++;""",
'direct final boss win handling'
)

wrapper="""const _origWinCombat = winCombat;
winCombat = function(){
  const c = S.run.combat;
  if(c.boss){
    if(c.enemy.phase===1 && c.enemy.hp <= c.enemy.maxHp*0.5 && c.enemy.hp>0){
      c.enemy.phase=2; c.enemy.dmg=[c.enemy.dmg[0]+3, c.enemy.dmg[1]+4];
      print(`<span class=\"tag boss\">PHASE 2</span> Smasher's chassis vents smoke. \"Now we're talking.\" <span class=\"bad\">His attacks hit harder.</span>`);
      refreshStatus();
      return enemyTurn();
    }
    if(c.enemy.hp<=0){
      print(`<span class=\"tag boss\">FLATLINE — CONFIRMED</span> <span class=\"good\">Adam Smasher hits the floor. For one silent second, Night City feels almost survivable.</span>`);
      return endRun(true);
    }
    refreshStatus();
    return enemyTurn();
  }
  return _origWinCombat();
};

"""
rep(wrapper,"",'remove winCombat wrapper')

# Clarify inventory behavior in the guide.
rep(
"If a seventh is added, the oldest inventory weapon is automatically pushed out, so drop unwanted weapons before taking new gear.",
"If you exceed your capacity, the oldest unequipped weapon is automatically pushed out, so your active weapon never disappears from the inventory.",
'inventory guide'
)

p.write_text(t)
print('Applied Cyberdoom gameplay debug fix pass')
