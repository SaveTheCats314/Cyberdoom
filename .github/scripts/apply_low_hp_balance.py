from pathlib import Path
import re

path = Path('index.html')
text = path.read_text()


def replace_once(old, new, label):
    global text
    if old not in text:
        raise SystemExit(f'Patch target not found: {label}')
    text = text.replace(old, new, 1)

# --- class baselines / ability descriptions ---
replace_once(
"""  { id:'netrunner', name:'Netrunner', tagline:'Lives in the net more than the meat.',
    hp:22, dmg:[2,4], def:1, tech:6, cool:3, humanity:85,
    weapon:'monowire', ability:{name:'Quickhack', desc:'Tech damage that ignores all armor + 30% chance to stun.', cd:2} },""",
"""  { id:'netrunner', name:'Netrunner', tagline:'Lives in the net more than the meat.',
    hp:24, dmg:[2,4], def:1, tech:6, cool:4, humanity:85,
    weapon:'monowire', ability:{name:'Quickhack', desc:'Armor-piercing tech damage that scales with target HP, breaches 1 armor, and can stun.', cd:2} },""",
'Netrunner class baseline'
)

replace_once(
"""  { id:'rocker', name:'Rockerboy', tagline:'Every gig might be the last encore.',
    hp:26, dmg:[3,6], def:2, tech:2, cool:7, humanity:100,""",
"""  { id:'rocker', name:'Rockerboy', tagline:'Every gig might be the last encore.',
    hp:28, dmg:[3,6], def:2, tech:2, cool:7, humanity:100,""",
'Rockerboy HP'
)

replace_once(
"""  { id:'fixer', name:'Fixer', tagline:'Knows a guy who knows a guy.',
    hp:24, dmg:[3,5], def:2, tech:3, cool:6, humanity:100,
    weapon:'silenced_pistol', ability:{name:'Connections', desc:'Free reroll of any shop, once per district.', cd:0} },""",
"""  { id:'fixer', name:'Fixer', tagline:'Knows a guy who knows a guy.',
    hp:26, dmg:[3,5], def:2, tech:3, cool:6, humanity:100,
    weapon:'silenced_pistol', ability:{name:'Connections', desc:'Call in armor-piercing backup and mark the target for +25% eddies. Fixers also get +1 shop reroll.', cd:3} },""",
'Fixer class baseline'
)

replace_once(
"""  fixer:     { desc:'+1 extra shop reroll', apply:p=>p._extraReroll=1 },""",
"""  fixer:     { desc:'+1 extra shop reroll', apply:p=>p._extraReroll=(p._extraReroll||0)+1 },""",
'Fixer mastery stacking'
)

# Base Fixer shop identity: one extra reroll before mastery.
replace_once(
"""    usedSecondWind:false,
  };
  // meta-shop permanent perks""",
"""    usedSecondWind:false,
  };
  if(p.cls==='fixer') p._extraReroll = (p._extraReroll||0) + 1;
  // meta-shop permanent perks""",
'Fixer base reroll'
)

# --- Evade now scales with Cool ---
replace_once(
"""function combatMenu(){
  const P = S.run.player;""",
"""function getEvadeChance(P){
  return Math.min(
    0.95,
    0.65 + ((P.cool||0) * 0.015) + (hasRelic(P,'ghost_runner') ? 0.15 : 0)
  );
}

function combatMenu(){
  const P = S.run.player;""",
'Evade helper'
)

replace_once(
"""    { label:'Evade', sub:`${hasRelic(P,'ghost_runner') ? '80' : '65'}% chance to avoid the next attack`, fn:()=>evadeAction() },""",
"""    { label:'Evade', sub:`${Math.round(getEvadeChance(P)*100)}% chance to avoid the next attack`, fn:()=>evadeAction() },""",
'Evade menu chance'
)

replace_once(
"""  c.evadeChance = 0.65 + (hasRelic(P,'ghost_runner') ? 0.15 : 0);""",
"""  c.evadeChance = getEvadeChance(P);""",
'Evade action chance'
)

# --- Watson early-game smoothing without weakening later districts ---
scaled_pattern = re.compile(r"function scaledEnemy\(base, act, elite, hardMode\)\{.*?\n\}", re.S)
scaled_match = scaled_pattern.search(text)
if not scaled_match:
    raise SystemExit('Patch target not found: scaledEnemy')
scaled_new = """function scaledEnemy(base, act, elite, hardMode){
  let hpScale = 1 + act*0.35;
  let dmgScale = 1 + act*0.35;

  // Watson is the learning district: reduce burst damage and soften its forced elite.
  if(act===0){
    dmgScale *= 0.85;
    if(elite || base.elite) hpScale *= 0.90;
  }

  if(hardMode){
    hpScale *= 1.2;
    dmgScale *= 1.2;
  }

  return {
    name: base.name,
    maxHp: Math.round(base.hp*hpScale),
    hp: Math.round(base.hp*hpScale),
    dmg: [Math.round(base.dmg[0]*dmgScale), Math.round(base.dmg[1]*dmgScale)],
    def: base.def + Math.floor(act*0.7),
    tech: !!base.tech,
    elite: !!elite || !!base.elite,
    berserk: !!base.berserk
  };
}"""
text = text[:scaled_match.start()] + scaled_new + text[scaled_match.end():]

# --- Netrunner Quickhack endgame scaling ---
replace_once(
"""    if(P.cls==='netrunner'){
      let d = rnd(6,11) + P.tech + P.dmgBonus;
      totalDmg = d;
      const stunned = Math.random()<0.3;
      print(`<span class=\"tag hack\">QUICKHACK</span> You burn straight through ${c.enemy.name}'s ICE for <b>${totalDmg}</b> tech damage (armor ignored).${stunned?' <span class=\"warn\">Target stunned — skips next attack.</span>':''}`);
      c.enemy.hp -= totalDmg; c.enemyStunned = stunned;""",
"""    if(P.cls==='netrunner'){
      const targetScale = Math.max(1, Math.round(c.enemy.maxHp*0.08));
      let d = rnd(6,11) + P.tech + P.dmgBonus + targetScale;
      totalDmg = d;
      const stunChance = Math.min(0.50, 0.25 + P.tech*0.02);
      const stunned = Math.random() < stunChance;
      c.enemy.def = Math.max(0, c.enemy.def-1);
      print(`<span class=\"tag hack\">QUICKHACK</span> You breach ${c.enemy.name}'s ICE for <b>${totalDmg}</b> tech damage (armor ignored). <span class=\"accent\">Armor -1.</span>${stunned?' <span class=\"warn\">Target stunned — skips next attack.</span>':''}`);
      c.enemy.hp -= totalDmg;
      c.enemyStunned = stunned;""",
'Netrunner Quickhack'
)

# --- Fixer now has an actual combat ability ---
replace_once(
"""    } else if(P.cls==='fixer'){
      print(`<span class=\"tag hack\">CONNECTIONS</span> Not usable mid-combat — save it for the next shop.`);
      ab.cdLeft=0; ab.ready=true;
    } else {""",
"""    } else if(P.cls==='fixer'){
      let d = rnd(5,8) + P.tech + P.cool + P.dmgBonus;
      d = Math.max(1,d);
      c.enemy.hp -= d;
      totalDmg = d;
      c.contractBonus = Math.max(c.contractBonus||0, 0.25);
      print(`<span class=\"tag hack\">CONNECTIONS</span> A contact paints the target from off-grid. <b>${d}</b> armor-piercing damage. <span class=\"good\">Target marked: +25% eddies on kill.</span>`);
    } else {""",
'Fixer Connections combat ability'
)

# --- Multi-hit weapons split armor across the attack instead of paying full armor every hit ---
replace_once(
"""    for(let i=0;i<hits;i++){
      let base = rnd(...P.weapon.dmg) + P.dmgBonus + (P.weapon.tech?P.tech:0);""",
"""    const armorPerHit = hits>1 ? Math.ceil(c.enemy.def / hits) : c.enemy.def;
    for(let i=0;i<hits;i++){
      let base = rnd(...P.weapon.dmg) + P.dmgBonus + (P.weapon.tech?P.tech:0);""",
'Multi-hit armor setup'
)

replace_once(
"""      d = Math.max(1, d - c.enemy.def);""",
"""      d = Math.max(1, d - armorPerHit);""",
'Multi-hit armor application'
)

# --- Fixer contract payout ---
replace_once(
"""  eddies = Math.round(eddies * (S.run.actEddiesMult||1) * (hasRelic(P,'loyalty_chip')?1.2:1));""",
"""  eddies = Math.round(
    eddies *
    (S.run.actEddiesMult||1) *
    (hasRelic(P,'loyalty_chip')?1.2:1) *
    (1 + (c.contractBonus||0))
  );""",
'Fixer contract payout'
)

path.write_text(text)
