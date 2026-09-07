from pathlib import Path

path = Path('index.html')
text = path.read_text()


def replace_once(old, new, label):
    global text
    if old not in text:
        raise SystemExit(f'Patch target not found: {label}')
    text = text.replace(old, new, 1)


# ---------- Cyberdoom branding ----------
replace_once('<title>NIGHT CITY // FLATLINE</title>', '<title>Cyberdoom</title>', 'document title')
replace_once(
    '<div class="title">NIGHT CITY <span>// FLATLINE</span></div>',
    '<div class="title">CYBER<span>DOOM</span></div>',
    'header brand'
)
text = text.replace('NIGHT CITY // FLATLINE v2 — cyberpunk text roguelike', 'CYBERDOOM v2 — cyberpunk text roguelike')
text = text.replace('// Hide the NIGHT CITY banner during an active run', '// Hide the Cyberdoom banner during an active run')
text = text.replace('<h1>NIGHT CITY <span>// FLATLINE</span></h1>', '<h1>CYBER<span>DOOM</span></h1>')


# ---------- Guide styling ----------
replace_once(
"""  .masteryPlate.legendary{
    color:var(--magenta);
    border-color:rgba(255,46,136,0.65);
  }

  .cardgrid{display:grid; gap:10px;}""",
"""  .masteryPlate.legendary{
    color:var(--magenta);
    border-color:rgba(255,46,136,0.65);
  }

  .guideLead{
    margin:0 0 12px;
    padding:11px;
    border:1px solid rgba(47,230,224,0.35);
    border-radius:7px;
    background:rgba(47,230,224,0.05);
    color:var(--text);
  }
  .guideLead b{color:var(--cyan);}
  .guideRow{
    padding:7px 0;
    border-top:1px dashed var(--line);
    font-size:11px;
  }
  .guideRow:first-of-type{border-top:0; padding-top:0;}
  .guideRow b{color:var(--cyan);}
  .guideRow strong{color:var(--amber);}
  .guideTip{
    margin-top:8px;
    padding:8px;
    border-left:2px solid var(--purple);
    background:rgba(178,107,255,0.05);
    color:var(--dim);
    font-size:10px;
  }
  .guideOpenBtn{
    width:100%;
    border:1px solid rgba(47,230,224,0.4);
    border-radius:6px;
    background:rgba(47,230,224,0.06);
    color:var(--cyan);
    font-family:inherit;
    font-size:11px;
    letter-spacing:.5px;
    padding:10px;
    cursor:pointer;
    text-align:left;
  }
  .guideOpenBtn small{
    display:block;
    margin-top:3px;
    color:var(--dim);
    font-size:9px;
    letter-spacing:0;
  }

  .cardgrid{display:grid; gap:10px;}""",
'guide CSS'
)


# ---------- Add guide access inside the Character Sheet ----------
replace_once(
"""    <section class=\"sheetSection\">
      <h3>WEAPON INVENTORY // ${P.inventory.length}/6</h3>
      ${inventoryHtml}
    </section>
  `;
}""",
"""    <section class=\"sheetSection\">
      <h3>WEAPON INVENTORY // ${P.inventory.length}/6</h3>
      ${inventoryHtml}
    </section>

    <section class=\"sheetSection\">
      <h3>REFERENCE</h3>
      <button class=\"guideOpenBtn\" type=\"button\" onclick=\"openNightCityGuide()\">
        Getting to Know Night City
        <small>Game rules, stat meanings, combat, builds, progression, and persistence.</small>
      </button>
    </section>
  `;
}""",
'character sheet guide button'
)


# ---------- Guide content / screens ----------
guide_functions = r'''
function nightCityGuideHtml(){
  return `
    <div class="guideLead">
      <b>Cyberdoom</b> is a run-based cyberpunk roguelike. Build a merc, survive Night City, defeat the NetWatch Warden, push through Corpo Plaza, and flatline Adam Smasher before Night City flatlines you.
    </div>

    <section class="sheetSection">
      <h3>THE RUN</h3>
      <div class="guideRow"><b>Start</b> — Choose a class. At Mastery 4+, that class can also choose between its standard and alternate special ability.</div>
      <div class="guideRow"><b>Loadout Cache</b> — Before Watson, choose one of three offered unlocked relics or take <strong>+60 eddies</strong>. This does not consume a district node.</div>
      <div class="guideRow"><b>Route</b> — Watson (7 nodes) → Pacifica (8) → Blackwall Relay / NetWatch Warden → Corpo Plaza (9) → Arasaka Tower / Adam Smasher.</div>
      <div class="guideRow"><b>Nodes</b> — Districts can contain combat, events, Ripperdocs, safehouses, relic caches, Fixer contacts, and elites. Normal districts end with an elite.</div>
      <div class="guideRow"><b>Victory</b> — Defeat Adam Smasher. Reaching 0 HP ends the run unless an effect such as Second Wind saves you.</div>
    </section>

    <section class="sheetSection">
      <h3>CORE STATS</h3>
      <div class="guideRow"><b>HP</b> — Your life. Enemy damage is applied to HP after defenses. At 0 HP, you flatline.</div>
      <div class="guideRow"><b>Humanity</b> — The cost of becoming more machine. Installing cyberware reduces Humanity. At or below 25%, normal attacks have a 30% chance to enter a chrome-fueled rage, adding +25% crit chance for that attack.</div>
      <div class="guideRow"><b>Defense / DEF</b> — Flat damage reduction against normal incoming enemy attacks.</div>
      <div class="guideRow"><b>Tech / TECH</b> — Improves Tech weapon damage and powers several hacking/class abilities, especially Netrunner tools.</div>
      <div class="guideRow"><b>Cool / COOL</b> — Raises Evade chance by 1.5 percentage points per point of Cool and also powers certain class abilities.</div>
      <div class="guideRow"><b>DMG Bonus</b> — Flat bonus added to many attacks and damaging abilities.</div>
      <div class="guideRow"><b>Crit</b> — Chance for a weapon hit to deal critical damage. Weapon crit, class bonuses, relics, chrome, affinity, and mastery can modify it.</div>
      <div class="guideRow"><b>Dodge</b> — A separate passive chance to completely avoid an enemy attack.</div>
      <div class="guideRow"><b>Regen</b> — HP automatically restored after enemy turns.</div>
      <div class="guideRow"><b>CDR</b> — Cooldown reduction. Lowers the cooldown applied when you activate a special ability.</div>
      <div class="guideRow"><b>Stims</b> — Consumable combat healing. A normal stim restores 25% max HP; Medtech Patch raises that to 35%.</div>
      <div class="guideRow"><b>Heat</b> — Represents attention drawn to your run. Higher Heat strengthens certain major encounters, including the Blackwall Relay and Arasaka Tower bosses.</div>
    </section>

    <section class="sheetSection">
      <h3>COMBAT RULES</h3>
      <div class="guideRow"><b>Attack</b> — Use your equipped weapon. Multi-hit weapons attack multiple times and split enemy armor pressure across their burst.</div>
      <div class="guideRow"><b>Special Ability</b> — Your class-defining action. Using it starts its cooldown. Mastery 4 unlocks an alternate ability for each class.</div>
      <div class="guideRow"><b>Use Stim</b> — Heal, then the enemy gets its turn.</div>
      <div class="guideRow"><b>Guard</b> — Spend your turn to reduce the next incoming hit by 50%. Guardian Daemon raises this to 65%.</div>
      <div class="guideRow"><b>Evade</b> — Spend your turn preparing to avoid the next attack. Base chance is 65% + 1.5% per Cool, plus relevant relic bonuses, capped at 95%.</div>
      <div class="guideRow"><b>Switch / Drop Weapon</b> — Inventory management does not consume a combat turn. You cannot drop your final weapon.</div>
      <div class="guideRow"><b>Character Sheet / Guide</b> — Opening information screens never consumes a turn or changes combat state.</div>
      <div class="guideTip"><b>Enemy threat:</b> STREET, DANGEROUS, and LETHAL are estimates relative to your current build. CONTACT / ELITE / BOSS describes enemy rank. The combat HUD also shows armor, damage range, and active states such as BLEED, STUNNED, BERSERK, TECH, or PHASE.</div>
    </section>

    <section class="sheetSection">
      <h3>WEAPONS & CLASS AFFINITY</h3>
      <div class="guideRow"><b>Inventory</b> — You can carry up to 6 weapons. If a seventh is added, the oldest inventory weapon is automatically pushed out, so drop unwanted weapons before taking new gear.</div>
      <div class="guideRow"><b>Mutations</b> — Weapons can gain run-defining effects such as Bleed, Vampiric healing, Shock/stun, armor Shred, or extra Fragment hits.</div>
      <div class="guideRow"><b>Solo — Pistol</b> — Sidearm Doctrine: +15% weapon damage and +5% crit.</div>
      <div class="guideRow"><b>Netrunner — Monowire</b> — Neural Conduit: +2 Tech damage and +5% crit.</div>
      <div class="guideRow"><b>Chrome Junkie — Gorilla Arms</b> — Full-Force Interface: +20% weapon damage.</div>
      <div class="guideRow"><b>Samurai — Katana</b> — Blade Discipline: +15% crit.</div>
      <div class="guideRow"><b>Rockerboy — SMG</b> — Full-Auto Rhythm: +1 damage on every shot.</div>
      <div class="guideRow"><b>Nomad — Shotgun</b> — Roadside Breacher: +20% weapon damage.</div>
      <div class="guideRow"><b>Fixer — Silenced Pistol</b> — Quiet Professional: +1 damage and +10% crit.</div>
      <div class="guideTip">Affinity follows the <b>weapon type</b>, not the exact starting item. A stronger weapon of your preferred type still activates it. Mastery further specializes affinities.</div>
    </section>

    <section class="sheetSection">
      <h3>RELICS, CHROME & BOONS</h3>
      <div class="guideRow"><b>Relics</b> — Passive run modifiers. They can alter damage, healing, Guard, Evade, economy, survivability, and other systems.</div>
      <div class="guideRow"><b>Cyberware / Chrome</b> — Permanent for the current run and immediately modifies your stats, but installing it costs Humanity. Chrome is lost when the run ends.</div>
      <div class="guideRow"><b>District Boons</b> — Fixer/contact effects that shape the current district. These are temporary and are reverted when you leave that district.</div>
      <div class="guideRow"><b>Build logic</b> — Strong runs come from stacking interactions: class + preferred weapon + mutation + relics + chrome + ability + mastery bonuses.</div>
    </section>

    <section class="sheetSection">
      <h3>CURRENCIES & PERSISTENCE</h3>
      <div class="guideRow"><b>Eddies (€$)</b> — Run-only money used for weapons, chrome, stims, and other in-run purchases. Eddies do not carry into the next run.</div>
      <div class="guideRow"><b>Credits (cr)</b> — Persistent currency earned from runs. Spend it in the Fixer Network on permanent unlocks and account-wide perks.</div>
      <div class="guideRow"><b>Persistent</b> — Credits, Fixer Network unlocks/perks, class mastery kills/wins, nameplates, best district, wins, and run history.</div>
      <div class="guideRow"><b>Run-only</b> — HP, Humanity, eddies, weapons, stims, relics, chrome, Heat, and district boons.</div>
      <div class="guideRow"><b>Active run saves</b> — Meta progression is saved locally, but an active run itself is not currently resumable after closing or reloading the game.</div>
    </section>

    <section class="sheetSection">
      <h3>CLASS MASTERY</h3>
      <div class="guideRow"><b>Level 1 — Initiate</b> — 10 kills. Class-specific passive upgrade.</div>
      <div class="guideRow"><b>Level 2 — Specialist</b> — 25 kills. First class nameplate.</div>
      <div class="guideRow"><b>Level 3 — Veteran</b> — 50 kills + 1 win. Preferred-weapon affinity upgrade.</div>
      <div class="guideRow"><b>Level 4 — Elite</b> — 80 kills + 2 wins. Unlocks the alternate special ability.</div>
      <div class="guideRow"><b>Level 5 — Ace</b> — 120 kills + 3 wins. Major class-specific mechanical upgrade.</div>
      <div class="guideRow"><b>Level 6 — Legend</b> — 170 kills + 5 wins. Legendary nameplate and class capstone.</div>
      <div class="guideTip">Mastery is persistent and class-specific. It is designed to deepen class identity, not replace the choices you make during a run.</div>
    </section>

    <section class="sheetSection">
      <h3>OVERWATCH MODE</h3>
      <div class="guideRow"><b>Unlock</b> — Becomes available through the Fixer Network after you have at least one win.</div>
      <div class="guideRow"><b>Effect</b> — Tougher enemies and larger payouts, including a 1.5× Credit reward multiplier.</div>
      <div class="guideTip">Use the Character Sheet during a run whenever you want the exact current values for your stats, equipment, relics, chrome, inventory, ability, and affinity state.</div>
    </section>
  `;
}

function showNightCityGuide(){
  $('#app').classList.remove('metaShopOpen');
  log.innerHTML='';
  print('<span class="tag hack">Getting to Know Night City</span> Rules, systems, stats, and survival data for Cyberdoom.', 'sys');
  const wrap = document.createElement('div');
  wrap.innerHTML = nightCityGuideHtml();
  log.appendChild(wrap);
  log.scrollTop = 0;
  actions([{ label:'Back to title', fn:()=>showTitle() }], {single:true});
}

function openNightCityGuide(){
  if(!S.run || S.run.over) return showNightCityGuide();

  const sheet = $('#charSheet');
  $('#sheetTitle').textContent = 'Getting to Know Night City';
  $('#sheetBody').innerHTML = nightCityGuideHtml() + `
    <section class="sheetSection">
      <button class="guideOpenBtn" type="button" onclick="backToCharacterSheet()">Back to Character Sheet</button>
    </section>
  `;
  sheet.classList.add('on');
  sheet.setAttribute('aria-hidden','false');
  const panel = sheet.querySelector('.sheetPanel');
  if(panel) panel.scrollTop = 0;
}

function backToCharacterSheet(){
  renderCharacterSheet();
  const panel = document.querySelector('#charSheet .sheetPanel');
  if(panel) panel.scrollTop = 0;
}
'''

replace_once('function getThreatLevel(P, e, c){', guide_functions + '\nfunction getThreatLevel(P, e, c){', 'guide functions')


# ---------- Main menu guide entry ----------
replace_once(
"""    { label:'Class Mastery', sub:'View mastery progress', fn:()=>showMastery() },
    { label:'Run History', sub: META.log.length?`${META.log.length} recent runs`:'No runs yet', disabled: !META.log.length, fn:()=>showHistory() },""",
"""    { label:'Class Mastery', sub:'View mastery progress', fn:()=>showMastery() },
    { label:'Getting to Know Night City', sub:'Rules, stats, combat, builds, and progression', cls:'gold', fn:()=>showNightCityGuide() },
    { label:'Run History', sub: META.log.length?`${META.log.length} recent runs`:'No runs yet', disabled: !META.log.length, fn:()=>showHistory() },""",
'main menu guide entry'
)

path.write_text(text)
