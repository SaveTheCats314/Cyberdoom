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
    new_text, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if count != 1:
        raise SystemExit(f'Patch target not found or ambiguous: {label} ({count})')
    text = new_text


# ------------------------------------------------------------------
# Relic synergy definitions
# ------------------------------------------------------------------
replace_once(
"""function relicPool(){ return ALL_RELICS.filter(r=>META.unlocks.relics.includes(r.id)); }
function hasRelic(P,id){ return P.relics.some(r=>r.id===id); }

// ---- fixer contact boons""",
"""function relicPool(){ return ALL_RELICS.filter(r=>META.unlocks.relics.includes(r.id)); }
function hasRelic(P,id){ return P.relics.some(r=>r.id===id); }

const RELIC_SYNERGIES = [
  { id:'redline_loop', name:'Redline Loop', relics:['bloodwire','deadeye_lens'], desc:'Critical hits restore 3 HP instead of 2.' },
  { id:'ghost_protocol', name:'Ghost Protocol', relics:['ghost_runner','combat_predictor'], desc:'A successful Evade reduces your special ability cooldown by 1 extra turn.' },
  { id:'fortress_stack', name:'Fortress Stack', relics:['guardian_daemon','titanium_spine'], desc:'Guard reduces the next incoming hit by 75%.' },
  { id:'trauma_rig', name:'Trauma Rig', relics:['medtech_patch','chrome_heart'], desc:'Combat stims also restore 5 Humanity.' },
  { id:'last_breath', name:'Last Breath', relics:['second_wind','adrenal_plug'], desc:'Second Wind revives you at 25% max HP instead of 1 HP.' },
  { id:'scavenger_contract', name:'Scavenger Contract', relics:['scavenger_eye','loyalty_chip'], desc:'+10% bonus loot chance; successful salvage also pays +10 eddies.' },
  { id:'execution_protocol', name:'Execution Protocol', relics:[\"widows_kiss\",'deadeye_lens'], desc:\"Widow's Kiss opening critical ignores 2 additional enemy armor.\" },
];

function hasRelicSynergy(P,id){
  const synergy = RELIC_SYNERGIES.find(s=>s.id===id);
  return !!(synergy && synergy.relics.every(r=>hasRelic(P,r)));
}

function getActiveRelicSynergies(P){
  return RELIC_SYNERGIES.filter(s=>s.relics.every(r=>hasRelic(P,r)));
}

// ---- fixer contact boons""",
'relic synergy definitions'
)


# ------------------------------------------------------------------
# Replace simple event pool with richer conditional encounters
# ------------------------------------------------------------------
events_block = r'''function uninstalledCyberware(P){
  return cyberwarePool().filter(c=>!P.cyberware.includes(c));
}

function unownedRelics(P){
  return relicPool().filter(r=>!hasRelic(P,r.id));
}

const EVENTS = [
  {
    id:'backalley_ripper',
    text:'A ripperdoc waves you into a back-alley clinic. "Cheap chrome, no questions." The tools are clean. The operating chair is not.',
    opts:[
      {
        label:'Take the free install',
        sub:'Free chrome, but the Humanity loss is unpredictable',
        disabled:P=>!uninstalledCyberware(P).length,
        fn:P=>{ const cw=pick(uninstalledCyberware(P)); installCyberware(P,cw,true); }
      },
      {
        label:'Calibrate the rig yourself',
        sub:'TECH 6 — free chrome without the extra Humanity risk',
        disabled:P=>P.tech<6 || !uninstalledCyberware(P).length,
        cls:'gold',
        fn:P=>{ const cw=pick(uninstalledCyberware(P)); installCyberware(P,cw,false); print('<span class="accent">Your calibration keeps the install inside spec.</span>'); }
      },
      {label:'Walk away', fn:()=>print('You keep walking. Some bargains cost too much.', 'flavor')}
    ]
  },
  {
    id:'braindance_kill',
    text:"A braindance parlor offers you somebody else's perfect kill. The recording is illegal, surgical, and disturbingly beautiful.",
    opts:[
      {
        label:'Jack in', sub:'+2 Cool, -4 Humanity',
        fn:P=>{ P.cool+=2; P.humanity=clamp(P.humanity-4,0,P.maxHumanity); print('<span class="good">+2 Cool.</span> <span class="warn">-4 Humanity.</span> Your hands remember a murder you never committed.'); }
      },
      {
        label:'Strip only the combat frame', sub:'COOL 7 — +5% crit, -2 Humanity',
        disabled:P=>P.cool<7,
        cls:'gold',
        fn:P=>{ P.critBonus+=0.05; P.humanity=clamp(P.humanity-2,0,P.maxHumanity); print('<span class="good">+5% crit.</span> <span class="warn">-2 Humanity.</span> You keep the timing and dump the memory.'); }
      },
      {label:'Skip it', fn:()=>print('You leave somebody else\'s memories on the shelf.', 'flavor')}
    ]
  },
  {
    id:'hot_shard',
    text:'A fixer pings you with a hot Arasaka data shard. No strings mentioned, which means there are definitely strings.',
    opts:[
      {
        label:'Take the shard', sub:'Random reward — or a tracer',
        fn:(P,run)=>{
          const r=rnd(1,3);
          if(r===1){ const e=rnd(40,90); P.eddies+=e; print(`<span class="good">+${e} eddies.</span> The buyer pays immediately.`); }
          else if(r===2){ const w=rollWeapon(pick(Object.keys(WEAPON_BASE))); addToInventory(P,w); print(`Encrypted blueprints print a <b>${w.name}</b>.`); }
          else { run.heat=(run.heat||0)+1; print('<span class="bad">Tracer detected. Heat +1.</span>'); }
        }
      },
      {
        label:'Scrub the tracer first', sub:'TECH 6 — +55 eddies and remove 1 Heat',
        disabled:P=>P.tech<6,
        cls:'gold',
        fn:(P,run)=>{ P.eddies+=55; run.heat=Math.max(0,(run.heat||0)-1); print('<span class="good">+55 eddies.</span> <span class="accent">Heat -1.</span> The shard leaves your hands clean.'); }
      },
      {
        label:'Call a buyer you trust', sub:'FIXER — +70 eddies, no tracer risk',
        show:P=>P.cls==='fixer',
        cls:'purp',
        fn:P=>{ P.eddies+=70; print('<span class="good">+70 eddies.</span> Your network makes the problem disappear.'); }
      },
      {label:'Ghost the ping', fn:()=>print('You let the signal die unanswered.', 'flavor')}
    ]
  },
  {
    id:'nomad_fire',
    text:'An old nomad crew has a fire going beneath an overpass. Food, tools, and one empty chair. Nobody asks your name.',
    opts:[
      {
        label:'Rest with them', sub:'Restore 30% max HP',
        fn:P=>{ const heal=Math.round(P.maxHp*0.30); P.hp=clamp(P.hp+heal,0,P.maxHp); print(`<span class="good">+${heal} HP.</span>`); }
      },
      {
        label:'Stay for the stories', sub:'+8 Humanity',
        fn:P=>{ const gain=Math.min(8,P.maxHumanity-P.humanity); P.humanity=clamp(P.humanity+8,0,P.maxHumanity); print(`<span class="good">+${gain} Humanity.</span> For a few minutes, Night City feels far away.`); }
      },
      {
        label:'Run with family', sub:'NOMAD — restore 25% HP and +8 Humanity',
        show:P=>P.cls==='nomad',
        cls:'purp',
        fn:P=>{ const heal=Math.round(P.maxHp*0.25); P.hp=clamp(P.hp+heal,0,P.maxHp); P.humanity=clamp(P.humanity+8,0,P.maxHumanity); print(`<span class="good">+${heal} HP, +8 Humanity.</span> Family recognizes family.`); }
      },
      {label:'Keep moving', fn:()=>print('You nod once and disappear back into traffic.', 'flavor')}
    ]
  },
  {
    id:'militech_vendor',
    text:'A street vendor is selling "guaranteed authentic" Militech surplus out of a van with three different plates.',
    opts:[
      {
        label:'Buy a weapon', sub:'30 eddies',
        disabled:P=>P.eddies<30,
        fn:P=>{ P.eddies-=30; const w=rollWeapon(pick(Object.keys(WEAPON_BASE)),rnd(2,4)); addToInventory(P,w); print(`You buy a <b>${w.name}</b>.`); }
      },
      {
        label:'Talk him down', sub:'COOL 7 — weapon for 20 eddies',
        disabled:P=>P.cool<7 || P.eddies<20,
        cls:'gold',
        fn:P=>{ P.eddies-=20; const w=rollWeapon(pick(Object.keys(WEAPON_BASE)),rnd(2,4)); addToInventory(P,w); print(`<span class="good">Saved 10 eddies.</span> You walk with a <b>${w.name}</b>.`); }
      },
      {label:'Not interested', fn:()=>print('You leave the van and its suspicious inventory behind.', 'flavor')}
    ]
  },
  {
    id:'trauma_wreck',
    text:'A Trauma Team AV sits broken across two lanes. The crew is gone. The medical lockers are still sealed and broadcasting ownership tags.',
    opts:[
      {
        label:'Rip open the lockers', sub:'+2 stims, +1 Heat',
        fn:(P,run)=>{ P.items.stims+=2; run.heat=(run.heat||0)+1; print('<span class="good">+2 stims.</span> <span class="bad">Heat +1.</span>'); }
      },
      {
        label:'Stabilize the trapped survivor', sub:'Spend 20 eddies — +12 Humanity and restore 15% HP',
        disabled:P=>P.eddies<20,
        fn:P=>{ P.eddies-=20; P.humanity=clamp(P.humanity+12,0,P.maxHumanity); const heal=Math.round(P.maxHp*0.15); P.hp=clamp(P.hp+heal,0,P.maxHp); print(`<span class="good">+12 Humanity, +${heal} HP.</span> <span class="warn">-20 eddies.</span>`); }
      },
      {
        label:'Sync the compatible injectors', sub:'MEDTECH PATCH — +1 stim and +8 Humanity',
        show:P=>hasRelic(P,'medtech_patch'),
        cls:'purp',
        fn:P=>{ P.items.stims+=1; P.humanity=clamp(P.humanity+8,0,P.maxHumanity); print('<span class="good">+1 stim, +8 Humanity.</span> Your patch authenticates the medical stack.'); }
      },
      {label:'Leave before backup arrives', fn:()=>print('You are gone before the sirens get close.', 'flavor')}
    ]
  },
  {
    id:'blackwall_echo', minAct:1,
    text:'A dead terminal starts whispering through the Blackwall. Something on the other side knows the shape of your neural signature.',
    opts:[
      {
        label:'Touch the signal', sub:'+2 Tech, -8 Humanity, +1 Heat',
        fn:(P,run)=>{ P.tech+=2; P.humanity=clamp(P.humanity-8,0,P.maxHumanity); run.heat=(run.heat||0)+1; print('<span class="good">+2 Tech.</span> <span class="warn">-8 Humanity.</span> <span class="bad">Heat +1.</span>'); }
      },
      {
        label:'Sandbox the echo', sub:'TECH 8 — +1 Tech and remove 1 Heat',
        disabled:P=>P.tech<8,
        cls:'gold',
        fn:(P,run)=>{ P.tech+=1; run.heat=Math.max(0,(run.heat||0)-1); print('<span class="good">+1 Tech.</span> <span class="accent">Heat -1.</span> The thing never reaches your nervous system.'); }
      },
      {
        label:'Anchor the intrusion', sub:'NEURAL ANCHOR — +1 Tech and +6 Humanity',
        show:P=>hasRelic(P,'neural_anchor'),
        cls:'purp',
        fn:P=>{ P.tech+=1; P.humanity=clamp(P.humanity+6,0,P.maxHumanity); print('<span class="good">+1 Tech, +6 Humanity.</span> The Anchor gives the signal nowhere to go.'); }
      },
      {label:'Kill the terminal', fn:()=>print('The screen dies. The whisper does not follow.', 'flavor')}
    ]
  },
  {
    id:'psycho_aftermath',
    text:'A cyberpsycho is already dead when you arrive. MaxTac has not. The body is a fortune in chrome if you can stomach the extraction.',
    opts:[
      {
        label:'Strip usable chrome', sub:'Free risky install',
        disabled:P=>!uninstalledCyberware(P).length,
        fn:P=>{ const cw=pick(uninstalledCyberware(P)); installCyberware(P,cw,true); }
      },
      {
        label:'Strip only resale parts', sub:"SCAVENGER'S EYE — +45 eddies",
        show:P=>hasRelic(P,'scavenger_eye'),
        cls:'purp',
        fn:P=>{ P.eddies+=45; print('<span class="good">+45 eddies.</span> You know exactly what not to touch.'); }
      },
      {
        label:'Study the chassis', sub:'CHROME JUNKIE — +1 Defense, -5 Humanity',
        show:P=>P.cls==='chrome',
        cls:'purp',
        fn:P=>{ P.def+=1; P.humanity=clamp(P.humanity-5,0,P.maxHumanity); print('<span class="good">+1 Defense.</span> <span class="warn">-5 Humanity.</span> You learn where metal survives and meat fails.'); }
      },
      {label:'Leave the corpse alone', fn:()=>print('Some upgrades should stay buried with their owners.', 'flavor')}
    ]
  },
  {
    id:'ncpd_checkpoint',
    text:'An NCPD checkpoint seals the street ahead. The scanner is old, the officers are tired, and your profile is complicated.',
    opts:[
      {
        label:'Pay the convenience fee', sub:'35 eddies',
        disabled:P=>P.eddies<35,
        fn:P=>{ P.eddies-=35; print('<span class="warn">-35 eddies.</span> Your record becomes somebody else\'s problem.'); }
      },
      {
        label:'Spoof your credentials', sub:'TECH 6 — remove 1 Heat',
        disabled:P=>P.tech<6,
        cls:'gold',
        fn:(P,run)=>{ run.heat=Math.max(0,(run.heat||0)-1); print('<span class="accent">Heat -1.</span> The scanner sees a citizen who does not exist.'); }
      },
      {
        label:'Talk your way through', sub:'COOL 7 — remove 1 Heat',
        disabled:P=>P.cool<7,
        cls:'gold',
        fn:(P,run)=>{ run.heat=Math.max(0,(run.heat||0)-1); print('<span class="accent">Heat -1.</span> Five sentences later they are apologizing to you.'); }
      },
      {
        label:'Take the maintenance alleys', sub:'Lose 8% max HP',
        fn:P=>{ const d=Math.max(2,Math.round(P.maxHp*0.08)); P.hp=clamp(P.hp-d,0,P.maxHp); print(`<span class="bad">-${d} HP.</span> Razor wire and broken concrete beat paperwork.`); }
      }
    ]
  },
  {
    id:'corpo_gala', minAct:3, maxAct:3,
    text:'A Corpo Plaza hotel is hosting a private launch party. Half the guests are armed. The other half own the people who are armed.',
    opts:[
      {
        label:'Work the room', sub:'FIXER — +90 eddies, +1 Heat',
        show:P=>P.cls==='fixer', cls:'purp',
        fn:(P,run)=>{ P.eddies+=90; run.heat=(run.heat||0)+1; print('<span class="good">+90 eddies.</span> <span class="bad">Heat +1.</span> Three new clients and one new enemy.'); }
      },
      {
        label:'Hijack the stage', sub:'ROCKERBOY — +60 eddies and +8 Humanity',
        show:P=>P.cls==='rocker', cls:'purp',
        fn:P=>{ P.eddies+=60; P.humanity=clamp(P.humanity+8,0,P.maxHumanity); print('<span class="good">+60 eddies, +8 Humanity.</span> For six minutes, everybody in the room belongs to you.'); }
      },
      {
        label:'Lift an executive access shard', sub:'COOL 8 — +50 eddies, 35% chance of +1 Heat',
        disabled:P=>P.cool<8,
        cls:'gold',
        fn:(P,run)=>{ P.eddies+=50; const caught=Math.random()<0.35; if(caught) run.heat=(run.heat||0)+1; print(`<span class="good">+50 eddies.</span>${caught?' <span class="bad">Heat +1.</span>':''}`); }
      },
      {label:'Stay invisible', fn:()=>print('The best disguise in Corpo Plaza is looking like you belong.', 'flavor')}
    ]
  },
  {
    id:'weapon_saint',
    text:'A gunsmith known as Saint keeps a folding workbench beneath a shrine of spent brass. "I can tune the weapon you trust, or build you another."',
    opts:[
      {
        label:'Tune your affinity weapon', sub:'25 eddies — +1 damage range and +3% crit',
        disabled:P=>P.eddies<25 || !getClassWeaponAffinity(P),
        cls:'gold',
        fn:P=>{ P.eddies-=25; P.weapon.dmg=[P.weapon.dmg[0]+1,P.weapon.dmg[1]+1]; P.weapon.crit=+(P.weapon.crit+0.03).toFixed(2); print(`<span class="good">${P.weapon.name} tuned: +1 damage, +3% crit.</span>`); }
      },
      {
        label:'Take a prototype of your preferred weapon', sub:'-8 Humanity — Militech-tier class weapon',
        fn:P=>{ const aff=getAffinityDefinition(P); const w=rollWeapon(aff.baseId,3); addToInventory(P,w); P.humanity=clamp(P.humanity-8,0,P.maxHumanity); print(`Saint slides over a <b>${w.name}</b>. <span class="warn">-8 Humanity.</span>`); }
      },
      {label:'Keep your current iron', fn:()=>print('Saint shrugs. "Knowing when not to change a weapon is a skill too."', 'flavor')}
    ]
  },
  {
    id:'relic_broker',
    text:'A black-market broker opens a velvet case containing one sealed relic. "Eddies, favors, blood. Value is value."',
    opts:[
      {
        label:'Buy the sealed relic', sub:'55 eddies',
        disabled:P=>P.eddies<55 || !unownedRelics(P).length,
        cls:'purp',
        fn:P=>{ P.eddies-=55; const r=pick(unownedRelics(P)); grantRelic(P,r); }
      },
      {
        label:'Call in a debt marker', sub:'FIXER — relic for 35 eddies',
        show:P=>P.cls==='fixer',
        disabled:P=>P.eddies<35 || !unownedRelics(P).length,
        cls:'purp',
        fn:P=>{ P.eddies-=35; const r=pick(unownedRelics(P)); grantRelic(P,r); print('<span class="accent">Network discount applied.</span>'); }
      },
      {
        label:'Pay in blood', sub:'Lose 5 max HP — gain a random relic',
        disabled:P=>P.maxHp<=15 || !unownedRelics(P).length,
        cls:'danger',
        fn:P=>{ P.maxHp=Math.max(10,P.maxHp-5); P.hp=Math.min(P.hp,P.maxHp); const r=pick(unownedRelics(P)); grantRelic(P,r); print('<span class="bad">-5 max HP.</span> The broker never asked whose blood.'); }
      },
      {label:'Close the case', fn:()=>print('The broker smiles like you made the expensive choice.', 'flavor')}
    ]
  }
];'''
regex_once(r"const EVENTS = \[.*?\n\];\n\n// ================= STATE =================", events_block + "\n\n// ================= STATE =================", 'event pool replacement')


# ------------------------------------------------------------------
# Relic pickup announces newly completed synergies
# ------------------------------------------------------------------
replace_once(
"""function grantRelic(P, relic){
  P.relics.push(relic);
  if(relic.apply) relic.apply(P);
  print(`<span class=\"tag relic\">RELIC</span> Acquired <b class=\"purp\">${relic.name}</b> — ${relic.desc}`);
}""",
"""function grantRelic(P, relic){
  const before = new Set(getActiveRelicSynergies(P).map(s=>s.id));
  P.relics.push(relic);
  if(relic.apply) relic.apply(P);
  print(`<span class=\"tag relic\">RELIC</span> Acquired <b class=\"purp\">${relic.name}</b> — ${relic.desc}`);
  getActiveRelicSynergies(P)
    .filter(s=>!before.has(s.id))
    .forEach(s=>print(`<span class=\"tag relic\">SYNERGY</span> <b class=\"purp\">${s.name}</b> online — ${s.desc}`));
}""",
'grant relic synergy announcement'
)


# ------------------------------------------------------------------
# Run tracks recent mystery events to prevent immediate repeats
# ------------------------------------------------------------------
replace_once(
"""kills:0, eliteKills:0, actBuffs:[], actEddiesMult:1, actContactDone:false,
            starting:true, hardMode: !!hardMode""",
"""kills:0, eliteKills:0, actBuffs:[], actEddiesMult:1, actContactDone:false,
            eventHistory:[], starting:true, hardMode: !!hardMode""",
'event history run state'
)


# ------------------------------------------------------------------
# Conditional event renderer
# ------------------------------------------------------------------
replace_once(
"""function runEvent(){
  const P = S.run.player;
  const ev = pick(EVENTS);
  print(`<span class=\"tag\">SIGNAL</span> ${ev.text}`, 'sys');
  actions(ev.opts.map(o=>({label:o.label, fn:()=>{ o.fn(P); divider(); advance(); }})));
}""",
"""function runEvent(){
  const P = S.run.player;
  const run = S.run;
  run.eventHistory = run.eventHistory || [];

  const eligible = EVENTS.filter(ev=>
    (ev.minAct==null || run.act>=ev.minAct) &&
    (ev.maxAct==null || run.act<=ev.maxAct)
  );
  const recent = new Set(run.eventHistory.slice(-3));
  const fresh = eligible.filter(ev=>!recent.has(ev.id));
  const ev = pick(fresh.length ? fresh : eligible);

  run.eventHistory.push(ev.id);
  run.eventHistory = run.eventHistory.slice(-5);

  print(`<span class=\"tag\">MYSTERY SIGNAL</span> ${ev.text}`, 'sys');

  const opts = ev.opts
    .filter(o=>!o.show || o.show(P,run))
    .map(o=>{
      const disabled = typeof o.disabled==='function' ? o.disabled(P,run) : !!o.disabled;
      const label = typeof o.label==='function' ? o.label(P,run) : o.label;
      const sub = typeof o.sub==='function' ? o.sub(P,run) : o.sub;
      return {
        label, sub, cls:o.cls, disabled,
        fn:()=>{
          const result = o.fn ? o.fn(P,run) : null;
          refreshStatus();
          checkCyberpsychosis(P);
          if(P.hp<=0 && checkDeath()) return;
          if(result && result.advance===false) return;
          divider();
          advance();
        }
      };
    });

  actions(opts);
}""",
'conditional event renderer'
)


# ------------------------------------------------------------------
# Character Sheet shows active relic combinations
# ------------------------------------------------------------------
replace_once(
"""  const relicHtml = P.relics.length
    ? P.relics.map(r=>`<div class=\"sheetItem\"><b>${r.name}</b><small>${r.desc}</small></div>`).join('')
    : '<div class=\"sheetEmpty\">No relics acquired.</div>';
  const inventoryHtml = P.inventory.length""",
"""  const relicHtml = P.relics.length
    ? P.relics.map(r=>`<div class=\"sheetItem\"><b>${r.name}</b><small>${r.desc}</small></div>`).join('')
    : '<div class=\"sheetEmpty\">No relics acquired.</div>';
  const activeSynergies = getActiveRelicSynergies(P);
  const synergyHtml = activeSynergies.length
    ? activeSynergies.map(s=>`<div class=\"sheetItem\"><b class=\"purp\">${s.name}</b><small>${s.desc}</small></div>`).join('')
    : '<div class=\"sheetEmpty\">No relic synergies online yet.</div>';
  const inventoryHtml = P.inventory.length""",
'character sheet synergy data'
)

replace_once(
"""    <section class=\"sheetSection\">
      <h3>RELICS // ${P.relics.length}</h3>
      ${relicHtml}
    </section>

    <section class=\"sheetSection\">
      <h3>ACTIVE DISTRICT BOONS</h3>""",
"""    <section class=\"sheetSection\">
      <h3>RELICS // ${P.relics.length}</h3>
      ${relicHtml}
    </section>

    <section class=\"sheetSection\">
      <h3>RELIC SYNERGIES // ${activeSynergies.length}</h3>
      ${synergyHtml}
    </section>

    <section class=\"sheetSection\">
      <h3>ACTIVE DISTRICT BOONS</h3>""",
'character sheet synergy section'
)


# ------------------------------------------------------------------
# Guide explains event checks and relic synergies
# ------------------------------------------------------------------
replace_once(
"""      <div class=\"guideRow\"><b>Nodes</b> — Districts can contain combat, events, Ripperdocs, safehouses, relic caches, Fixer contacts, and elites. Normal districts end with an elite.</div>""",
"""      <div class=\"guideRow\"><b>Nodes</b> — Districts can contain combat, mystery events, Ripperdocs, safehouses, relic caches, Fixer contacts, and elites. Normal districts end with an elite.</div>
      <div class=\"guideRow\"><b>Mystery checks</b> — Some event choices require TECH, COOL, a specific class, or a particular relic. Stat-gated choices remain visible so you can see what your build could have unlocked.</div>""",
'guide event checks'
)
replace_once(
"""      <div class=\"guideRow\"><b>Relics</b> — Passive run modifiers. They can alter damage, healing, Guard, Evade, economy, survivability, and other systems.</div>""",
"""      <div class=\"guideRow\"><b>Relics</b> — Passive run modifiers. They can alter damage, healing, Guard, Evade, economy, survivability, and other systems.</div>
      <div class=\"guideRow\"><b>Relic Synergies</b> — Certain relic pairs combine into named effects. When a combo comes online, Cyberdoom announces it and lists the active synergy in your Character Sheet.</div>""",
'guide relic synergies'
)


# ------------------------------------------------------------------
# Synergy mechanics
# ------------------------------------------------------------------
replace_once(
"""    { label:'Use Stim', sub:`Heal ${hasRelic(P,'medtech_patch') ? '35' : '25'}% HP (${P.items.stims} left)`, disabled: P.items.stims<=0, fn:()=>useStim() },""",
"""    { label:'Use Stim', sub:`Heal ${hasRelic(P,'medtech_patch') ? '35' : '25'}% HP${hasRelicSynergy(P,'trauma_rig')?' + 5 Humanity':''} (${P.items.stims} left)`, disabled: P.items.stims<=0, fn:()=>useStim() },""",
'combat menu trauma rig'
)
replace_once(
"""    { label:'Guard', sub:`Reduce the next incoming hit by ${hasRelic(P,'guardian_daemon') ? '65' : '50'}%`, cls:'gold', fn:()=>guardAction() },""",
"""    { label:'Guard', sub:`Reduce the next incoming hit by ${hasRelicSynergy(P,'fortress_stack') ? '75' : hasRelic(P,'guardian_daemon') ? '65' : '50'}%`, cls:'gold', fn:()=>guardAction() },""",
'combat menu fortress stack'
)

replace_once(
"""  P.hp = clamp(P.hp+heal, 0, P.maxHp);
  print(`<span class=\"tag hack\">STIM</span> <span class=\"good\">+${heal} HP.</span>`);""",
"""  P.hp = clamp(P.hp+heal, 0, P.maxHp);
  let extra = '';
  if(hasRelicSynergy(P,'trauma_rig')){
    const hum = Math.min(5,P.maxHumanity-P.humanity);
    P.humanity = clamp(P.humanity+5,0,P.maxHumanity);
    extra = ` <span class=\"purp\">Trauma Rig: +${hum} Humanity.</span>`;
  }
  print(`<span class=\"tag hack\">STIM</span> <span class=\"good\">+${heal} HP.</span>${extra}`);""",
'useStim trauma rig'
)

replace_once(
"""  const guardPct = hasRelic(P,'guardian_daemon') ? 65 : 50;""",
"""  const guardPct = hasRelicSynergy(P,'fortress_stack') ? 75 : hasRelic(P,'guardian_daemon') ? 65 : 50;""",
'guard fortress stack'
)

replace_once(
"""  if(isCrit && hasRelic(P,'bloodwire')){ P.hp=clamp(P.hp+2,0,P.maxHp); extra+=' <span class=\"good\">+2 HP (Bloodwire).</span>'; }""",
"""  if(isCrit && hasRelic(P,'bloodwire')){
    const heal = hasRelicSynergy(P,'redline_loop') ? 3 : 2;
    P.hp=clamp(P.hp+heal,0,P.maxHp);
    extra+=` <span class=\"good\">+${heal} HP (${hasRelicSynergy(P,'redline_loop')?'Redline Loop':'Bloodwire'}).</span>`;
  }""",
'redline loop crit healing'
)

replace_once(
"""      let crit = Math.random() < critChance;
      if(i===0 && !c.firstHitUsed && hasRelic(P,\"widows_kiss\")){ crit=true; c.firstHitUsed=true; }
      let d = crit ? Math.round(base*1.8) : base;
      d = Math.max(1, d - armorPerHit);
      c.enemy.hp -= d; totalDmg += d; anyCrit = anyCrit||crit;
      effectsHtml += applyHitEffects(P, c, d, crit);""",
"""      let crit = Math.random() < critChance;
      let openingExecution = false;
      if(i===0 && !c.firstHitUsed && hasRelic(P,\"widows_kiss\")){
        crit=true;
        c.firstHitUsed=true;
        openingExecution = hasRelicSynergy(P,'execution_protocol');
      }
      let d = crit ? Math.round(base*1.8) : base;
      const armorThisHit = openingExecution ? Math.max(0,armorPerHit-2) : armorPerHit;
      d = Math.max(1, d - armorThisHit);
      c.enemy.hp -= d; totalDmg += d; anyCrit = anyCrit||crit;
      effectsHtml += applyHitEffects(P, c, d, crit);
      if(openingExecution) effectsHtml += ' <span class=\"purp\">EXECUTION PROTOCOL: -2 armor.</span>';""",
'execution protocol opening hit'
)

replace_once(
"""        d = 0;
        avoided = true;
      } else {""",
"""        d = 0;
        avoided = true;
        if(hasRelicSynergy(P,'ghost_protocol') && P.ability.cdLeft>0){
          P.ability.cdLeft = Math.max(0,P.ability.cdLeft-1);
          print('<span class=\"tag relic\">GHOST PROTOCOL</span> Successful Evade cuts your special cooldown by 1.');
        }
      } else {""",
'ghost protocol evade cooldown'
)

replace_once(
"""      P.usedSecondWind = true; P.hp = 1;
      print(`<span class=\"tag relic\">SECOND WIND</span> <span class=\"purp\">Your relic flatlines instead of you — emergency systems kick your heart back on. 1 HP.</span>`);""",
"""      P.usedSecondWind = true;
      const reviveHp = hasRelicSynergy(P,'last_breath') ? Math.max(1,Math.round(P.maxHp*0.25)) : 1;
      P.hp = reviveHp;
      print(`<span class=\"tag relic\">SECOND WIND</span> <span class=\"purp\">Your relic flatlines instead of you — emergency systems kick your heart back on. ${reviveHp} HP.${hasRelicSynergy(P,'last_breath')?' LAST BREATH online.':''}</span>`);""",
'last breath revive'
)

replace_once(
"""  const lootChance = 0.35 + (hasRelic(P,'scavenger_eye') ? 0.15 : 0);
  if(c.guaranteedLoot || Math.random()<lootChance){
    if(Math.random()<0.5){""",
"""  const scavengerContract = hasRelicSynergy(P,'scavenger_contract');
  const lootChance = 0.35 + (hasRelic(P,'scavenger_eye') ? 0.15 : 0) + (scavengerContract ? 0.10 : 0);
  if(c.guaranteedLoot || Math.random()<lootChance){
    if(scavengerContract){
      P.eddies += 10;
      print('<span class=\"tag relic\">SCAVENGER CONTRACT</span> <span class=\"good\">+10 eddies salvage fee.</span>');
    }
    if(Math.random()<0.5){""",
'scavenger contract loot'
)

path.write_text(text)
