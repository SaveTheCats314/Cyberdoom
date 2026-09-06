from pathlib import Path

path = Path('index.html')
text = path.read_text()

def replace_once(old, new, label):
    global text
    if old not in text:
        raise SystemExit(f'Patch target not found: {label}')
    text = text.replace(old, new, 1)

replace_once(
'''  <div class="enemyTop">
    <span id="enemyName">HOSTILE</span>
    <span id="enemyType">CONTACT</span>
  </div>''',
'''  <div class="enemyTop">
    <span id="enemyName">HOSTILE</span>
    <div class="enemyBadges">
      <span id="enemyThreat">STREET</span>
      <span id="enemyType">CONTACT</span>
    </div>
  </div>''',
'enemy top markup'
)

css_anchor = '''#enemyType{
  flex:0 0 auto;
  color:var(--dim);
  border:1px solid var(--line);
  border-radius:3px;
  padding:1px 5px;
  font-size:9px;
  letter-spacing:1px;
}
'''

css_insert = '''.enemyBadges{
  display:flex;
  align-items:center;
  justify-content:flex-end;
  gap:5px;
  flex:0 0 auto;
}

#enemyThreat{
  flex:0 0 auto;
  border:1px solid var(--line);
  border-radius:3px;
  padding:1px 5px;
  font-size:9px;
  font-weight:bold;
  letter-spacing:1px;
}

#enemyThreat.street{
  color:var(--green);
  border-color:rgba(61,255,154,0.45);
}

#enemyThreat.dangerous{
  color:var(--amber);
  border-color:rgba(255,176,32,0.55);
}

#enemyThreat.lethal{
  color:var(--red);
  border-color:rgba(255,71,87,0.7);
  box-shadow:0 0 8px rgba(255,71,87,0.12);
}

''' + css_anchor
replace_once(css_anchor, css_insert, 'enemy badge CSS')

marker = '''  function refreshEnemyStatus(){
'''
helper = '''function getThreatLevel(P, e, c){
  if(e.boss || c.boss){
    return { label:'LETHAL', cls:'lethal' };
  }

  const avgDamage = (e.dmg[0] + e.dmg[1]) / 2;
  const expectedHit = Math.max(0, avgDamage - Math.floor(P.def));
  const hitPressure = expectedHit / Math.max(1, P.maxHp);
  const hpPressure = e.maxHp / Math.max(1, P.maxHp);

  let score =
    (hitPressure * 2.5) +
    (hpPressure * 0.35) +
    (e.def * 0.05);

  if(e.elite) score += 0.5;
  if(e.berserk) score += 0.2;

  if(score >= 1.15){
    return { label:'LETHAL', cls:'lethal' };
  }

  if(score >= 0.5){
    return { label:'DANGEROUS', cls:'dangerous' };
  }

  return { label:'STREET', cls:'street' };
}

function refreshEnemyStatus(){
'''
replace_once(marker, helper, 'refreshEnemyStatus marker')

js_anchor = '''  $('#enemyName').textContent = e.name.toUpperCase();

  const type = $('#enemyType');
'''
js_insert = '''  $('#enemyName').textContent = e.name.toUpperCase();

  const threat = getThreatLevel(S.run.player, e, c);
  const threatEl = $('#enemyThreat');
  threatEl.textContent = threat.label;
  threatEl.className = threat.cls;

  const type = $('#enemyType');
'''
replace_once(js_anchor, js_insert, 'threat refresh logic')

tech_anchor = '''  const effects = [];

  if(c.enemyBleed > 0)
'''
tech_insert = '''  const effects = [];

  if(e.tech)
    effects.push('TECH');

  if(c.enemyBleed > 0)
'''
replace_once(tech_anchor, tech_insert, 'tech enemy indicator')

path.write_text(text)
