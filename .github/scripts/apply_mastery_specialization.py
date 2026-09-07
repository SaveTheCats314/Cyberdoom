from pathlib import Path
import re

path = Path('index.html')
text = path.read_text()


def replace_once(old, new, label):
    global text
    if old not in text:
        raise SystemExit(f'Patch target not found: {label}')
    text = text.replace(old, new, 1)


def sub_once(pattern, repl, label):
    global text
    new_text, count = re.subn(pattern, repl, text, count=1, flags=re.S)
    if count != 1:
        raise SystemExit(f'Patch target not found: {label}')
    text = new_text


# ---------- mastery cosmetic styling ----------
replace_once(
"""  .cardgrid{display:grid; gap:10px;}""",
"""  .hudNameplate{
    display:inline-block;
    margin-right:4px;
    padding:1px 4px;
    border:1px solid rgba(178,107,255,0.45);
    border-radius:3px;
    color:var(--purple);
    font-size:8px;
    letter-spacing:.7px;
    vertical-align:1px;
  }
  .hudNameplate.legendary{
    color:var(--magenta);
    border-color:rgba(255,46,136,0.65);
    box-shadow:0 0 8px rgba(255,46,136,0.12);
  }
  .masteryReward{
    padding:5px 0;
    color:var(--dim);
    font-size:10px;
  }
  .masteryReward.unlocked{color:var(--text);}
  .masteryPlate{
    display:inline-block;
    margin-left:5px;
    padding:1px 5px;
    border:1px solid rgba(178,107,255,0.45);
    border-radius:3px;
    color:var(--purple);
    font-size:9px;
    letter-spacing:.8px;
  }
  .masteryPlate.legendary{
    color:var(--magenta);
    border-color:rgba(255,46,136,0.65);
  }

  .cardgrid{display:grid; gap:10px;}""",
'mastery cosmetic CSS'
)


# ---------- add stable IDs to the seven default abilities ----------
ability_replacements = {
"ability:{name:'Overwatch', desc:'+60% damage this turn, ignore 2 armor.', cd:3}": "ability:{id:'solo_overwatch', name:'Overwatch', desc:'+60% damage this turn, ignore 2 armor.', cd:3}",
"ability:{name:'Quickhack', desc:'Armor-piercing tech damage that scales with target HP, breaches 1 armor, and can stun.', cd:2}": "ability:{id:'netrunner_quickhack', name:'Quickhack', desc:'Armor-piercing tech damage that scales with target HP, breaches 1 armor, and can stun.', cd:2}",
"ability:{name:'Berserk', desc:'Damage scales up as your HP drops. Costs Humanity to use.', cd:2}": "ability:{id:'chrome_berserk', name:'Berserk', desc:'Damage scales up as your HP drops. Costs Humanity to use.', cd:2}",
"ability:{name:'Blade Dance', desc:'Guaranteed crit; crits chain into a free bonus strike.', cd:3}": "ability:{id:'samurai_blade_dance', name:'Blade Dance', desc:'Guaranteed crit; crits chain into a free bonus strike.', cd:3}",
"ability:{name:'Rally Cry', desc:'Buff all stats for 3 turns.', cd:4}": "ability:{id:'rocker_rally', name:'Rally Cry', desc:'Buff all stats for 3 turns.', cd:4}",
"ability:{name:'Scavenger Instinct', desc:'Guarantees bonus loot after this fight.', cd:0}": "ability:{id:'nomad_scavenger', name:'Scavenger Instinct', desc:'Guarantees bonus loot after this fight.', cd:0}",
"ability:{name:'Connections', desc:'Call in armor-piercing backup and mark the target for +25% eddies. Fixers also get +1 shop reroll.', cd:3}": "ability:{id:'fixer_connections', name:'Connections', desc:'Call in armor-piercing backup and mark the target for +25% eddies. Fixers also get +1 shop reroll.', cd:3}",
}
for old, new in ability_replacements.items():
    replace_once(old, new, 'default ability ID')


# ---------- replace the old 3-tier mastery with a 6-rank specialized system ----------
mastery_block = r'''// ================= CLASS MASTERY =================
const MASTERY_RANKS = [
  { level:1, name:'Initiate',   kills:10,  wins:0 },
  { level:2, name:'Specialist', kills:25,  wins:0 },
  { level:3, name:'Veteran',    kills:50,  wins:1 },
  { level:4, name:'Elite',      kills:80,  wins:2 },
  { level:5, name:'Ace',        kills:120, wins:3 },
  { level:6, name:'Legend',     kills:170, wins:5 },
];

const ALT_ABILITIES = {
  solo: {
    id:'solo_killshot', name:'Killshot', cd:4,
    desc:'A guaranteed critical weapon strike that ignores all armor.'
  },
  netrunner: {
    id:'netrunner_daemon', name:'Daemon Cascade', cd:3,
    desc:'Lower direct damage, but uploads Tech-scaled bleed and has a 70% stun chance.'
  },
  chrome: {
    id:'chrome_groundpound', name:'Ground Pound', cd:3,
    desc:'Heavy chrome-powered damage with a 40% stun chance. Costs more Humanity than Berserk.'
  },
  samurai: {
    id:'samurai_iaijutsu', name:'Iaijutsu', cd:4,
    desc:'One massive 3x draw strike that ignores half of enemy armor.'
  },
  rocker: {
    id:'rocker_feedback', name:'Feedback Burst', cd:3,
    desc:'Cool-scaled sonic damage that permanently lowers enemy damage for the fight.'
  },
  nomad: {
    id:'nomad_roadwarrior', name:'Road Warrior', cd:3,
    desc:'Heavy weapon damage followed by a 35% Guard against the counterattack.'
  },
  fixer: {
    id:'fixer_professional', name:'Professional Courtesy', cd:3,
    desc:'Armor-piercing damage, strips 2 armor, and marks the target for bonus eddies.'
  },
};

const MASTERY_PATHS = {
  solo: {
    plates:{2:'GUNHAND',6:'BLACKHAND'},
    rewards:{
      1:{desc:'+1 Defense.', apply:p=>p.def+=1},
      2:{desc:'Cosmetic nameplate unlocked: GUNHAND.'},
      3:{desc:'Sidearm Doctrine II: +10% Pistol damage and +5% crit.'},
      4:{desc:'Alternate ability unlocked: Killshot.'},
      5:{desc:'Combat Drills: chosen Solo ability cooldown -1.', apply:p=>p.ability.cd=Math.max(1,p.ability.cd-1)},
      6:{desc:'BLACKHAND nameplate + +1 damage with all ballistic weapons.', apply:p=>p._ballisticMastery=1},
    }
  },
  netrunner: {
    plates:{2:'GHOST',6:'BLACKWALL'},
    rewards:{
      1:{desc:'+1 Tech.', apply:p=>p.tech+=1},
      2:{desc:'Cosmetic nameplate unlocked: GHOST.'},
      3:{desc:'Neural Conduit II: Monowire gains +1 Tech damage and +5% crit.'},
      4:{desc:'Alternate ability unlocked: Daemon Cascade.'},
      5:{desc:'Optimized Deck: chosen Netrunner ability cooldown -1.', apply:p=>p.ability.cd=Math.max(1,p.ability.cd-1)},
      6:{desc:'BLACKWALL nameplate + +2 Tech.', apply:p=>p.tech+=2},
    }
  },
  chrome: {
    plates:{2:'IRON',6:'CYBERDEMON'},
    rewards:{
      1:{desc:'+5 max Humanity.', apply:p=>{p.maxHumanity+=5; p.humanity+=5;}},
      2:{desc:'Cosmetic nameplate unlocked: IRON.'},
      3:{desc:'Full-Force Interface II: +10% Gorilla Arms damage.'},
      4:{desc:'Alternate ability unlocked: Ground Pound.'},
      5:{desc:'Chrome Efficiency: special abilities cost 1 less Humanity.', apply:p=>p._chromeAbilityDiscount=1},
      6:{desc:'CYBERDEMON nameplate + +2 Defense.', apply:p=>p.def+=2},
    }
  },
  samurai: {
    plates:{2:'RONIN',6:'SHOGUN'},
    rewards:{
      1:{desc:'+5% global crit chance.', apply:p=>p.critBonus+=0.05},
      2:{desc:'Cosmetic nameplate unlocked: RONIN.'},
      3:{desc:'Blade Discipline II: +10% Katana crit chance.'},
      4:{desc:'Alternate ability unlocked: Iaijutsu.'},
      5:{desc:'Perfect Form: Blade Dance follow-up and Iaijutsu become stronger.', apply:p=>p._samuraiMastery=true},
      6:{desc:'SHOGUN nameplate + another +10% global crit chance.', apply:p=>p.critBonus+=0.10},
    }
  },
  rocker: {
    plates:{2:'HEADLINER',6:'NEON ICON'},
    rewards:{
      1:{desc:'+1 Cool.', apply:p=>p.cool+=1},
      2:{desc:'Cosmetic nameplate unlocked: HEADLINER.'},
      3:{desc:'Full-Auto Rhythm II: SMG gains another +1 damage per shot.'},
      4:{desc:'Alternate ability unlocked: Feedback Burst.'},
      5:{desc:'Encore: Rally lasts +1 turn; Feedback Burst hits and suppresses harder.', apply:p=>p._rockerEncore=1},
      6:{desc:'NEON ICON nameplate + +1 global damage.', apply:p=>p.dmgBonus+=1},
    }
  },
  nomad: {
    plates:{2:'ROAD DOG',6:'WRAITH'},
    rewards:{
      1:{desc:'Shop prices -10%.', apply:p=>p.shopDiscount=(p.shopDiscount||0)+0.10},
      2:{desc:'Cosmetic nameplate unlocked: ROAD DOG.'},
      3:{desc:'Roadside Breacher II: +10% Shotgun damage.'},
      4:{desc:'Alternate ability unlocked: Road Warrior.'},
      5:{desc:'Salvage Expert: either Nomad special marks the kill for +20% eddies.', apply:p=>p._nomadSalvage=0.20},
      6:{desc:'WRAITH nameplate + +1 Defense and another 5% shop discount.', apply:p=>{p.def+=1; p.shopDiscount=(p.shopDiscount||0)+0.05;}},
    }
  },
  fixer: {
    plates:{2:'OPERATOR',6:'KINGMAKER'},
    rewards:{
      1:{desc:'Shop prices -5%.', apply:p=>p.shopDiscount=(p.shopDiscount||0)+0.05},
      2:{desc:'Cosmetic nameplate unlocked: OPERATOR.'},
      3:{desc:'Quiet Professional II: +1 Silenced Pistol damage and +5% crit.'},
      4:{desc:'Alternate ability unlocked: Professional Courtesy.'},
      5:{desc:'Premium Contracts: Fixer special marks are worth another +10% eddies.', apply:p=>p._fixerContractBonus=0.10},
      6:{desc:'KINGMAKER nameplate + +1 Cool and another shop reroll.', apply:p=>{p.cool+=1; p._extraReroll=(p._extraReroll||0)+1;}},
    }
  },
};

const MASTERY_AFFINITY_BONUS = {
  solo:      {damageMult:0.10, critBonus:0.05},
  netrunner: {techBonus:1, critBonus:0.05},
  chrome:    {damageMult:0.10},
  samurai:   {critBonus:0.10},
  rocker:    {flatDamage:1},
  nomad:     {damageMult:0.10},
  fixer:     {flatDamage:1, critBonus:0.05},
};

function getMasteryLevel(m){
  m = m || {kills:0,wins:0};
  let level = 0;
  MASTERY_RANKS.forEach(rank=>{
    if((m.kills||0) >= rank.kills && (m.wins||0) >= rank.wins) level = rank.level;
  });
  return level;
}

function getMasteryRankName(level){
  if(level<=0) return 'Unranked';
  return (MASTERY_RANKS.find(r=>r.level===level)||{}).name || 'Legend';
}

function getMasteryNameplate(clsId, m){
  const level = getMasteryLevel(m);
  const path = MASTERY_PATHS[clsId];
  if(!path) return '';
  if(level>=6) return path.plates[6];
  if(level>=2) return path.plates[2];
  return '';
}

function applyMasteryBonuses(p, clsId, m){
  const level = getMasteryLevel(m);
  const path = MASTERY_PATHS[clsId];
  p.masteryLevel = level;
  p.nameplate = getMasteryNameplate(clsId,m);
  if(!path) return;
  for(let i=1;i<=level;i++){
    const reward = path.rewards[i];
    if(reward && reward.apply) reward.apply(p);
  }
}
'''
sub_once(
    r"// class-specific mastery perk applied at tier 2\nconst MASTERY_PASSIVE = \{.*?const MASTERY_WINS_T3 = 5;",
    mastery_block,
    'old mastery system'
)


# ---------- mastery-enhanced weapon affinities ----------
sub_once(
    r"function getClassWeaponAffinity\(P\)\{.*?\n\}",
    r'''function getClassWeaponAffinity(P){
  const baseAffinity = getAffinityDefinition(P);
  if(!baseAffinity || !P.weapon || P.weapon.baseId !== baseAffinity.baseId) return null;

  const affinity = {...baseAffinity};
  if((P.masteryLevel||0) >= 3){
    const bonus = MASTERY_AFFINITY_BONUS[P.cls] || {};
    if(bonus.damageMult) affinity.damageMult = (affinity.damageMult||1) + bonus.damageMult;
    if(bonus.critBonus) affinity.critBonus = (affinity.critBonus||0) + bonus.critBonus;
    if(bonus.techBonus) affinity.techBonus = (affinity.techBonus||0) + bonus.techBonus;
    if(bonus.flatDamage) affinity.flatDamage = (affinity.flatDamage||0) + bonus.flatDamage;
  }
  return affinity;
}''',
    'affinity mastery upgrade'
)


# ---------- new player: derive/apply mastery rather than old generic tiers ----------
replace_once(
"""  // class mastery bonuses
  if(m.kills >= MASTERY_TIERS[0]){ p.maxHp += 4; p.hp += 4; }
  if(m.kills >= MASTERY_TIERS[1]){ const pas = MASTERY_PASSIVE[cls.id]; if(pas) pas.apply(p); }
  if(m.wins  >= MASTERY_WINS_T3){ p.dmgBonus += 1; p.mastered = true; }""",
"""  // specialized class mastery bonuses
  applyMasteryBonuses(p, cls.id, m);
  p.mastered = p.masteryLevel >= 6;""",
'newPlayer mastery application'
)


# ---------- show nameplate directly in the in-run HUD ----------
replace_once(
"""  $('#stClass').textContent = p.className.toUpperCase();""",
"""  $('#stClass').innerHTML = p.nameplate
    ? `<span class=\"hudNameplate ${p.masteryLevel>=6?'legendary':''}\">${p.nameplate}</span>${p.className.toUpperCase()}`
    : p.className.toUpperCase();""",
'HUD mastery nameplate'
)


# ---------- enrich the character sheet mastery presentation ----------
replace_once(
"""  $('#sheetTitle').textContent = `${P.className.toUpperCase()} // STATUS`;""",
"""  $('#sheetTitle').textContent = `${P.nameplate ? P.nameplate+' // ' : ''}${P.className.toUpperCase()} // STATUS`;""",
'character sheet title nameplate'
)

replace_once(
"""    <section class=\"sheetSection\">
      <h3>CLASS IDENTITY</h3>
      <div class=\"sheetAffinity ${affinity?'':'inactive'}\">""",
"""    <section class=\"sheetSection\">
      <h3>CLASS IDENTITY</h3>
      <div class=\"sheetItem\"><b>MASTERY LEVEL ${P.masteryLevel||0}/6 — ${getMasteryRankName(P.masteryLevel||0)}</b><small>${P.nameplate ? `Nameplate: ${P.nameplate}` : 'No mastery nameplate unlocked yet.'}</small></div>
      <div class=\"sheetAffinity ${affinity?'':'inactive'}\">""",
'character sheet mastery level'
)


# ---------- replace ability resolution with default + alternate variants ----------
ability_resolution = r'''  if(useAbility){
    const ab = P.ability;
    ab.cdLeft = Math.max(0, ab.cd - Math.max(0,P.cdrBonus));
    ab.ready = false;
    const abilityId = ab.id || '';

    if(abilityId==='netrunner_quickhack'){
      const targetScale = Math.max(1, Math.round(c.enemy.maxHp*0.08));
      let d = rnd(6,11) + P.tech + P.dmgBonus + targetScale;
      totalDmg = d;
      const stunChance = Math.min(0.50, 0.25 + P.tech*0.02);
      const stunned = Math.random() < stunChance;
      c.enemy.def = Math.max(0, c.enemy.def-1);
      print(`<span class="tag hack">QUICKHACK</span> You breach ${c.enemy.name}'s ICE for <b>${totalDmg}</b> tech damage (armor ignored). <span class="accent">Armor -1.</span>${stunned?' <span class="warn">Target stunned — skips next attack.</span>':''}`);
      c.enemy.hp -= totalDmg;
      c.enemyStunned = stunned;
    }
    else if(abilityId==='netrunner_daemon'){
      const targetScale = Math.max(1, Math.round(c.enemy.maxHp*0.05));
      const d = rnd(3,6) + P.tech + P.dmgBonus + targetScale;
      const bleed = Math.max(2, Math.round(P.tech*0.7));
      const stunned = Math.random() < 0.70;
      c.enemy.hp -= d;
      c.enemyBleed = (c.enemyBleed||0) + bleed;
      c.enemyStunned = stunned;
      totalDmg = d;
      print(`<span class="tag hack">DAEMON CASCADE</span> Malicious code tears through the target for <b>${d}</b> tech damage. <span class="warn">BLEED ${bleed}</span>${stunned?' <span class="accent">Target stunned.</span>':''}`);
    }
    else if(abilityId==='chrome_berserk'){
      const missing = 1-(P.hp/P.maxHp);
      let d = rnd(...P.dmgRange) + Math.round(missing*10) + P.dmgBonus - c.enemy.def;
      d = Math.max(1,d);
      const humCost = Math.max(1,3-(P._chromeAbilityDiscount||0));
      P.humanity = clamp(P.humanity-humCost,0,P.maxHumanity);
      print(`<span class="tag crit">BERSERK</span> Rage fuels the chrome. <b>${d}</b> damage. <span class="warn">-${humCost} Humanity.</span>`);
      c.enemy.hp -= d; totalDmg=d;
      checkCyberpsychosis(P);
    }
    else if(abilityId==='chrome_groundpound'){
      const missing = 1-(P.hp/P.maxHp);
      let d = rnd(...P.weapon.dmg) + P.dmgBonus + P.def + Math.round(missing*6) - c.enemy.def;
      d = Math.max(1,d);
      const humCost = Math.max(1,5-(P._chromeAbilityDiscount||0));
      const stunned = Math.random()<0.40;
      P.humanity = clamp(P.humanity-humCost,0,P.maxHumanity);
      c.enemy.hp -= d;
      c.enemyStunned = stunned;
      totalDmg=d;
      print(`<span class="tag crit">GROUND POUND</span> Chrome hits pavement and target alike for <b>${d}</b> damage. <span class="warn">-${humCost} Humanity.</span>${stunned?' <span class="accent">Target stunned.</span>':''}`);
      checkCyberpsychosis(P);
    }
    else if(abilityId==='samurai_blade_dance'){
      let d = rnd(...P.dmgRange) + P.dmgBonus - c.enemy.def;
      d=Math.max(1,d)*2;
      const followMult = 0.6 + (P._samuraiMastery?0.20:0);
      print(`<span class="tag crit">BLADE DANCE</span> Guaranteed critical — <b>${d}</b> damage, then a follow-up strike!`);
      c.enemy.hp -= d;
      let d2 = Math.max(1, Math.round((rnd(...P.dmgRange)+P.dmgBonus-c.enemy.def)*followMult));
      c.enemy.hp -= d2;
      print(`Follow-up strike: <b>${d2}</b> more damage.`);
      totalDmg = d+d2;
    }
    else if(abilityId==='samurai_iaijutsu'){
      const mult = P._samuraiMastery ? 3.4 : 3.0;
      let d = Math.round((rnd(...P.weapon.dmg)+P.dmgBonus)*mult) - Math.floor(c.enemy.def*0.5);
      d = Math.max(1,d);
      c.enemy.hp -= d;
      totalDmg=d;
      anyCrit=true;
      effectsHtml += applyHitEffects(P,c,d,true);
      print(`<span class="tag crit">IAIJUTSU</span> One draw. One cut. <b>${d}</b> damage through half armor. <span class="warn">CRITICAL!</span>${effectsHtml}`);
    }
    else if(abilityId==='rocker_rally'){
      P.dmgBonus += 2;
      P.def += 1;
      P.cool += 2;
      c.rallyTurns = 3 + (P._rockerEncore||0);
      print(`<span class="tag hack">RALLY CRY</span> Adrenaline and distortion pedals. <span class="good">+2 dmg, +1 def, +2 cool for ${c.rallyTurns} turns.</span>`);
    }
    else if(abilityId==='rocker_feedback'){
      const suppress = 2 + (P._rockerEncore||0);
      let d = rnd(4,7) + P.cool + P.dmgBonus + (P._rockerEncore?2:0) - Math.floor(c.enemy.def*0.5);
      d = Math.max(1,d);
      c.enemy.hp -= d;
      c.enemy.dmg = [Math.max(1,c.enemy.dmg[0]-suppress), Math.max(1,c.enemy.dmg[1]-suppress)];
      totalDmg=d;
      print(`<span class="tag hack">FEEDBACK BURST</span> Sonic overload hits for <b>${d}</b> damage. <span class="good">Enemy damage -${suppress} for this fight.</span>`);
    }
    else if(abilityId==='nomad_scavenger'){
      c.guaranteedLoot = true;
      if(P._nomadSalvage) c.contractBonus = Math.max(c.contractBonus||0,P._nomadSalvage);
      print(`<span class="tag hack">SCAVENGER INSTINCT</span> You mark this kill for salvage. Guaranteed bonus loot after the fight.${P._nomadSalvage?' <span class="good"> +20% eddies on kill.</span>':''}`);
    }
    else if(abilityId==='nomad_roadwarrior'){
      let d = Math.round((rnd(...P.weapon.dmg)+P.dmgBonus+P.def)*1.3) - c.enemy.def;
      d = Math.max(1,d);
      c.enemy.hp -= d;
      c.guarding = true;
      c.guardReduction = 0.35;
      if(P._nomadSalvage) c.contractBonus = Math.max(c.contractBonus||0,P._nomadSalvage);
      totalDmg=d;
      print(`<span class="tag hack">ROAD WARRIOR</span> You crash through the line for <b>${d}</b> damage, then brace. <span class="good">35% Guard on the counterattack.</span>${P._nomadSalvage?' <span class="good"> Kill marked +20% eddies.</span>':''}`);
    }
    else if(abilityId==='fixer_connections'){
      let d = rnd(5,8) + P.tech + P.cool + P.dmgBonus;
      d = Math.max(1,d);
      c.enemy.hp -= d;
      totalDmg = d;
      const mark = 0.25 + (P._fixerContractBonus||0);
      c.contractBonus = Math.max(c.contractBonus||0, mark);
      print(`<span class="tag hack">CONNECTIONS</span> A contact paints the target from off-grid. <b>${d}</b> armor-piercing damage. <span class="good">Target marked: +${Math.round(mark*100)}% eddies on kill.</span>`);
    }
    else if(abilityId==='fixer_professional'){
      let d = rnd(4,6) + P.tech + P.cool + P.dmgBonus;
      d = Math.max(1,d);
      c.enemy.hp -= d;
      c.enemy.def = Math.max(0,c.enemy.def-2);
      const mark = 0.15 + (P._fixerContractBonus||0);
      c.contractBonus = Math.max(c.contractBonus||0,mark);
      totalDmg=d;
      print(`<span class="tag hack">PROFESSIONAL COURTESY</span> A clean off-book hit deals <b>${d}</b> armor-piercing damage. <span class="accent">Armor -2.</span> <span class="good">+${Math.round(mark*100)}% eddies on kill.</span>`);
    }
    else if(abilityId==='solo_killshot'){
      const affinity = getClassWeaponAffinity(P);
      let base = rnd(...P.weapon.dmg) + P.dmgBonus + (P.weapon.tech?P.tech:0);
      if(P._ballisticMastery && P.weapon.tag==='ballistic') base += P._ballisticMastery;
      if(affinity){
        base += (affinity.techBonus||0) + (affinity.flatDamage||0);
        if(affinity.damageMult) base = Math.round(base*affinity.damageMult);
      }
      const d = Math.max(1,Math.round(base*2.2));
      c.enemy.hp -= d;
      totalDmg=d;
      anyCrit=true;
      effectsHtml += applyHitEffects(P,c,d,true);
      print(`<span class="tag crit">KILLSHOT</span> One perfect line through the target. <b>${d}</b> damage, armor ignored. <span class="warn">CRITICAL!</span>${effectsHtml}`);
    }
    else {
      let d = Math.round((rnd(...P.dmgRange)+P.dmgBonus)*1.6) - Math.max(0,c.enemy.def-2);
      d = Math.max(1,d);
      print(`<span class="tag crit">OVERWATCH</span> Combat reflexes kick in. <b>${d}</b> damage, armor mostly bypassed.`);
      c.enemy.hp -= d; totalDmg=d;
    }
  } else {
    const armorPerHit'''
sub_once(
    r"  if\(useAbility\)\{.*?\n  \} else \{\n    const armorPerHit",
    ability_resolution,
    'player ability resolution'
)


# Legendary Solo capstone applies to normal ballistic weapon attacks too.
replace_once(
"""      let base = rnd(...P.weapon.dmg) + P.dmgBonus + (P.weapon.tech?P.tech:0);
      if(affinity){""",
"""      let base = rnd(...P.weapon.dmg) + P.dmgBonus + (P.weapon.tech?P.tech:0);
      if(P._ballisticMastery && P.weapon.tag==='ballistic') base += P._ballisticMastery;
      if(affinity){""",
'ballistic mastery normal attack'
)


# ---------- mastery screen: show all ranks/rewards and next requirement ----------
mastery_screen = r'''function showMastery(){
  $('#app').classList.remove('metaShopOpen');
  log.innerHTML='';
  print('<span class="tag purp">CLASS MASTERY</span> Six ranks per class. Kills build experience; higher ranks also require successful runs.', 'sys');

  CLASSES.forEach(c=>{
    const m = META.mastery[c.id] || {kills:0,wins:0};
    const level = getMasteryLevel(m);
    const plate = getMasteryNameplate(c.id,m);
    const next = MASTERY_RANKS[level] || null;
    const pct = next ? clamp((m.kills||0)/next.kills*100,0,100) : 100;
    const path = MASTERY_PATHS[c.id];
    const rewards = MASTERY_RANKS.map(rank=>{
      const unlocked = level >= rank.level;
      const req = `${rank.kills} kills${rank.wins?` + ${rank.wins} win${rank.wins===1?'':'s'}`:''}`;
      return `<div class="masteryReward ${unlocked?'unlocked':''}">${unlocked?'✓':'○'} <b>L${rank.level} ${rank.name}</b> — ${req}<br><span class="flavor">${path.rewards[rank.level].desc}</span></div>`;
    }).join('');

    print(`
      <div class="entry">
        <p><b class="accent">${c.name}</b> — Mastery <b>${level}/6</b>${plate?` <span class="masteryPlate ${level>=6?'legendary':''}">${plate}</span>`:''}</p>
        <p class="flavor">${m.kills||0} kills · ${m.wins||0} wins · ${level>=6?'LEGEND COMPLETE':`Next: ${next.kills} kills${next.wins?` + ${next.wins} win${next.wins===1?'':'s'}`:''}`}</p>
        <div class="mbar"><i style="width:${pct}%"></i></div>
        ${rewards}
      </div>
    `);
  });

  actions([{ label:'Back to title', fn:()=>showTitle() }], {single:true});
}'''
sub_once(
    r"function showMastery\(\)\{.*?\n\}\n\n// ================= HISTORY",
    mastery_screen + "\n\n// ================= HISTORY",
    'mastery screen'
)


# ---------- ability loadout selection unlocked at Mastery 4 ----------
class_select = r'''function showAbilitySelect(cls, hardMode){
  $('#app').classList.remove('metaShopOpen');
  log.innerHTML='';

  const m = META.mastery[cls.id] || {kills:0,wins:0};
  const level = getMasteryLevel(m);
  const alt = ALT_ABILITIES[cls.id];
  const standard = {...cls.ability};

  print(`<span class="tag purp">SPECIALIZATION</span> <b>${cls.name}</b> Mastery ${level}/6 — choose the special ability for this run.`, 'sys');

  const wrap = document.createElement('div');
  wrap.className='cardgrid';

  [
    {ability:standard, label:'STANDARD'},
    {ability:alt, label:'ALTERNATE'}
  ].forEach(choice=>{
    const div = document.createElement('div');
    div.className='card';
    div.innerHTML = `<h3>${choice.ability.name} <span class="flavor">// ${choice.label}</span></h3><div>${choice.ability.desc}</div><div class="stats">Cooldown <b>${choice.ability.cd}</b></div>`;
    div.onclick = ()=>{
      cls.ability = {...choice.ability};
      startRun(cls,hardMode);
    };
    wrap.appendChild(div);
  });

  log.appendChild(wrap);
  actions([{label:'Back to classes', fn:()=>showClassSelect(hardMode)}], {single:true});
}

function showClassSelect(hardMode){
  $('#app').classList.remove('metaShopOpen');
  hardMode = !!hardMode;
  const overwatchUnlocked = META.purchased.includes('perk_overwatch');
  log.innerHTML='';
  print('<span class="tag">CHARACTER CREATION</span> Choose your build. Stats roll with small variance each run — no two mercs are identical.', 'sys');
  if(overwatchUnlocked){
    print(`<span class="tag purp">OVERWATCH MODE</span> unlocked — tougher enemies, 1.5x credit payout. Currently <b class="${hardMode?'bad':'good'}">${hardMode?'ON':'OFF'}</b>. Toggle below, then pick a class.`);
  }

  const wrap = document.createElement('div');
  wrap.className='cardgrid';
  CLASSES.forEach(c=>{
    const m = META.mastery[c.id] || {kills:0,wins:0};
    const level = getMasteryLevel(m);
    const plate = getMasteryNameplate(c.id,m);
    const altUnlocked = level>=4;
    const div = document.createElement('div');
    div.className='card';
    div.innerHTML = `<h3>${c.name}${plate?` <span class="masteryPlate ${level>=6?'legendary':''}">${plate}</span>`:''}</h3><div>${c.tagline}</div>
      <div class="stats">HP <b>${c.hp}</b> · DMG <b>${c.dmg[0]}-${c.dmg[1]}</b> · DEF <b>${c.def}</b> · TECH <b>${c.tech}</b> · COOL <b>${c.cool}</b> · HUMANITY <b>${c.humanity}</b><br>
      Weapon: <b>${WEAPON_BASE[c.weapon].name}</b> · Ability: <b>${c.ability.name}</b> — ${c.ability.desc}<br>
      Affinity: <b>${CLASS_WEAPON_AFFINITY[c.id].name}</b> — ${CLASS_WEAPON_AFFINITY[c.id].desc}<br>
      Mastery: <b>${level}/6 ${getMasteryRankName(level)}</b> · ${m.kills||0} kills / ${m.wins||0} wins${altUnlocked?`<br><span class="purp">Alternate special unlocked: ${ALT_ABILITIES[c.id].name}</span>`:''}</div>`;
    div.onclick = ()=>{
      const clone = JSON.parse(JSON.stringify(c));
      clone.hp += rnd(-3,3);
      clone.def += rnd(0,1);
      clone.cool += rnd(-1,1);
      if(altUnlocked) showAbilitySelect(clone,hardMode);
      else startRun(clone,hardMode);
    };
    wrap.appendChild(div);
  });
  log.appendChild(wrap);

  if(overwatchUnlocked){
    actions([
      { label: hardMode?'Turn Overwatch Mode OFF':'Turn Overwatch Mode ON', cls:hardMode?'':'danger', fn:()=>showClassSelect(!hardMode) },
      { label:'Back', fn:()=>showTitle() }
    ]);
  } else {
    actions([{ label:'Back', fn:()=>showTitle() }], {single:true});
  }
}'''
sub_once(
    r"function showClassSelect\(hardMode\)\{.*?\n\}\n\n// ================= BOOT",
    class_select + "\n\n// ================= BOOT",
    'class selection specialization'
)


# ---------- end-of-run mastery level-up feedback ----------
replace_once(
"""  if(!META.mastery[P.cls]) META.mastery[P.cls] = {kills:0, wins:0};
  META.mastery[P.cls].kills += run.kills;
  if(won) { META.runsWon++; META.mastery[P.cls].wins += 1; }""",
"""  if(!META.mastery[P.cls]) META.mastery[P.cls] = {kills:0, wins:0};
  const masteryBefore = getMasteryLevel(META.mastery[P.cls]);
  META.mastery[P.cls].kills += run.kills;
  if(won) { META.runsWon++; META.mastery[P.cls].wins += 1; }
  const masteryAfter = getMasteryLevel(META.mastery[P.cls]);""",
'end-run mastery level tracking'
)

replace_once(
"""  print(`<span class=\"purp\">+${earnedCredits} credits</span> earned for the Fixer Network. <span class=\"flavor\">Legend record: ${META.runsWon} wins / ${META.runsStarted} runs.</span>`);""",
"""  print(`<span class=\"purp\">+${earnedCredits} credits</span> earned for the Fixer Network. <span class=\"flavor\">Legend record: ${META.runsWon} wins / ${META.runsStarted} runs.</span>`);
  if(masteryAfter>masteryBefore){
    for(let lvl=masteryBefore+1; lvl<=masteryAfter; lvl++){
      const rank = MASTERY_RANKS.find(r=>r.level===lvl);
      const reward = MASTERY_PATHS[P.cls].rewards[lvl];
      print(`<span class=\"tag purp\">MASTERY UP</span> <b>${P.className} Level ${lvl} — ${rank.name}</b><br><span class=\"purp\">${reward.desc}</span>`);
    }
  }""",
'end-run mastery reward feedback'
)


path.write_text(text)
