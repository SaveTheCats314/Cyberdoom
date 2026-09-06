from pathlib import Path
import re

path = Path('index.html')
text = path.read_text()


def replace_once(old, new, label):
    global text
    if old not in text:
        raise SystemExit(f'Patch target not found: {label}')
    text = text.replace(old, new, 1)


# --- HUD: dedicated loadout start state ---
replace_once(
"""  $('#stFloor').textContent =
    `${S.run.actName.toUpperCase()} ${S.run.node+1}/${S.run.actLen}`;""",
"""  $('#stFloor').textContent = S.run.starting
    ? `${S.run.actName.toUpperCase()} // LOADOUT`
    : `${S.run.actName.toUpperCase()} ${S.run.node+1}/${S.run.actLen}`;""",
'run HUD loadout state'
)


# --- baseline unlock pools + save migration ---
replace_once(
"""function defaultMeta(){
  return {
    runsStarted:0, runsWon:0, bestDistrict:0, credits:0,
    mastery:{}, // classId -> {kills:0, wins:0}
    unlocks:{ relics:['bloodwire','scavenger_eye','ghost_runner','overclock_battery'],
              mutations:['bleed','vampiric'],
              cyberware:['optics','reflex','plating','arms','legs'] },
    purchased:[], // meta-shop perk ids
    log:[]
  };
}""",
"""const BASE_RELIC_UNLOCKS = [
  'bloodwire','scavenger_eye','ghost_runner','overclock_battery',
  'deadeye_lens','neural_anchor','titanium_spine','reflex_tuner',
  'chrome_heart','medtech_patch','guardian_daemon','combat_predictor'
];

const BASE_CHROME_UNLOCKS = [
  'optics','reflex','plating','arms','legs',
  'bloodpump','smartlink','ramdeck','optical_camo','pain_editor','synlungs'
];

function defaultMeta(){
  return {
    runsStarted:0, runsWon:0, bestDistrict:0, credits:0,
    progressionV3:true,
    mastery:{}, // classId -> {kills:0, wins:0}
    unlocks:{ relics:[...BASE_RELIC_UNLOCKS],
              mutations:['bleed','vampiric'],
              cyberware:[...BASE_CHROME_UNLOCKS] },
    purchased:[], // meta-shop perk ids
    log:[]
  };
}""",
'base unlock pools'
)

replace_once(
"""async function loadSlot(n){
  const existing = await peekSlot(n);
  META = existing || defaultMeta();
  SLOT = n;
  updateHeader();
}""",
"""async function loadSlot(n){
  const existing = await peekSlot(n);
  META = existing || defaultMeta();

  META.unlocks = META.unlocks || {};
  META.unlocks.relics = [...new Set([...(META.unlocks.relics||[]), ...BASE_RELIC_UNLOCKS])];
  META.unlocks.cyberware = [...new Set([...(META.unlocks.cyberware||[]), ...BASE_CHROME_UNLOCKS])];
  META.unlocks.mutations = META.unlocks.mutations || ['bleed','vampiric'];

  // Existing saves used district index 3 for Corpo Plaza and 4 for Arasaka Tower.
  if(!META.progressionV3){
    if((META.bestDistrict||0) >= 3) META.bestDistrict += 1;
    META.progressionV3 = true;
  }

  SLOT = n;
  updateHeader();
}""",
'load slot migration'
)


# --- expand chrome pool ---
replace_once(
"""  { id:'tech',     slot:'Optics',   name:'Tech Scanner',        desc:'+3 tech (armor-piercing dmg)', apply:p=>p.tech+=3,        hum:5 },
];""",
"""  { id:'tech',     slot:'Optics',   name:'Tech Scanner',        desc:'+3 tech (armor-piercing dmg)', apply:p=>p.tech+=3,        hum:5 },
  { id:'bloodpump', slot:'Circulatory System', name:'Blood Pump', desc:'+6 max HP', apply:p=>{p.maxHp+=6; p.hp+=6;}, hum:7 },
  { id:'smartlink', slot:'Hands', name:'Smart Link', desc:'+1 damage and +8% crit chance', apply:p=>{p.dmgBonus+=1; p.critBonus+=0.08;}, hum:6 },
  { id:'ramdeck', slot:'Frontal Cortex', name:'RAM Accelerator', desc:'+2 Tech and -1 ability cooldown', apply:p=>{p.tech+=2; p.cdrBonus+=1;}, hum:9 },
  { id:'optical_camo', slot:'Integumentary System', name:'Optical Camo', desc:'+8% dodge and +2 Cool', apply:p=>{p.dodge+=0.08; p.cool+=2;}, hum:10 },
  { id:'pain_editor', slot:'Nervous System', name:'Pain Editor', desc:'+2 defense and +4 max HP', apply:p=>{p.def+=2; p.maxHp+=4; p.hp+=4;}, hum:9 },
  { id:'synlungs', slot:'Circulatory System', name:'Syn-Lungs', desc:'+1 HP regeneration each turn and +2 Cool', apply:p=>{p.regen+=1; p.cool+=2;}, hum:7 },
];""",
'expanded cyberware pool'
)


# --- expand relic pool ---
replace_once(
"""  { id:\"widows_kiss\",      name:\"Widow's Kiss\",     desc:'The first attack in every fight is a guaranteed critical.' },
];""",
"""  { id:\"widows_kiss\",      name:\"Widow's Kiss\",     desc:'The first attack in every fight is a guaranteed critical.' },
  { id:'deadeye_lens',     name:'Deadeye Lens',      desc:'+10% critical chance.', apply:p=>p.critBonus+=0.10 },
  { id:'neural_anchor',    name:'Neural Anchor',     desc:'+2 Tech.', apply:p=>p.tech+=2 },
  { id:'titanium_spine',   name:'Titanium Spine',    desc:'+2 defense.', apply:p=>p.def+=2 },
  { id:'reflex_tuner',     name:'Reflex Tuner',      desc:'+3 Cool.', apply:p=>p.cool+=3 },
  { id:'chrome_heart',     name:'Chrome Heart',      desc:'+6 max HP, but -5 max Humanity.', apply:p=>{p.maxHp+=6; p.hp+=6; p.maxHumanity=Math.max(25,p.maxHumanity-5); p.humanity=Math.min(p.humanity,p.maxHumanity);} },
  { id:'medtech_patch',    name:'Medtech Patch',     desc:'Combat stims heal 35% max HP instead of 25%.' },
  { id:'guardian_daemon',  name:'Guardian Daemon',   desc:'Guard reduces the next incoming hit by 65% instead of 50%.' },
  { id:'combat_predictor', name:'Combat Predictor',  desc:'+8% chance to successfully Evade.' },
];""",
'expanded relic pool'
)


# --- longer run structure with a separate midboss gate ---
replace_once(
"""const ACTS = [
  { name:'Watson',      len:4 },
  { name:'Pacifica',    len:4 },
  { name:'Corpo Plaza', len:4 },
  { name:'Arasaka Tower', len:1, boss:true },
];""",
"""const ACTS = [
  { name:'Watson',          len:7 },
  { name:'Pacifica',        len:8 },
  { name:'Blackwall Relay', len:1, midboss:true },
  { name:'Corpo Plaza',     len:9 },
  { name:'Arasaka Tower',   len:1, boss:true },
];""",
'longer act structure'
)

replace_once(
"""  S.run = { player, act:0, node:0, actName:ACTS[0].name, actLen:ACTS[0].len, heat:0,
            kills:0, eliteKills:0, actBuffs:[], actEddiesMult:1, actContactDone:false, hardMode: !!hardMode };""",
"""  S.run = { player, act:0, node:0, actName:ACTS[0].name, actLen:ACTS[0].len, heat:0,
            kills:0, eliteKills:0, actBuffs:[], actEddiesMult:1, actContactDone:false,
            starting:true, hardMode: !!hardMode };""",
'start run state'
)

replace_once(
"""  divider();
  nextNode();
}

function nextNode(){""",
"""  divider();
  runStartChoice();
}

function runStartChoice(){
  const P = S.run.player;
  S.run.starting = true;
  refreshStatus();

  print(`<span class=\"tag relic\">LOADOUT CACHE</span> Before you disappear into Watson, one last dead-drop waits under a flickering holo-ad. Take one edge into the run.`, 'sys');

  const choices = [...relicPool()]
    .filter(r=>!hasRelic(P,r.id))
    .sort(()=>Math.random()-0.5)
    .slice(0,3);

  const opts = choices.map(r=>({
    label:`Take ${r.name}`,
    sub:r.desc,
    cls:'purp',
    fn:()=>{
      grantRelic(P,r);
      S.run.starting=false;
      refreshStatus();
      divider();
      nextNode();
    }
  }));

  opts.push({
    label:'Take the eddies',
    sub:'+60 eddies instead of a relic',
    cls:'gold',
    fn:()=>{
      P.eddies += 60;
      print(`<span class=\"tag loot\">STARTING CAPITAL</span> <span class=\"good\">+60 eddies.</span>`);
      S.run.starting=false;
      refreshStatus();
      divider();
      nextNode();
    }
  });

  actions(opts);
}

function nextNode(){""",
'loadout cache start'
)


# Replace nextNode as a whole so act references refresh correctly after district transitions.
next_node_pattern = re.compile(r"function nextNode\(\)\{.*?\n\}\nfunction advance\(\)", re.S)
if not next_node_pattern.search(text):
    raise SystemExit('Patch target not found: nextNode function')

new_next_node = r'''function nextNode(){
  const run = S.run;
  let act = ACTS[run.act];
  refreshStatus();

  if(run.node >= act.len){
    revertActBuffs();
    run.act++;
    if(run.act >= ACTS.length){ return victory(); }
    run.node = 0;
    run.actContactDone = false;
    run.actEddiesMult = 1;
    act = ACTS[run.act];
    run.actName = act.name;
    run.actLen = act.len;
    print(`<span class="tag">DISTRICT</span> Entering <b class="accent">${run.actName}</b>...`, 'sys');
    divider();
    refreshStatus();
  }

  if(act.midboss) return midBossEncounter();
  if(act.boss) return bossEncounter();

  const contactNode = Math.max(2, Math.floor(act.len*0.35));
  if(!run.actContactDone && run.node===contactNode && act.len>3){
    run.actContactDone = true;
    return runContact();
  }

  let type;
  if(run.node === act.len-1){
    type='elite';
  }
  else{
    const roll = Math.random();
    if(roll<0.38) type='combat';
    else if(roll<0.58) type='event';
    else if(roll<0.72) type='shop';
    else if(roll<0.84) type='rest';
    else type='relic';
  }

  if(type==='combat') return startCombat(pick(ENEMY_POOL.street), false);
  if(type==='elite') return startCombat(pick(ENEMY_POOL.elite), true);
  if(type==='event') return runEvent();
  if(type==='shop') return runShop();
  if(type==='rest') return runRest();
  if(type==='relic') return runRelicCache();
}
function advance()'''
text = next_node_pattern.sub(new_next_node, text, count=1)


# --- keep normal district scaling stable despite inserted midboss act ---
scaled_pattern = re.compile(r"function scaledEnemy\(base, act, elite, hardMode\)\{.*?\n\}\n\nfunction startCombat", re.S)
if not scaled_pattern.search(text):
    raise SystemExit('Patch target not found: scaledEnemy function')

new_scaled = r'''function scaledEnemy(base, act, elite, hardMode){
  // Blackwall Relay sits at act index 2, but it should not inflate Corpo's normal scaling tier.
  const tier = act >= 3 ? act-1 : act;
  let hpScale = 1 + tier*0.35;
  let dmgScale = 1 + tier*0.35;

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
    def: base.def + Math.floor(tier*0.7),
    tech: !!base.tech,
    elite: !!elite || !!base.elite,
    berserk: !!base.berserk
  };
}

function startCombat'''
text = scaled_pattern.sub(new_scaled, text, count=1)


# --- new relic hooks for defense / healing ---
replace_once(
"""    0.65 + ((P.cool||0) * 0.015) + (hasRelic(P,'ghost_runner') ? 0.15 : 0)""",
"""    0.65 +
    ((P.cool||0) * 0.015) +
    (hasRelic(P,'ghost_runner') ? 0.15 : 0) +
    (hasRelic(P,'combat_predictor') ? 0.08 : 0)""",
'combat predictor evade hook'
)

replace_once(
"""    { label:'Use Stim', sub:`Heal 25% HP (${P.items.stims} left)`, disabled: P.items.stims<=0, fn:()=>useStim() },""",
"""    { label:'Use Stim', sub:`Heal ${hasRelic(P,'medtech_patch') ? '35' : '25'}% HP (${P.items.stims} left)`, disabled: P.items.stims<=0, fn:()=>useStim() },""",
'medtech stim label'
)

replace_once(
"""    { label:'Guard', sub:'Reduce the next incoming hit by 50%', cls:'gold', fn:()=>guardAction() },""",
"""    { label:'Guard', sub:`Reduce the next incoming hit by ${hasRelic(P,'guardian_daemon') ? '65' : '50'}%`, cls:'gold', fn:()=>guardAction() },""",
'guardian guard label'
)

stim_guard_pattern = re.compile(r"function useStim\(\)\{.*?\n\}\n\nfunction guardAction\(\)\{.*?\n\}\n\nfunction evadeAction", re.S)
if not stim_guard_pattern.search(text):
    raise SystemExit('Patch target not found: stim/guard functions')

new_stim_guard = r'''function useStim(){
  const P = S.run.player;
  P.items.stims--;
  const healPct = hasRelic(P,'medtech_patch') ? 0.35 : 0.25;
  const heal = Math.round(P.maxHp*healPct);
  P.hp = clamp(P.hp+heal, 0, P.maxHp);
  print(`<span class="tag hack">STIM</span> <span class="good">+${heal} HP.</span>`);
  refreshStatus();
  enemyTurn();
}

function guardAction(){
  const P = S.run.player;
  const c = S.run.combat;
  if(!c) return;

  const guardPct = hasRelic(P,'guardian_daemon') ? 65 : 50;
  c.guarding = true;
  c.evading = false;
  c.guardReduction = guardPct/100;

  print(
    `<span class="tag hack">GUARD</span> You brace for impact. ` +
    `<span class="good">The next incoming hit will be reduced by ${guardPct}%.</span>`
  );

  enemyTurn();
}

function evadeAction'''
text = stim_guard_pattern.sub(new_stim_guard, text, count=1)

replace_once(
"""    if(c.guarding && d > 0){
      const original = Math.max(0,d);
      d = Math.ceil(original * 0.5);

      print(
        `<span class=\"tag hack\">GUARD</span> You absorb the hit. ` +
        `<span class=\"good\">${original} → ${d} damage.</span>`
      );
    }

    c.guarding = false;""",
"""    if(c.guarding && d > 0){
      const original = Math.max(0,d);
      const reduction = c.guardReduction || 0.50;
      d = Math.ceil(original * (1-reduction));

      print(
        `<span class=\"tag hack\">GUARD</span> You absorb the hit. ` +
        `<span class=\"good\">${original} → ${d} damage.</span>`
      );
    }

    c.guarding = false;
    c.guardReduction = 0;""",
'guardian daemon damage hook'
)


# --- reward tier respects inserted midboss + midboss bounty ---
replace_once(
"""  let eddies = rnd(10,25) + S.run.act*8;""",
"""  const rewardTier = S.run.act >= 3 ? S.run.act-1 : S.run.act;
  let eddies = rnd(10,25) + rewardTier*8 + (c.midboss ? 40 : 0);""",
'midboss reward tier'
)


# --- dedicated mid-game boss ---
replace_once(
"""// ================= BOSS: ADAM SMASHER =================
function bossEncounter(){""",
"""// ================= MIDBOSS: BLACKWALL RELAY =================
function midBossEncounter(){
  print(`<span class=\"tag boss\">BLACKWALL RELAY</span>`, 'sys');
  print(`<span class=\"flavor\">The route out of Pacifica goes dark. NetWatch has burned every exit except one, and something armored is standing in it.</span>`);
  print(`<b class=\"bad\">NETWATCH WARDEN</b> locks onto your signal. Its hunter-killer rig is built to survive runners, solos, and anyone unlucky enough to be nearby.`);
  actions([{ label:'Breach the relay', sub:'Mid-run boss — relic drop + bonus eddies', cls:'danger', fn:()=>startMidBossFight() }], {single:true});
}

function startMidBossFight(){
  const run = S.run;
  const hardBonus = run.hardMode ? 1.2 : 1;
  const heatBonus = 1 + (run.heat||0)*0.05;
  const hp = Math.round(90 * hardBonus * heatBonus);
  const boss = {
    name:'NetWatch Warden',
    maxHp:hp,
    hp,
    dmg:[Math.round(7*hardBonus), Math.round(11*hardBonus)],
    def:4,
    tech:true,
    elite:true,
    boss:true,
    berserk:true
  };

  run.combat = {
    enemy:boss,
    midboss:true,
    enemyBleed:0,
    firstHitUsed:false
  };

  refreshStatus();
  combatMenu();
}

// ================= BOSS: ADAM SMASHER =================
function bossEncounter(){""",
'midboss encounter'
)


# --- credits / best district labels for five-stage run ---
replace_once(
"""  const base = [6, 12, 20, 32][run.act] || 6;""",
"""  const base = [8, 16, 26, 34, 46][run.act] || 8;""",
'run credit curve'
)

replace_once(
"""${['Watson','Pacifica','Corpo Plaza','Arasaka Tower'][data.bestDistrict-1]||'—'}""",
"""${['Watson','Pacifica','Blackwall Relay','Corpo Plaza','Arasaka Tower'][data.bestDistrict-1]||'—'}""",
'save slot best district label'
)

replace_once(
"""${['—','Watson','Pacifica','Corpo Plaza','ARASAKA TOWER'][META.bestDistrict]||'—'}""",
"""${['—','Watson','Pacifica','Blackwall Relay','Corpo Plaza','ARASAKA TOWER'][META.bestDistrict]||'—'}""",
'title best district label'
)

path.write_text(text)
