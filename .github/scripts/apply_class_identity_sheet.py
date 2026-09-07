from pathlib import Path
import re

path = Path('index.html')
text = path.read_text()


def replace_once(old, new, label):
    global text
    if old not in text:
        raise SystemExit(f'Patch target not found: {label}')
    text = text.replace(old, new, 1)


# ---------- HUD button + character sheet overlay ----------
replace_once(
"""    <span class=\"hudClass\" id=\"stClass\">-</span>""",
"""    <button class=\"hudClass hudSheetBtn\" id=\"stClass\" type=\"button\" onclick=\"openCharacterSheet()\" aria-label=\"Open character sheet\">-</button>""",
'character sheet HUD button'
)

replace_once(
"""</div>
  <div id=\"log\"></div>
  <div id=\"actions\"></div>""",
"""</div>

  <div id=\"charSheet\" class=\"sheetOverlay\" aria-hidden=\"true\">
    <div class=\"sheetPanel\">
      <div class=\"sheetHead\">
        <div>
          <div class=\"sheetEyebrow\">RUN // CHARACTER DATA</div>
          <h2 id=\"sheetTitle\">CHARACTER SHEET</h2>
        </div>
        <button id=\"sheetClose\" type=\"button\" onclick=\"closeCharacterSheet()\" aria-label=\"Close character sheet\">×</button>
      </div>
      <div id=\"sheetBody\"></div>
    </div>
  </div>

  <div id=\"log\"></div>
  <div id=\"actions\"></div>""",
'character sheet overlay HTML'
)

replace_once(
"""  .cardgrid{display:grid; gap:10px;}""",
"""  .hudSheetBtn{
    appearance:none;
    -webkit-appearance:none;
    border:0;
    background:transparent;
    padding:0;
    margin:0;
    text-align:left;
    font-family:inherit;
    cursor:pointer;
  }
  .hudSheetBtn::after{
    content:'  ▾';
    color:var(--dim);
    font-size:9px;
  }

  .sheetOverlay{
    display:none;
    position:fixed;
    inset:0;
    z-index:100;
    background:rgba(2,4,7,0.94);
    padding-top:env(safe-area-inset-top);
    padding-bottom:env(safe-area-inset-bottom);
  }
  .sheetOverlay.on{display:flex;}
  .sheetPanel{
    width:100%;
    max-width:640px;
    height:100%;
    margin:0 auto;
    overflow-y:auto;
    -webkit-overflow-scrolling:touch;
    background:var(--bg);
    border-left:1px solid var(--line);
    border-right:1px solid var(--line);
    padding:14px;
  }
  .sheetHead{
    position:sticky;
    top:0;
    z-index:2;
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:12px;
    padding:8px 0 12px;
    margin-bottom:10px;
    background:rgba(4,5,7,0.97);
    border-bottom:1px solid var(--line);
  }
  .sheetHead h2{
    margin:2px 0 0;
    color:var(--cyan);
    font-size:18px;
    letter-spacing:1px;
  }
  .sheetEyebrow{
    color:var(--dim);
    font-size:9px;
    letter-spacing:1.5px;
  }
  #sheetClose{
    width:40px;
    height:40px;
    flex:0 0 auto;
    border:1px solid var(--line);
    border-radius:6px;
    background:var(--panel2);
    color:var(--text);
    font-family:inherit;
    font-size:24px;
    line-height:1;
  }
  .sheetSection{
    margin:0 0 12px;
    padding:11px;
    border:1px solid var(--line);
    border-radius:7px;
    background:var(--panel);
  }
  .sheetSection h3{
    margin:0 0 8px;
    color:var(--magenta);
    font-size:11px;
    letter-spacing:1.2px;
  }
  .sheetStatGrid{
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:7px;
  }
  .sheetStat{
    padding:7px;
    border:1px solid var(--line);
    border-radius:5px;
    background:var(--panel2);
    min-width:0;
  }
  .sheetStat span{
    display:block;
    color:var(--dim);
    font-size:8px;
    letter-spacing:.8px;
  }
  .sheetStat b{
    display:block;
    margin-top:2px;
    color:var(--text);
    font-size:12px;
    overflow:hidden;
    text-overflow:ellipsis;
  }
  .sheetItem{
    padding:8px 0;
    border-top:1px dashed var(--line);
  }
  .sheetItem:first-of-type{border-top:0; padding-top:0;}
  .sheetItem:last-child{padding-bottom:0;}
  .sheetItem b{color:var(--text);}
  .sheetItem small{
    display:block;
    margin-top:2px;
    color:var(--dim);
    font-size:10px;
  }
  .sheetAffinity{
    padding:9px;
    border:1px solid rgba(47,230,224,0.35);
    border-radius:6px;
    background:rgba(47,230,224,0.05);
  }
  .sheetAffinity.inactive{
    border-color:var(--line);
    background:var(--panel2);
    opacity:.72;
  }
  .sheetEmpty{color:var(--dim); font-style:italic;}
  .sheetEquipped{color:var(--green); font-size:9px; letter-spacing:1px;}

  .cardgrid{display:grid; gap:10px;}""",
'character sheet CSS'
)

# Close the overlay automatically whenever the run HUD is turned off.
replace_once(
"""    const enemyHud = $('#enemyStatus');
    if(enemyHud) enemyHud.classList.remove('on');
  }
}function updateHeader()""",
"""    const enemyHud = $('#enemyStatus');
    if(enemyHud) enemyHud.classList.remove('on');
    const sheet = $('#charSheet');
    if(sheet) sheet.classList.remove('on');
  }
}function updateHeader()""",
'character sheet cleanup'
)


# ---------- class weapon affinities ----------
replace_once(
"""const CLASSES = [
  { id:'solo', name:'Solo', tagline:'Corporate-trained killing machine.',
    hp:34, dmg:[4,7], def:3, tech:1, cool:4, humanity:100,
    weapon:'pistol', ability:{name:'Overwatch', desc:'+60% damage this turn, ignore 2 armor.', cd:3} },
  { id:'netrunner', name:'Netrunner', tagline:'Lives in the net more than the meat.',
    hp:24, dmg:[2,4], def:1, tech:6, cool:4, humanity:85,
    weapon:'monowire', ability:{name:'Quickhack', desc:'Armor-piercing tech damage that scales with target HP, breaches 1 armor, and can stun.', cd:2} },
  { id:'chrome', name:'Chrome Junkie', tagline:'More metal than man. Getting worse.',
    hp:44, dmg:[5,9], def:5, tech:0, cool:0, humanity:55,
    weapon:'gorilla_arms', ability:{name:'Berserk', desc:'Damage scales up as your HP drops. Costs Humanity to use.', cd:2} },
  { id:'samurai', name:'Samurai', tagline:'Steel over chrome. Honor over eddies.',
    hp:28, dmg:[6,9], def:2, tech:1, cool:5, humanity:95,
    weapon:'katana', ability:{name:'Blade Dance', desc:'Guaranteed crit; crits chain into a free bonus strike.', cd:3} },
  { id:'rocker', name:'Rockerboy', tagline:'Every gig might be the last encore.',
    hp:28, dmg:[3,6], def:2, tech:2, cool:7, humanity:100,
    weapon:'smg', ability:{name:'Rally Cry', desc:'Buff all stats for 3 turns.', cd:4} },
  { id:'nomad', name:'Nomad', tagline:'Family, road, and a well-oiled shotgun.',
    hp:32, dmg:[5,8], def:4, tech:2, cool:3, humanity:100,
    weapon:'shotgun', ability:{name:'Scavenger Instinct', desc:'Guarantees bonus loot after this fight.', cd:0} },
  { id:'fixer', name:'Fixer', tagline:'Knows a guy who knows a guy.',
    hp:26, dmg:[3,5], def:2, tech:3, cool:6, humanity:100,
    weapon:'silenced_pistol', ability:{name:'Connections', desc:'Call in armor-piercing backup and mark the target for +25% eddies. Fixers also get +1 shop reroll.', cd:3} },
];""",
"""const CLASSES = [
  { id:'solo', name:'Solo', tagline:'Corporate-trained killing machine.',
    hp:34, dmg:[4,7], def:3, tech:1, cool:4, humanity:100,
    weapon:'pistol', ability:{name:'Overwatch', desc:'+60% damage this turn, ignore 2 armor.', cd:3} },
  { id:'netrunner', name:'Netrunner', tagline:'Lives in the net more than the meat.',
    hp:24, dmg:[2,4], def:1, tech:6, cool:4, humanity:85,
    weapon:'monowire', ability:{name:'Quickhack', desc:'Armor-piercing tech damage that scales with target HP, breaches 1 armor, and can stun.', cd:2} },
  { id:'chrome', name:'Chrome Junkie', tagline:'More metal than man. Getting worse.',
    hp:44, dmg:[5,9], def:5, tech:0, cool:0, humanity:55,
    weapon:'gorilla_arms', ability:{name:'Berserk', desc:'Damage scales up as your HP drops. Costs Humanity to use.', cd:2} },
  { id:'samurai', name:'Samurai', tagline:'Steel over chrome. Honor over eddies.',
    hp:28, dmg:[6,9], def:2, tech:1, cool:5, humanity:95,
    weapon:'katana', ability:{name:'Blade Dance', desc:'Guaranteed crit; crits chain into a free bonus strike.', cd:3} },
  { id:'rocker', name:'Rockerboy', tagline:'Every gig might be the last encore.',
    hp:28, dmg:[3,6], def:2, tech:2, cool:7, humanity:100,
    weapon:'smg', ability:{name:'Rally Cry', desc:'Buff all stats for 3 turns.', cd:4} },
  { id:'nomad', name:'Nomad', tagline:'Family, road, and a well-oiled shotgun.',
    hp:32, dmg:[5,8], def:4, tech:2, cool:3, humanity:100,
    weapon:'shotgun', ability:{name:'Scavenger Instinct', desc:'Guarantees bonus loot after this fight.', cd:0} },
  { id:'fixer', name:'Fixer', tagline:'Knows a guy who knows a guy.',
    hp:26, dmg:[3,5], def:2, tech:3, cool:6, humanity:100,
    weapon:'silenced_pistol', ability:{name:'Connections', desc:'Call in armor-piercing backup and mark the target for +25% eddies. Fixers also get +1 shop reroll.', cd:3} },
];

const CLASS_WEAPON_AFFINITY = {
  solo: {
    baseId:'pistol', name:'Sidearm Doctrine',
    desc:'Pistol weapon attacks deal +15% damage and gain +5% crit chance.',
    damageMult:1.15, critBonus:0.05
  },
  netrunner: {
    baseId:'monowire', name:'Neural Conduit',
    desc:'Monowire weapon attacks gain +2 Tech damage and +5% crit chance.',
    techBonus:2, critBonus:0.05
  },
  chrome: {
    baseId:'gorilla_arms', name:'Full-Force Interface',
    desc:'Gorilla Arms weapon attacks deal +20% damage.',
    damageMult:1.20
  },
  samurai: {
    baseId:'katana', name:'Blade Discipline',
    desc:'Katana weapon attacks gain +15% crit chance.',
    critBonus:0.15
  },
  rocker: {
    baseId:'smg', name:'Full-Auto Rhythm',
    desc:'SMG weapon attacks gain +1 damage on every shot.',
    flatDamage:1
  },
  nomad: {
    baseId:'shotgun', name:'Roadside Breacher',
    desc:'Shotgun weapon attacks deal +20% damage.',
    damageMult:1.20
  },
  fixer: {
    baseId:'silenced_pistol', name:'Quiet Professional',
    desc:'Silenced Pistol weapon attacks gain +1 damage and +10% crit chance.',
    flatDamage:1, critBonus:0.10
  },
};

function getAffinityDefinition(P){
  return P ? CLASS_WEAPON_AFFINITY[P.cls] || null : null;
}

function getClassWeaponAffinity(P){
  const affinity = getAffinityDefinition(P);
  if(!affinity || !P.weapon || P.weapon.baseId !== affinity.baseId) return null;
  return affinity;
}""",
'class weapon affinities'
)


# ---------- character sheet functions ----------
replace_once(
"""function getThreatLevel(P, e, c){""",
"""function closeCharacterSheet(){
  const sheet = $('#charSheet');
  if(!sheet) return;
  sheet.classList.remove('on');
  sheet.setAttribute('aria-hidden','true');
}

function openCharacterSheet(){
  if(!S.run || S.run.over) return;
  renderCharacterSheet();
  const sheet = $('#charSheet');
  sheet.classList.add('on');
  sheet.setAttribute('aria-hidden','false');
}

function renderCharacterSheet(){
  if(!S.run) return;

  const run = S.run;
  const P = run.player;
  const affinityDef = getAffinityDefinition(P);
  const affinity = getClassWeaponAffinity(P);
  const baseWeapon = WEAPON_BASE[P.weapon.baseId];
  const effectiveCrit = Math.max(0, P.weapon.crit + P.critBonus + (affinity?.critBonus||0));
  const dodgePct = Math.round((P.dodge||0)*100);
  const boonHtml = run.actBuffs && run.actBuffs.length
    ? run.actBuffs.map(b=>`<div class=\"sheetItem\"><b>${b.label}</b><small>${b.sub}</small></div>`).join('')
    : '<div class=\"sheetEmpty\">No active district boons.</div>';
  const chromeHtml = P.cyberware.length
    ? P.cyberware.map(c=>`<div class=\"sheetItem\"><b>${c.name}</b> <span class=\"flavor\">// ${c.slot}</span><small>${c.desc} · Humanity cost ${c.hum}</small></div>`).join('')
    : '<div class=\"sheetEmpty\">No chrome installed.</div>';
  const relicHtml = P.relics.length
    ? P.relics.map(r=>`<div class=\"sheetItem\"><b>${r.name}</b><small>${r.desc}</small></div>`).join('')
    : '<div class=\"sheetEmpty\">No relics acquired.</div>';
  const inventoryHtml = P.inventory.length
    ? P.inventory.map((w,i)=>{
        const base = WEAPON_BASE[w.baseId];
        const equipped = w===P.weapon;
        const aff = affinityDef && w.baseId===affinityDef.baseId;
        return `<div class=\"sheetItem\">
          <b>${i+1}. ${w.name}</b> ${equipped?'<span class=\"sheetEquipped\">EQUIPPED</span>':''}
          <small>${base ? base.name : w.baseId} · ${w.dmg[0]}–${w.dmg[1]} dmg · ${Math.round(w.crit*100)}% base crit · ${w.hits||1} hit${(w.hits||1)>1?'s':''}${w.mutation?` · ${w.mutation.name}: ${w.mutation.desc}`:''}${aff?' · CLASS AFFINITY WEAPON':''}</small>
        </div>`;
      }).join('')
    : '<div class=\"sheetEmpty\">Inventory empty.</div>';

  $('#sheetTitle').textContent = `${P.className.toUpperCase()} // STATUS`;
  $('#sheetBody').innerHTML = `
    <section class=\"sheetSection\">
      <h3>CORE STATUS</h3>
      <div class=\"sheetStatGrid\">
        <div class=\"sheetStat\"><span>HP</span><b>${Math.max(0,P.hp)}/${P.maxHp}</b></div>
        <div class=\"sheetStat\"><span>HUMANITY</span><b>${Math.max(0,P.humanity)}/${P.maxHumanity}</b></div>
        <div class=\"sheetStat\"><span>EDDIES</span><b>€$ ${P.eddies}</b></div>
        <div class=\"sheetStat\"><span>DEFENSE</span><b>${P.def}</b></div>
        <div class=\"sheetStat\"><span>TECH</span><b>${P.tech}</b></div>
        <div class=\"sheetStat\"><span>COOL</span><b>${P.cool}</b></div>
        <div class=\"sheetStat\"><span>DMG BONUS</span><b>+${P.dmgBonus||0}</b></div>
        <div class=\"sheetStat\"><span>DODGE</span><b>${dodgePct}%</b></div>
        <div class=\"sheetStat\"><span>REGEN</span><b>${P.regen||0}/turn</b></div>
        <div class=\"sheetStat\"><span>CDR</span><b>${P.cdrBonus||0}</b></div>
        <div class=\"sheetStat\"><span>STIMS</span><b>${P.items.stims}</b></div>
        <div class=\"sheetStat\"><span>HEAT</span><b>${run.heat||0}</b></div>
      </div>
    </section>

    <section class=\"sheetSection\">
      <h3>CLASS IDENTITY</h3>
      <div class=\"sheetAffinity ${affinity?'':'inactive'}\">
        <b class=\"${affinity?'accent':'flavor'}\">${affinity?'AFFINITY ACTIVE':'AFFINITY INACTIVE'} // ${affinityDef?.name||'—'}</b>
        <div>${affinityDef?.desc||'No class weapon affinity.'}</div>
        <small class=\"flavor\">Preferred weapon: ${affinityDef && WEAPON_BASE[affinityDef.baseId] ? WEAPON_BASE[affinityDef.baseId].name : '—'}</small>
      </div>
      <div class=\"sheetItem\"><b>${P.ability.name}</b><small>${P.ability.desc} · Cooldown ${P.ability.cd}${P.ability.cdLeft>0?` · ${P.ability.cdLeft} turns remaining`:' · READY'}</small></div>
      <div class=\"sheetItem\"><b>Run position</b><small>${run.starting?'Loadout Cache':`${run.actName} ${run.node+1}/${run.actLen}`} · ${run.hardMode?'OVERWATCH MODE':'Standard difficulty'} · ${run.kills} kills · ${run.eliteKills} elite/boss kills</small></div>
    </section>

    <section class=\"sheetSection\">
      <h3>EQUIPPED WEAPON</h3>
      <div class=\"sheetItem\">
        <b>${P.weapon.name}</b>
        <small>${baseWeapon ? baseWeapon.name : P.weapon.baseId} · ${P.weapon.dmg[0]}–${P.weapon.dmg[1]} dmg · ${Math.round(effectiveCrit*100)}% effective crit · ${P.weapon.hits||1} hit${(P.weapon.hits||1)>1?'s':''}${P.weapon.tech?' · TECH WEAPON':''}</small>
        ${P.weapon.mutation?`<small class=\"accent\">Mutation: ${P.weapon.mutation.name} — ${P.weapon.mutation.desc}</small>`:''}
      </div>
    </section>

    <section class=\"sheetSection\">
      <h3>CYBERWARE // ${P.cyberware.length}</h3>
      ${chromeHtml}
    </section>

    <section class=\"sheetSection\">
      <h3>RELICS // ${P.relics.length}</h3>
      ${relicHtml}
    </section>

    <section class=\"sheetSection\">
      <h3>ACTIVE DISTRICT BOONS</h3>
      ${boonHtml}
    </section>

    <section class=\"sheetSection\">
      <h3>WEAPON INVENTORY // ${P.inventory.length}/6</h3>
      ${inventoryHtml}
    </section>
  `;
}

function getThreatLevel(P, e, c){""",
'character sheet functions'
)


# ---------- combat affinity hooks ----------
replace_once(
"""  const ab = P.ability;
  actions([
    { label:'Attack', sub:`${P.weapon.name}`, fn:()=>playerAttack(false) },""",
"""  const ab = P.ability;
  const affinity = getClassWeaponAffinity(P);
  actions([
    { label:'Attack', sub:`${P.weapon.name}${affinity?' • AFFINITY':''}`, fn:()=>playerAttack(false) },""",
'combat menu affinity indicator'
)

replace_once(
"""  let hits = (P.weapon.hits || 1) + (P.weapon.mutation && P.weapon.mutation.id==='fragment' ? 1 : 0);
  let totalDmg = 0, anyCrit=false, effectsHtml='';""",
"""  const affinity = getClassWeaponAffinity(P);
  let hits = (P.weapon.hits || 1) + (P.weapon.mutation && P.weapon.mutation.id==='fragment' ? 1 : 0);
  let totalDmg = 0, anyCrit=false, effectsHtml='';""",
'player attack affinity state'
)

replace_once(
"""      let base = rnd(...P.weapon.dmg) + P.dmgBonus + (P.weapon.tech?P.tech:0);
      if(hasRelic(P,'adrenal_plug') && P.hp < P.maxHp*0.3) base += 3;
      let critChance = P.weapon.crit + P.critBonus + (berserkMode?0.25:0);""",
"""      let base = rnd(...P.weapon.dmg) + P.dmgBonus + (P.weapon.tech?P.tech:0);
      if(affinity){
        base += (affinity.techBonus||0) + (affinity.flatDamage||0);
        if(affinity.damageMult) base = Math.round(base * affinity.damageMult);
      }
      if(hasRelic(P,'adrenal_plug') && P.hp < P.maxHp*0.3) base += 3;
      let critChance = P.weapon.crit + P.critBonus + (affinity?.critBonus||0) + (berserkMode?0.25:0);""",
'weapon affinity damage and crit'
)

replace_once(
"""    print(`<span class=\"tag${anyCrit?' crit':''}\">HIT</span> ${P.weapon.name} deals <b>${totalDmg}</b> damage${hits>1?` across ${hits} shots`:''}.${anyCrit?' <span class=\"warn\">CRITICAL!</span>':''}${berserkMode?' <span class=\"bad\">(chrome-fueled rage)</span>':''}${effectsHtml}`);""",
"""    print(`<span class=\"tag${anyCrit?' crit':''}\">HIT</span> ${P.weapon.name} deals <b>${totalDmg}</b> damage${hits>1?` across ${hits} shots`:''}.${affinity?' <span class=\"accent\">CLASS AFFINITY</span>':''}${anyCrit?' <span class=\"warn\">CRITICAL!</span>':''}${berserkMode?' <span class=\"bad\">(chrome-fueled rage)</span>':''}${effectsHtml}`);""",
'weapon affinity combat log'
)


# ---------- class select affinity description ----------
replace_once(
"""      Weapon: <b>${WEAPON_BASE[c.weapon].name}</b> · Ability: <b>${c.ability.name}</b> — ${c.ability.desc}<br>Mastery: ${m.kills} kills / ${m.wins} wins</div>`;""",
"""      Weapon: <b>${WEAPON_BASE[c.weapon].name}</b> · Ability: <b>${c.ability.name}</b> — ${c.ability.desc}<br>
      Affinity: <b>${CLASS_WEAPON_AFFINITY[c.id].name}</b> — ${CLASS_WEAPON_AFFINITY[c.id].desc}<br>Mastery: ${m.kills} kills / ${m.wins} wins</div>`;""",
'class select affinity copy'
)

path.write_text(text)
