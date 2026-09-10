from pathlib import Path
import re

path = Path('index.html')
text = path.read_text()


def replace_once(old, new, label):
    global text
    if old not in text:
        raise SystemExit(f'Patch target not found: {label}')
    text = text.replace(old, new, 1)


def regex_once(pattern, replacement, label):
    global text
    text2, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if count != 1:
        raise SystemExit(f'Patch target not found/ambiguous: {label} ({count})')
    text = text2

# ---------------------------------------------------------------
# Rarity UI
# ---------------------------------------------------------------
replace_once(
"""  .cardgrid{display:grid; gap:10px;}""",
"""  .rarity{
    display:inline-block;
    padding:1px 5px;
    border:1px solid currentColor;
    border-radius:3px;
    font-size:8px;
    font-weight:bold;
    letter-spacing:.7px;
    line-height:1.4;
    vertical-align:1px;
    white-space:nowrap;
  }
  .rarity.common{color:#929aa4;}
  .rarity.uncommon{color:#58e68b;}
  .rarity.rare{color:#4da3ff;}
  .rarity.epic{color:#b26bff;}
  .rarity.legendary{color:#ffd84a; text-shadow:0 0 7px rgba(255,216,74,.18);}

  .cardgrid{display:grid; gap:10px;}""",
'rarity CSS'
)

# ---------------------------------------------------------------
# Rarity helpers + class relic definitions
# ---------------------------------------------------------------
anchor = """function getActiveRelicSynergies(P){
  return RELIC_SYNERGIES.filter(s=>s.relics.every(r=>hasRelic(P,r)));
}

// ---- fixer contact boons"""

block = r'''function getActiveRelicSynergies(P){
  return RELIC_SYNERGIES.filter(s=>s.relics.every(r=>hasRelic(P,r)));
}

const RARITY_NAMES = {
  common:'COMMON', uncommon:'UNCOMMON', rare:'RARE', epic:'EPIC', legendary:'LEGENDARY'
};
const RARITY_WEIGHTS = { common:40, uncommon:28, rare:18, epic:10, legendary:4 };

const STANDARD_RELIC_RARITY = {
  deadeye_lens:'common', neural_anchor:'common', titanium_spine:'common', reflex_tuner:'common',
  bloodwire:'uncommon', scavenger_eye:'uncommon', ghost_runner:'uncommon', medtech_patch:'uncommon', combat_predictor:'uncommon',
  overclock_battery:'rare', guardian_daemon:'rare', chrome_heart:'rare', loyalty_chip:'rare',
  adrenal_plug:'epic', second_wind:'legendary', widows_kiss:'legendary'
};

function rarityBadge(rarity){
  const r = rarity || 'common';
  return `<span class="rarity ${r}">${RARITY_NAMES[r]||String(r).toUpperCase()}</span>`;
}
function relicRarity(relic){ return relic?.rarity || STANDARD_RELIC_RARITY[relic?.id] || 'uncommon'; }
function cyberwareRarity(cw){
  if(!cw) return 'uncommon';
  if(cw.hum>=11) return 'legendary';
  if(cw.hum>=9) return 'epic';
  if(cw.hum>=7) return 'rare';
  return 'uncommon';
}
function weaponRarityFromTier(tier){
  if(tier>=7) return 'legendary';
  if(tier>=5) return 'epic';
  if(tier>=3) return 'rare';
  if(tier>=1) return 'uncommon';
  return 'common';
}
function weightedPickByRarity(items, rarityFn){
  if(!items.length) return null;
  const weighted = items.map(item=>({item, weight:RARITY_WEIGHTS[(rarityFn?rarityFn(item):item.rarity)||'common']||1}));
  const total = weighted.reduce((s,x)=>s+x.weight,0);
  let roll = Math.random()*total;
  for(const entry of weighted){
    roll -= entry.weight;
    if(roll<=0) return entry.item;
  }
  return weighted[weighted.length-1].item;
}
function weightedSampleByRarity(items, count, rarityFn){
  const pool=[...items], out=[];
  while(pool.length && out.length<count){
    const item=weightedPickByRarity(pool,rarityFn);
    if(!item) break;
    out.push(item);
    pool.splice(pool.indexOf(item),1);
  }
  return out;
}

const CLASS_RELICS = {
  solo:[
    {id:'solo_dead_center',name:'Dead Center',rarity:'rare',desc:'The first weapon attack each fight deals +40% damage.',apply:p=>p._soloDeadCenter=0.40},
    {id:'solo_cover_discipline',name:'Cover Discipline',rarity:'rare',desc:'Guard primes your next weapon attack for +35% damage.',apply:p=>p._soloCoverDiscipline=0.35},
    {id:'solo_combat_tempo',name:'Combat Tempo',rarity:'rare',desc:'Every kill reduces your special ability cooldown by 1.',apply:p=>p._killCooldown=(p._killCooldown||0)+1},
    {id:'solo_execution_license',name:'Execution License',rarity:'epic',desc:'Weapon attacks deal +35% damage to enemies below 40% HP.',apply:p=>p._executeMult=0.35},
    {id:'solo_armor_piercer',name:'Armor-Piercer Firmware',rarity:'epic',desc:'Pistol affinity attacks ignore 2 additional armor.',apply:p=>p._affinityArmorPierce=2},
    {id:'solo_blackhand_protocol',name:'Blackhand Protocol',rarity:'legendary',desc:'Every third weapon attack is a guaranteed crit and deals +50% damage.',apply:p=>p._blackhandProtocol=true},
  ],
  netrunner:[
    {id:'net_icebreaker',name:'ICEbreaker Daemon',rarity:'rare',desc:'Tech weapon attacks and damaging specials strip 1 enemy armor.',apply:p=>p._netIcebreaker=true},
    {id:'net_recursive_ping',name:'Recursive Ping',rarity:'rare',desc:'Damaging special abilities upload 3 bleed.',apply:p=>p._netRecursivePing=3},
    {id:'net_buffer_overflow',name:'Buffer Overflow',rarity:'rare',desc:'Stunning a target reduces your special cooldown by 1.',apply:p=>p._netBufferOverflow=1},
    {id:'net_ghost_ram',name:'Ghost RAM',rarity:'epic',desc:'Monowire critical hits reduce your special cooldown by 1.',apply:p=>p._netGhostRam=1},
    {id:'net_blackwall_tap',name:'Blackwall Tap',rarity:'epic',desc:'Damaging specials deal +40% bonus true damage but cost 4 Humanity.',apply:p=>p._netBlackwallTap=true},
    {id:'net_zero_day',name:'Zero Day',rarity:'legendary',desc:'Your first special ability each fight refreshes immediately after resolving.',apply:p=>p._netZeroDay=true},
  ],
  chrome:[
    {id:'chrome_metal_dividend',name:'Metal Dividend',rarity:'rare',desc:'Weapon attacks gain +1 damage per installed piece of chrome.',apply:p=>p._chromeMetalDividend=true},
    {id:'chrome_trauma_plate',name:'Trauma Plate',rarity:'rare',desc:'While below 50% HP, incoming damage is reduced by 20%.',apply:p=>p._chromeTraumaPlate=0.20},
    {id:'chrome_limiters_off',name:'Limiters Off',rarity:'rare',desc:'At critical Humanity (25% or less), weapon attacks deal +35% damage.',apply:p=>p._chromeLimitersOff=0.35},
    {id:'chrome_hydraulic_overdrive',name:'Hydraulic Overdrive',rarity:'epic',desc:'Gorilla Arms gain one additional hit per weapon attack.',apply:p=>p._chromeHydraulic=true},
    {id:'chrome_blood_machine',name:'Blood Machine',rarity:'epic',desc:'Kills heal 4% max HP per installed chrome, up to 20%.',apply:p=>p._chromeBloodMachine=true},
    {id:'chrome_full_conversion',name:'Full Conversion',rarity:'legendary',desc:'Chrome installs cost 50% less Humanity and grant +2 max HP each.',apply:p=>{p._fullConversion=true;const b=(p.cyberware?.length||0)*2;p.maxHp+=b;p.hp+=b;}},
  ],
  samurai:[
    {id:'samurai_perfect_draw',name:'Perfect Draw',rarity:'rare',desc:'Your first Katana weapon attack each fight is a guaranteed critical.',apply:p=>p._samuraiPerfectDraw=true},
    {id:'samurai_crimson_edge',name:'Crimson Edge',rarity:'rare',desc:'Katana critical hits inflict bleed equal to 25% of damage dealt.',apply:p=>p._samuraiCrimsonEdge=true},
    {id:'samurai_still_water',name:'Still Water',rarity:'rare',desc:'A successful Evade primes your next weapon hit as a guaranteed critical.',apply:p=>p._samuraiStillWater=true},
    {id:'samurai_riposte_core',name:'Riposte Core',rarity:'epic',desc:'Guard reflects 50% of prevented damage back at the attacker.',apply:p=>p._samuraiRiposte=0.50},
    {id:'samurai_flowing_steel',name:'Flowing Steel',rarity:'epic',desc:'Katana critical hits add a free follow-up strike for 35% damage.',apply:p=>p._samuraiFlowingSteel=0.35},
    {id:'samurai_no_second_strike',name:'No Second Strike',rarity:'legendary',desc:'Your first Katana weapon attack each fight deals +100% damage.',apply:p=>p._samuraiNoSecondStrike=true},
  ],
  rocker:[
    {id:'rocker_feedback_loop',name:'Feedback Loop',rarity:'rare',desc:'Rally Cry lasts +1 turn; Feedback Burst suppresses 1 extra enemy damage.',apply:p=>p._rockerFeedbackLoop=1},
    {id:'rocker_full_auto_chorus',name:'Full-Auto Chorus',rarity:'rare',desc:'Each successive SMG shot in a burst gains +1 damage.',apply:p=>p._rockerFullAutoChorus=true},
    {id:'rocker_stage_presence',name:'Stage Presence',rarity:'rare',desc:'Weapon attacks gain bonus damage equal to 25% of your Cool.',apply:p=>p._rockerStagePresence=true},
    {id:'rocker_encore_circuit',name:'Encore Circuit',rarity:'epic',desc:'Every kill reduces your special ability cooldown by 2.',apply:p=>p._killCooldown=(p._killCooldown||0)+2},
    {id:'rocker_riot_shield',name:'Riot Shield',rarity:'epic',desc:'Using a special ability grants 40% Guard against the counterattack.',apply:p=>p._rockerRiotShield=0.40},
    {id:'rocker_never_fade',name:'Never Fade Away',rarity:'legendary',desc:'Once per run, a lethal hit restores you to 35% HP and instantly readies your special.',apply:p=>p._rockerNeverFade=true},
  ],
  nomad:[
    {id:'nomad_pack_rat',name:'Pack Rat',rarity:'rare',desc:'Weapon inventory capacity increases from 6 to 8.',apply:p=>p.inventoryCap=8},
    {id:'nomad_road_armor',name:'Road Armor',rarity:'rare',desc:'The first damaging enemy hit each fight is reduced by 50%.',apply:p=>p._nomadRoadArmor=0.50},
    {id:'nomad_jury_rig',name:'Jury-Rig Trigger',rarity:'rare',desc:'Switching weapons primes the next weapon attack for +35% damage.',apply:p=>p._nomadJuryRig=0.35},
    {id:'nomad_salvage_rights',name:'Salvage Rights',rarity:'epic',desc:'+25% chance to find bonus salvage after combat.',apply:p=>p._nomadSalvageRights=0.25},
    {id:'nomad_camp_routine',name:'Camp Routine',rarity:'epic',desc:'After every combat, restore 8% max HP and 5 Humanity.',apply:p=>p._nomadCampRoutine=true},
    {id:'nomad_family_convoy',name:'Family Convoy',rarity:'legendary',desc:'Each new normal district grants +1 Stim and +25 eddies.',apply:p=>{p._nomadFamilyConvoy=true;p.items.stims+=1;p.eddies+=25;}},
  ],
  fixer:[
    {id:'fixer_preferred_client',name:'Preferred Client',rarity:'rare',desc:'Shop prices are 15% lower.',apply:p=>p.shopDiscount=(p.shopDiscount||0)+0.15},
    {id:'fixer_brokers_eye',name:"Broker's Eye",rarity:'rare',desc:'Each shop reroll upgrades rerolled weapon quality by at least one tier.',apply:p=>p._fixerBrokersEye=true},
    {id:'fixer_clean_contract',name:'Clean Contract',rarity:'rare',desc:'Marked kills restore 15% max HP.',apply:p=>p._fixerCleanContract=0.15},
    {id:'fixer_double_dip',name:'Double Dip',rarity:'epic',desc:'Marked kills pay an additional +20 eddies.',apply:p=>p._fixerDoubleDip=20},
    {id:'fixer_network_effect',name:'Network Effect',rarity:'epic',desc:'Fixer Contact district boons are 50% stronger.',apply:p=>p._fixerNetworkEffect=0.50},
    {id:'fixer_city_retainer',name:'City on Retainer',rarity:'legendary',desc:'-20% shop prices, +1 shop reroll, and contract marks gain +15% payout.',apply:p=>{p.shopDiscount=(p.shopDiscount||0)+0.20;p._extraReroll=(p._extraReroll||0)+1;p._fixerContractBonus=(p._fixerContractBonus||0)+0.15;}},
  ],
};

function classRelicPool(P){ return CLASS_RELICS[P?.cls] || []; }
function hasClassRelic(P,id){ return !!P?.classRelics?.some(r=>r.id===id); }
function grantClassRelic(P,relic){
  if(!relic || hasClassRelic(P,relic.id)) return;
  P.classRelics.push(relic);
  if(relic.apply) relic.apply(P);
  print(`<span class="tag relic">CLASS CORE</span> ${rarityBadge(relic.rarity)} Acquired <b class="purp">${relic.name}</b> — ${relic.desc}`);
  refreshStatus();
}

// ---- fixer contact boons'''
replace_once(anchor, block, 'rarity and class relic block')

# ---------------------------------------------------------------
# Weapon rarity is actually weighted
# ---------------------------------------------------------------
replace_once(
"""const SUFFIX = [
  { n:'', crit:0 },
  { n:'of Precision', crit:0.10 },
  { n:'of the Viper', crit:0.15 },
  { n:'\"Bloodrunner\"', crit:0.20 },
  { n:'of Malorian make', crit:0.25 },
];

// ---- weapon mutations""",
"""const SUFFIX = [
  { n:'', crit:0 },
  { n:'of Precision', crit:0.10 },
  { n:'of the Viper', crit:0.15 },
  { n:'\"Bloodrunner\"', crit:0.20 },
  { n:'of Malorian make', crit:0.25 },
];
const PREFIX_WEIGHTS = [24,20,18,14,10,7,4,3];
function rollWeaponPrefix(){
  let roll=Math.random()*PREFIX_WEIGHTS.reduce((a,b)=>a+b,0);
  for(let i=0;i<PREFIX.length;i++){
    roll-=PREFIX_WEIGHTS[i];
    if(roll<=0) return PREFIX[i];
  }
  return PREFIX[PREFIX.length-1];
}

// ---- weapon mutations""",
'weapon prefix weights'
)
replace_once("const pre = forceTier!=null ? PREFIX[forceTier] : pick(PREFIX);", "const pre = forceTier!=null ? PREFIX[forceTier] : rollWeaponPrefix();", 'weighted weapon roll')
replace_once("""    humMod: pre.hum, tier, mutation
  };""", """    humMod: pre.hum, tier, rarity:weaponRarityFromTier(tier), mutation
  };""", 'weapon rarity property')

# ---------------------------------------------------------------
# Player class relic state + inventory capacity
# ---------------------------------------------------------------
replace_once("cyberware: [], relics:[],", "cyberware: [], relics:[], classRelics:[],", 'player class relic inventory')
replace_once("weapon: w, inventory:[w],", "weapon: w, inventory:[w], inventoryCap:6,", 'player inventory cap')
replace_once("function addToInventory(P, w){ P.inventory.push(w); if(P.inventory.length>6) P.inventory.shift(); }", "function addToInventory(P, w){ P.inventory.push(w); const cap=P.inventoryCap||6; if(P.inventory.length>cap) P.inventory.shift(); }", 'inventory capacity function')

# Full Conversion modifies future chrome installs
regex_once(
    r"function installCyberware\(P, cw, risky\)\{.*?\n\}",
    r'''function installCyberware(P, cw, risky){
  P.cyberware.push(cw);
  cw.apply(P);
  let humLoss = risky ? cw.hum + rnd(2,6) : cw.hum;
  if(P._fullConversion) humLoss = Math.max(1,Math.ceil(humLoss*0.5));
  P.humanity = clamp(P.humanity - humLoss, 0, P.maxHumanity);
  let extra='';
  if(P._fullConversion){ P.maxHp+=2; P.hp+=2; extra=' <span class="purp">Full Conversion: +2 max HP.</span>'; }
  print(`<span class="tag loot">CHROME</span> ${rarityBadge(cyberwareRarity(cw))} Installed <b>${cw.name}</b> (${cw.slot}) — ${cw.desc}. <span class="warn">-${humLoss} Humanity</span>.${extra}`);
  checkCyberpsychosis(P);
}''',
    'install cyberware'
)

# Standard relic grant gets rarity + preserves synergy announcement
regex_once(
    r"function grantRelic\(P, relic\)\{.*?\n\}\n\n// ================= RUN / MAP FLOW",
    r'''function grantRelic(P, relic){
  const before = new Set(getActiveRelicSynergies(P).map(s=>s.id));
  P.relics.push(relic);
  if(relic.apply) relic.apply(P);
  print(`<span class="tag relic">RELIC</span> ${rarityBadge(relicRarity(relic))} Acquired <b class="purp">${relic.name}</b> — ${relic.desc}`);
  getActiveRelicSynergies(P).filter(s=>!before.has(s.id)).forEach(s=>{
    print(`<span class="tag relic">SYNERGY</span> <b class="purp">${s.name.toUpperCase()} ONLINE</b> — ${s.desc}`);
  });
}

// ================= RUN / MAP FLOW''',
    'grant relic rarity'
)

# ---------------------------------------------------------------
# Guaranteed Class Core choices: entering Pacifica and Corpo Plaza
# ---------------------------------------------------------------
replace_once(
"""            kills:0, eliteKills:0, actBuffs:[], actEddiesMult:1, actContactDone:false,
            starting:true, hardMode: !!hardMode };""",
"""            kills:0, eliteKills:0, actBuffs:[], actEddiesMult:1, actContactDone:false,
            starting:true, classRelicsGranted:0, hardMode: !!hardMode };""",
'class relic run counter'
)

class_choice = r'''function runClassRelicChoice(stage){
  const run=S.run, P=run.player;
  const avail=classRelicPool(P).filter(r=>!hasClassRelic(P,r.id));
  if(!avail.length){ run.classRelicsGranted=Math.max(run.classRelicsGranted||0,stage); return nextNode(); }

  let choices=[];
  if(stage===1){
    const firstPool=avail.filter(r=>r.rarity!=='legendary');
    choices=weightedSampleByRarity(firstPool.length?firstPool:avail,3,r=>r.rarity);
  } else {
    const premium=avail.filter(r=>r.rarity==='epic' || r.rarity==='legendary');
    const premiumPick=weightedPickByRarity(premium,r=>r.rarity);
    const restPool=avail.filter(r=>r!==premiumPick);
    choices=[...(premiumPick?[premiumPick]:[]), ...weightedSampleByRarity(restPool,2,r=>r.rarity)];
  }

  print(`<span class="tag relic">CLASS CORE ${stage}/2</span> <b class="accent">${P.className.toUpperCase()} SPECIALIZATION</b>`, 'sys');
  print(`<span class="flavor">A class-locked relic synchronizes with your combat profile. Choose one. These are run-defining and never enter the normal relic pool.</span>`);

  actions(choices.map(r=>({
    label:r.name,
    sub:`${rarityBadge(r.rarity)} ${r.desc}`,
    cls:r.rarity==='legendary'?'gold':'purp',
    fn:()=>{
      grantClassRelic(P,r);
      run.classRelicsGranted=Math.max(run.classRelicsGranted||0,stage);
      divider();
      nextNode();
    }
  })));
}

'''
replace_once("function nextNode(){", class_choice + "function nextNode(){", 'class relic choice function')
replace_once("function nextNode(){\n  const run = S.run;\n  let act = ACTS[run.act];", "function nextNode(){\n  const run = S.run;\n  const P = run.player;\n  let enteredNewAct = false;\n  let act = ACTS[run.act];", 'nextNode transition state')
replace_once("    run.act++;\n    if(run.act >= ACTS.length)", "    run.act++;\n    enteredNewAct = true;\n    if(run.act >= ACTS.length)", 'entered act marker')
replace_once(
"""  if(act.midboss) return midBossEncounter();
  if(act.boss) return bossEncounter();""",
"""  if(enteredNewAct && P._nomadFamilyConvoy && !act.midboss && !act.boss){
    P.items.stims += 1;
    P.eddies += 25;
    print('<span class="tag relic">FAMILY CONVOY</span> <span class="good">+1 Stim, +25 eddies.</span> Your people were here first.');
    refreshStatus();
  }

  if(run.act===1 && (run.classRelicsGranted||0)<1) return runClassRelicChoice(1);
  if(run.act===3 && (run.classRelicsGranted||0)<2) return runClassRelicChoice(2);

  if(act.midboss) return midBossEncounter();
  if(act.boss) return bossEncounter();""",
'class relic progression gates'
)

# Standard relic offers use rarity weighting + labels
replace_once(
"""  const choices = [...relicPool()]
    .filter(r=>!hasRelic(P,r.id))
    .sort(()=>Math.random()-0.5)
    .slice(0,3);""",
"""  const choices = weightedSampleByRarity(
    relicPool().filter(r=>!hasRelic(P,r.id)), 3, relicRarity
  );""",
'start relic rarity weighting'
)
replace_once("sub:r.desc,\n    cls:'purp',", "sub:`${rarityBadge(relicRarity(r))} ${r.desc}`,\n    cls:'purp',", 'start relic labels')
replace_once("const opts = avail.sort(()=>Math.random()-0.5).slice(0,3);", "const opts = weightedSampleByRarity(avail,3,relicRarity);", 'cache relic weighting')
replace_once("const list = opts.map(r=>({ label:r.name, sub:r.desc, cls:'purp'", "const list = opts.map(r=>({ label:r.name, sub:`${rarityBadge(relicRarity(r))} ${r.desc}`, cls:'purp'", 'cache relic labels')
replace_once("const opts3 = avail.sort(()=>Math.random()-0.5).slice(0,3);", "const opts3 = weightedSampleByRarity(avail,3,relicRarity);", 'elite relic weighting')
replace_once("const list = opts3.map(r=>({ label:r.name, sub:r.desc, cls:'purp'", "const list = opts3.map(r=>({ label:r.name, sub:`${rarityBadge(relicRarity(r))} ${r.desc}`, cls:'purp'", 'elite relic labels')

# ---------------------------------------------------------------
# Character Sheet rarity + class cores
# ---------------------------------------------------------------
replace_once(
"""  const chromeHtml = P.cyberware.length
    ? P.cyberware.map(c=>`<div class=\"sheetItem\"><b>${c.name}</b> <span class=\"flavor\">// ${c.slot}</span><small>${c.desc} · Humanity cost ${c.hum}</small></div>`).join('')""",
"""  const chromeHtml = P.cyberware.length
    ? P.cyberware.map(c=>`<div class=\"sheetItem\">${rarityBadge(cyberwareRarity(c))} <b>${c.name}</b> <span class=\"flavor\">// ${c.slot}</span><small>${c.desc} · Humanity cost ${c.hum}</small></div>`).join('')""",
'chrome sheet rarity'
)
replace_once(
"""  const relicHtml = P.relics.length
    ? P.relics.map(r=>`<div class=\"sheetItem\"><b>${r.name}</b><small>${r.desc}</small></div>`).join('')
    : '<div class=\"sheetEmpty\">No relics acquired.</div>';""",
"""  const relicHtml = P.relics.length
    ? P.relics.map(r=>`<div class=\"sheetItem\">${rarityBadge(relicRarity(r))} <b>${r.name}</b><small>${r.desc}</small></div>`).join('')
    : '<div class=\"sheetEmpty\">No relics acquired.</div>';
  const classRelicHtml = P.classRelics?.length
    ? P.classRelics.map(r=>`<div class=\"sheetItem\">${rarityBadge(r.rarity)} <b class=\"purp\">${r.name}</b><small>${r.desc}</small></div>`).join('')
    : '<div class=\"sheetEmpty\">No Class Cores acquired yet.</div>';""",
'relic sheet rarity and class relics'
)
replace_once("<b>${i+1}. ${w.name}</b> ${equipped?", "${rarityBadge(w.rarity||weaponRarityFromTier(w.tier||0))} <b>${i+1}. ${w.name}</b> ${equipped?", 'weapon sheet rarity')
replace_once(
"""    <section class=\"sheetSection\">
      <h3>RELICS // ${P.relics.length}</h3>
      ${relicHtml}
    </section>

    <section class=\"sheetSection\">
      <h3>RELIC SYNERGIES""",
"""    <section class=\"sheetSection\">
      <h3>RELICS // ${P.relics.length}</h3>
      ${relicHtml}
    </section>

    <section class=\"sheetSection\">
      <h3>CLASS CORES // ${P.classRelics?.length||0}/2</h3>
      ${classRelicHtml}
    </section>

    <section class=\"sheetSection\">
      <h3>RELIC SYNERGIES""",
'class relic sheet section'
)
replace_once("<h3>WEAPON INVENTORY // ${P.inventory.length}/6</h3>", "<h3>WEAPON INVENTORY // ${P.inventory.length}/${P.inventoryCap||6}</h3>", 'inventory cap sheet')

# ---------------------------------------------------------------
# Combat hooks for class relics
# ---------------------------------------------------------------
# Switch primes Nomad Jury-Rig
replace_once(
"fn:()=>{ P.weapon=w; print(`Switched to <b>${w.name}</b>.`); combatMenu(); }",
"fn:()=>{ P.weapon=w; if(P._nomadJuryRig){P._juryRigPrimed=true;} print(`Switched to <b>${w.name}</b>.${P._nomadJuryRig?' <span class=\"purp\">Jury-Rig primed.</span>':''}`); combatMenu(); }",
'nomad jury rig switch'
)
# Guard primes Solo and enables Samurai riposte through existing guard data
replace_once(
"""  c.guardReduction = guardPct/100;

  print(""",
"""  c.guardReduction = guardPct/100;
  if(P._soloCoverDiscipline) P._guardAttackPrimed = true;

  print(""",
'solo guard prime'
)

# Rocker special modifications
replace_once("c.rallyTurns = 3 + (P._rockerEncore||0);", "c.rallyTurns = 3 + (P._rockerEncore||0) + (P._rockerFeedbackLoop||0);", 'rocker rally class relic')
replace_once("const suppress = 2 + (P._rockerEncore||0);", "const suppress = 2 + (P._rockerEncore||0) + (P._rockerFeedbackLoop||0);", 'rocker feedback class relic')

# Normal attack setup: counters/hits
replace_once(
"""  let hits = (P.weapon.hits || 1) + (P.weapon.mutation && P.weapon.mutation.id==='fragment' ? 1 : 0);
  let totalDmg = 0, anyCrit=false, effectsHtml='';""",
"""  let hits = (P.weapon.hits || 1) + (P.weapon.mutation && P.weapon.mutation.id==='fragment' ? 1 : 0);
  if(!useAbility && P._chromeHydraulic && P.weapon.baseId==='gorilla_arms') hits += 1;
  let totalDmg = 0, anyCrit=false, effectsHtml='';
  const firstWeaponAttack = !useAbility && !c._classFirstWeaponUsed;
  if(!useAbility){
    c._classFirstWeaponUsed = true;
    P._weaponAttackCount = (P._weaponAttackCount||0)+1;
  }
  const blackhandProc = !useAbility && P._blackhandProtocol && P._weaponAttackCount%3===0;""",
'class relic attack setup'
)

# Add generic post-ability class relic effects just before refreshStatus
replace_once(
"""  }

  refreshStatus();
  if(c.enemy.hp <= 0) return winCombat();
  enemyTurn();
}""",
"""  }

  if(useAbility && totalDmg>0 && P._netIcebreaker){
    c.enemy.def=Math.max(0,c.enemy.def-1);
    print('<span class=\"tag relic\">ICEBREAKER</span> Enemy armor -1.');
  }
  if(useAbility && totalDmg>0 && P._netRecursivePing){
    c.enemyBleed=(c.enemyBleed||0)+P._netRecursivePing;
    print(`<span class=\"tag relic\">RECURSIVE PING</span> BLEED ${P._netRecursivePing}.`);
  }
  if(useAbility && totalDmg>0 && P._netBlackwallTap){
    const bonus=Math.max(1,Math.round(totalDmg*0.40));
    c.enemy.hp-=bonus;
    P.humanity=clamp(P.humanity-4,0,P.maxHumanity);
    print(`<span class=\"tag relic\">BLACKWALL TAP</span> <b>${bonus}</b> bonus true damage. <span class=\"warn\">-4 Humanity.</span>`);
    checkCyberpsychosis(P);
  }
  if(useAbility && c.enemyStunned && P._netBufferOverflow && P.ability.cdLeft>0){
    P.ability.cdLeft=Math.max(0,P.ability.cdLeft-P._netBufferOverflow);
    print('<span class=\"tag relic\">BUFFER OVERFLOW</span> Special cooldown -1.');
  }
  if(useAbility && P._netZeroDay && !c._zeroDayUsed){
    c._zeroDayUsed=true;
    P.ability.cdLeft=0;
    print('<span class=\"tag relic\">ZERO DAY</span> First special refreshed immediately.');
  }
  if(useAbility && P._rockerRiotShield && c.enemy.hp>0){
    c.guarding=true;
    c.guardReduction=Math.max(c.guardReduction||0,P._rockerRiotShield);
    print('<span class=\"tag relic\">RIOT SHIELD</span> 40% Guard online for the counterattack.');
  }

  refreshStatus();
  if(c.enemy.hp <= 0) return winCombat();
  enemyTurn();
}""",
'post ability class relic hooks'
)

# Enhance normal attack loop. Replace base calculation and crit/armor block.
replace_once(
"""      let base = rnd(...P.weapon.dmg) + P.dmgBonus + (P.weapon.tech?P.tech:0);
      if(P._ballisticMastery && P.weapon.tag==='ballistic') base += P._ballisticMastery;
      if(affinity){""",
"""      let base = rnd(...P.weapon.dmg) + P.dmgBonus + (P.weapon.tech?P.tech:0);
      if(P._ballisticMastery && P.weapon.tag==='ballistic') base += P._ballisticMastery;
      if(P._chromeMetalDividend) base += P.cyberware.length;
      if(P._rockerStagePresence) base += Math.floor((P.cool||0)*0.25);
      if(P._rockerFullAutoChorus && P.weapon.baseId==='smg') base += i;
      if(affinity){""",
'normal attack class flat bonuses'
)
replace_once(
"""      if(hasRelic(P,'adrenal_plug') && P.hp < P.maxHp*0.3) base += 3;
      let critChance = P.weapon.crit + P.critBonus + (affinity?.critBonus||0) + (berserkMode?0.25:0);
      let crit = Math.random() < critChance;""",
"""      if(hasRelic(P,'adrenal_plug') && P.hp < P.maxHp*0.3) base += 3;
      let classMult=1;
      if(firstWeaponAttack && P._soloDeadCenter) classMult += P._soloDeadCenter;
      if(firstWeaponAttack && P._samuraiNoSecondStrike && P.weapon.baseId==='katana') classMult += 1.0;
      if(P._executeMult && c.enemy.hp<c.enemy.maxHp*0.40) classMult += P._executeMult;
      if(P._chromeLimitersOff && P.humanity<=P.maxHumanity*0.25) classMult += P._chromeLimitersOff;
      if(P._juryRigPrimed) classMult += P._nomadJuryRig||0;
      if(blackhandProc) classMult += 0.50;
      base=Math.round(base*classMult);
      let critChance = P.weapon.crit + P.critBonus + (affinity?.critBonus||0) + (berserkMode?0.25:0);
      let crit = Math.random() < critChance;
      if((firstWeaponAttack && P._samuraiPerfectDraw && P.weapon.baseId==='katana') || P._stillWaterPrimed || blackhandProc){ crit=true; }""",
'normal attack multipliers and guaranteed crits'
)
replace_once(
"""      const armorThisHit = openingExecution ? Math.max(0,armorPerHit-2) : armorPerHit;
      d = Math.max(1, d - armorThisHit);""",
"""      let armorThisHit = openingExecution ? Math.max(0,armorPerHit-2) : armorPerHit;
      if(P._affinityArmorPierce && affinity && P.weapon.baseId==='pistol') armorThisHit=Math.max(0,armorThisHit-P._affinityArmorPierce);
      d = Math.max(1, d - armorThisHit);""",
'solo armor pierce'
)
replace_once(
"""    print(`<span class=\"tag${anyCrit?' crit':''}\">HIT</span> ${P.weapon.name} deals <b>${totalDmg}</b> damage${hits>1?` across ${hits} shots`:''}.${affinity?' <span class=\"accent\">CLASS AFFINITY</span>':''}${anyCrit?' <span class=\"warn\">CRITICAL!</span>':''}${berserkMode?' <span class=\"bad\">(chrome-fueled rage)</span>':''}${effectsHtml}`);
  }""",
"""    if(P._netIcebreaker && P.weapon.tech){
      c.enemy.def=Math.max(0,c.enemy.def-1);
      effectsHtml += ' <span class=\"purp\">ICEBREAKER: armor -1.</span>';
    }
    if(P._juryRigPrimed) P._juryRigPrimed=false;
    if(P._stillWaterPrimed) P._stillWaterPrimed=false;
    print(`<span class=\"tag${anyCrit?' crit':''}\">HIT</span> ${P.weapon.name} deals <b>${totalDmg}</b> damage${hits>1?` across ${hits} shots`:''}.${affinity?' <span class=\"accent\">CLASS AFFINITY</span>':''}${anyCrit?' <span class=\"warn\">CRITICAL!</span>':''}${berserkMode?' <span class=\"bad\">(chrome-fueled rage)</span>':''}${blackhandProc?' <span class=\"purp\">BLACKHAND PROTOCOL</span>':''}${effectsHtml}`);
  }""",
'normal attack cleanup and output'
)

# applyHitEffects gets Netrunner/Samurai crit mechanics
replace_once(
"""  if(isCrit && hasRelic(P,'bloodwire')){
    const heal = hasRelicSynergy(P,'redline_loop') ? 3 : 2;""",
"""  if(isCrit && P._netGhostRam && P.weapon.tech && P.ability.cdLeft>0){
    P.ability.cdLeft=Math.max(0,P.ability.cdLeft-P._netGhostRam);
    extra+=' <span class=\"purp\">Ghost RAM: cooldown -1.</span>';
  }
  if(isCrit && P.weapon.baseId==='katana' && P._samuraiCrimsonEdge){
    const bleed=Math.max(1,Math.round(dmgDealt*0.25));
    c.enemyBleed=(c.enemyBleed||0)+bleed;
    extra+=` <span class=\"purp\">Crimson Edge: BLEED ${bleed}.</span>`;
  }
  if(isCrit && P.weapon.baseId==='katana' && P._samuraiFlowingSteel){
    const follow=Math.max(1,Math.round(dmgDealt*P._samuraiFlowingSteel));
    c.enemy.hp-=follow;
    extra+=` <span class=\"purp\">Flowing Steel: +${follow} follow-up.</span>`;
  }
  if(isCrit && hasRelic(P,'bloodwire')){
    const heal = hasRelicSynergy(P,'redline_loop') ? 3 : 2;""",
'class crit mechanics'
)

# Enemy turn: trauma plate, road armor, still water, riposte, reflected kill
replace_once(
"""    if(c.enemy.berserk && c.enemy.hp < c.enemy.maxHp*0.4){
      d = Math.round(d*1.5);
    }

    let avoided = false;""",
"""    if(c.enemy.berserk && c.enemy.hp < c.enemy.maxHp*0.4){
      d = Math.round(d*1.5);
    }
    if(P._chromeTraumaPlate && P.hp<P.maxHp*0.50 && d>0){
      d=Math.ceil(d*(1-P._chromeTraumaPlate));
      print('<span class=\"tag relic\">TRAUMA PLATE</span> Incoming damage reduced by 20%.');
    }

    let avoided = false;""",
'trauma plate'
)
replace_once(
"""        d = 0;
        avoided = true;
        if(hasRelicSynergy(P,'ghost_protocol')""",
"""        d = 0;
        avoided = true;
        if(P._samuraiStillWater){
          P._stillWaterPrimed=true;
          print('<span class=\"tag relic\">STILL WATER</span> Next weapon hit is a guaranteed critical.');
        }
        if(hasRelicSynergy(P,'ghost_protocol')""",
'still water evade'
)
replace_once(
"""    if(c.guarding && d > 0){
      const original = Math.max(0,d);""",
"""    if(!avoided && d>0 && P._nomadRoadArmor && !c._roadArmorUsed){
      const original=d;
      d=Math.ceil(d*(1-P._nomadRoadArmor));
      c._roadArmorUsed=true;
      print(`<span class=\"tag relic\">ROAD ARMOR</span> First hit ${original} → ${d}.`);
    }

    if(c.guarding && d > 0){
      const original = Math.max(0,d);""",
'nomad road armor'
)
replace_once(
"""      d = Math.ceil(original * (1-reduction));

      print(
        `<span class=\"tag hack\">GUARD</span> You absorb the hit. ` +
        `<span class=\"good\">${original} → ${d} damage.</span>`
      );""",
"""      d = Math.ceil(original * (1-reduction));
      let riposte='';
      if(P._samuraiRiposte){
        const reflected=Math.max(1,Math.round((original-d)*P._samuraiRiposte));
        c.enemy.hp-=reflected;
        riposte=` <span class=\"purp\">Riposte: ${reflected} reflected.</span>`;
      }

      print(
        `<span class=\"tag hack\">GUARD</span> You absorb the hit. ` +
        `<span class=\"good\">${original} → ${d} damage.</span>${riposte}`
      );""",
'samurai riposte'
)
replace_once(
"""  refreshStatus();
  if(checkDeath()) return;
  combatMenu();
}""",
"""  refreshStatus();
  if(checkDeath()) return;
  if(c.enemy.hp<=0) return winCombat();
  combatMenu();
}""",
'reflected damage kill resolution'
)

# Rocker Never Fade triggers before Second Wind
replace_once(
"""  if(P.hp<=0){
    if(hasRelic(P,'second_wind') && !P.usedSecondWind){""",
"""  if(P.hp<=0){
    if(P._rockerNeverFade && !P._rockerNeverFadeUsed){
      P._rockerNeverFadeUsed=true;
      P.hp=Math.max(1,Math.round(P.maxHp*0.35));
      P.ability.cdLeft=0;
      print(`<span class=\"tag relic\">NEVER FADE AWAY</span> <span class=\"purp\">The signal comes back screaming. ${P.hp} HP and special READY.</span>`);
      refreshStatus();
      return false;
    }
    if(hasRelic(P,'second_wind') && !P.usedSecondWind){""",
'rocker legendary revive'
)

# ---------------------------------------------------------------
# Post-kill class mechanics + Nomad loot bonus
# ---------------------------------------------------------------
replace_once(
"""  P.eddies += eddies;
  print(`<span class=\"tag\">DOWN</span> <b>${c.enemy.name}</b> flatlines. <span class=\"good\">+${eddies} eddies.</span>`);

  if(c.enemy.elite){""",
"""  P.eddies += eddies;
  print(`<span class=\"tag\">DOWN</span> <b>${c.enemy.name}</b> flatlines. <span class=\"good\">+${eddies} eddies.</span>`);

  if(P._killCooldown && P.ability.cdLeft>0){
    const before=P.ability.cdLeft;
    P.ability.cdLeft=Math.max(0,P.ability.cdLeft-P._killCooldown);
    print(`<span class=\"tag relic\">TEMPO</span> Special cooldown ${before} → ${P.ability.cdLeft}.`);
  }
  if(P._chromeBloodMachine && P.cyberware.length){
    const pct=Math.min(0.20,P.cyberware.length*0.04);
    const heal=Math.max(1,Math.round(P.maxHp*pct));
    P.hp=clamp(P.hp+heal,0,P.maxHp);
    print(`<span class=\"tag relic\">BLOOD MACHINE</span> <span class=\"good\">+${heal} HP.</span>`);
  }
  if(P._fixerCleanContract && (c.contractBonus||0)>0){
    const heal=Math.max(1,Math.round(P.maxHp*P._fixerCleanContract));
    P.hp=clamp(P.hp+heal,0,P.maxHp);
    print(`<span class=\"tag relic\">CLEAN CONTRACT</span> <span class=\"good\">+${heal} HP.</span>`);
  }
  if(P._fixerDoubleDip && (c.contractBonus||0)>0){
    P.eddies+=P._fixerDoubleDip;
    print(`<span class=\"tag relic\">DOUBLE DIP</span> <span class=\"good\">+${P._fixerDoubleDip} eddies.</span>`);
  }
  if(P._nomadCampRoutine){
    const heal=Math.max(1,Math.round(P.maxHp*0.08));
    const hum=Math.min(5,P.maxHumanity-P.humanity);
    P.hp=clamp(P.hp+heal,0,P.maxHp);
    P.humanity=clamp(P.humanity+5,0,P.maxHumanity);
    print(`<span class=\"tag relic\">CAMP ROUTINE</span> <span class=\"good\">+${heal} HP, +${hum} Humanity.</span>`);
  }

  if(c.enemy.elite){""",
'post kill class relics'
)
replace_once(
"""  const lootChance = 0.35 + (hasRelic(P,'scavenger_eye') ? 0.15 : 0) + (scavengerContract ? 0.10 : 0);""",
"""  const lootChance = 0.35 + (hasRelic(P,'scavenger_eye') ? 0.15 : 0) + (scavengerContract ? 0.10 : 0) + (P._nomadSalvageRights||0);""",
'nomad salvage rights'
)

# ---------------------------------------------------------------
# Fixer class relic economy
# ---------------------------------------------------------------
replace_once(
"""    label: b.label, sub: b.sub, cls:'purp', fn:()=>{
      if(b.stat==='eddiesMult') S.run.actEddiesMult = 1+b.amount;
      else P[b.stat] += b.amount;
      S.run.actBuffs.push(b);
      print(`Favor called in: <b class=\"purp\">${b.label}</b>.`);""",
"""    label: b.label, sub:P._fixerNetworkEffect?`${b.sub} · NETWORK +50%`:b.sub, cls:'purp', fn:()=>{
      let amount=b.amount;
      if(P._fixerNetworkEffect){
        amount*=1.5;
        if(['dmgBonus','def','tech'].includes(b.stat)) amount=Math.round(amount);
      }
      const applied={...b,amount};
      if(applied.stat==='eddiesMult') S.run.actEddiesMult = 1+applied.amount;
      else P[applied.stat] += applied.amount;
      S.run.actBuffs.push(applied);
      print(`Favor called in: <b class=\"purp\">${b.label}</b>${P._fixerNetworkEffect?' <span class=\"purp\">[NETWORK EFFECT]</span>':''}.`);""",
'fixer network effect'
)
replace_once(
"""            if(s.kind==='weapon') stock[i]={kind:'weapon', item:rollWeapon(pick(Object.keys(WEAPON_BASE))), price:Math.round(rnd(35,70)*disc)};""",
"""            if(s.kind==='weapon'){
              const forced=P._fixerBrokersEye ? Math.min(7,Math.max(1,(s.item.tier||0)+1)) : undefined;
              stock[i]={kind:'weapon', item:rollWeapon(pick(Object.keys(WEAPON_BASE)),forced), price:Math.round(rnd(35,70)*disc)};
            }""",
'fixer broker reroll'
)

# Shop rarity labels
replace_once(
"""if(s.kind==='weapon'){ label=`Buy: ${s.item.name}`; sub=`${s.item.dmg[0]}-${s.item.dmg[1]} dmg, crit ${Math.round(s.item.crit*100)}% — ${s.price}e`; }
      else if(s.kind==='cyber'){ label=`Install: ${s.item.name}`; sub=`${s.item.desc} (${s.item.slot}) — ${s.price}e, -${s.item.hum} Humanity`; }""",
"""if(s.kind==='weapon'){ label=`Buy: ${s.item.name}`; sub=`${rarityBadge(s.item.rarity||weaponRarityFromTier(s.item.tier||0))} ${s.item.dmg[0]}-${s.item.dmg[1]} dmg, crit ${Math.round(s.item.crit*100)}% — ${s.price}e`; }
      else if(s.kind==='cyber'){ label=`Install: ${s.item.name}`; sub=`${rarityBadge(cyberwareRarity(s.item))} ${s.item.desc} (${s.item.slot}) — ${s.price}e, -${s.item.hum} Humanity`; }""",
'shop rarity labels'
)

# ---------------------------------------------------------------
# Guide documentation
# ---------------------------------------------------------------
replace_once(
"""    <section class=\"sheetSection\">
      <h3>RELICS, CHROME & BOONS</h3>""",
"""    <section class=\"sheetSection\">
      <h3>RARITY</h3>
      <div class=\"guideRow\">${rarityBadge('common')} Grey — baseline/common gear.</div>
      <div class=\"guideRow\">${rarityBadge('uncommon')} Green — stronger, still regularly seen.</div>
      <div class=\"guideRow\">${rarityBadge('rare')} Blue — specialized or high-value.</div>
      <div class=\"guideRow\">${rarityBadge('epic')} Purple — powerful build-shaping gear.</div>
      <div class=\"guideRow\">${rarityBadge('legendary')} Yellow — run-defining and scarce.</div>
      <div class=\"guideTip\">Weapon quality and standard relic offers use rarity-weighted rolls: higher tiers appear less often. Forced rewards can override normal rarity odds.</div>
    </section>

    <section class=\"sheetSection\">
      <h3>CLASS CORES</h3>
      <div class=\"guideRow\"><b>Separate pool</b> — Every class has 6 exclusive Class Core relics: 3 Rare, 2 Epic, and 1 Legendary. They never appear in the normal relic pool.</div>
      <div class=\"guideRow\"><b>Guaranteed Core I</b> — Choose 1 of 3 when entering Pacifica after clearing Watson.</div>
      <div class=\"guideRow\"><b>Guaranteed Core II</b> — Choose a second Core after the NetWatch Warden when entering Corpo Plaza. At least one offered choice is Epic or Legendary.</div>
      <div class=\"guideRow\"><b>Purpose</b> — Class Cores alter mechanics: extra hits, cooldown loops, revives, ripostes, stronger contracts, expanded inventory, chrome scaling, and other class-defining effects.</div>
      <div class=\"guideTip\">A completed run is balanced around obtaining exactly two Class Cores. Dying before reaching the next Core gate ends the run normally.</div>
    </section>

    <section class=\"sheetSection\">
      <h3>RELICS, CHROME & BOONS</h3>""",
'guide rarity and class cores'
)
replace_once("You can carry up to 6 weapons.", "You can carry 6 weapons by default; Nomad's Pack Rat Class Core raises the limit to 8.", 'guide inventory cap')

path.write_text(text)
print('Applied class cores + rarity system')
