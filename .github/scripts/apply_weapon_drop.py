from pathlib import Path
import re

path = Path('index.html')
text = path.read_text()


def replace_once(old, new, label):
    global text
    if old not in text:
        raise SystemExit(f'Patch target not found: {label}')
    text = text.replace(old, new, 1)


# Add drop-button styling beside the existing character-sheet inventory styles.
replace_once(
"""  .sheetEquipped{color:var(--green); font-size:9px; letter-spacing:1px;}""",
"""  .sheetEquipped{color:var(--green); font-size:9px; letter-spacing:1px;}
  .sheetWeaponRow{
    display:flex;
    align-items:flex-start;
    justify-content:space-between;
    gap:10px;
  }
  .sheetWeaponInfo{min-width:0; flex:1 1 auto;}
  .sheetDrop{
    flex:0 0 auto;
    border:1px solid rgba(255,71,87,0.45);
    border-radius:5px;
    background:rgba(255,71,87,0.06);
    color:var(--red);
    font-family:inherit;
    font-size:9px;
    letter-spacing:.8px;
    padding:6px 8px;
    cursor:pointer;
  }
  .sheetDrop:disabled{
    opacity:.28;
    cursor:default;
  }""",
'weapon drop CSS'
)


# Add the actual inventory mutation helper before the character sheet renderer.
replace_once(
"""function renderCharacterSheet(){
  if(!S.run) return;""",
"""function dropWeapon(index){
  if(!S.run || S.run.over) return;

  const P = S.run.player;
  if(!Array.isArray(P.inventory) || P.inventory.length<=1) return;

  const weapon = P.inventory[index];
  if(!weapon) return;

  const wasEquipped = weapon === P.weapon;
  P.inventory.splice(index, 1);

  if(wasEquipped){
    P.weapon = P.inventory[0];
  }

  print(
    `<span class=\"tag\">DROP</span> Left <b>${weapon.name}</b> behind.` +
    (wasEquipped ? ` <span class=\"accent\">Equipped ${P.weapon.name}.</span>` : '')
  );

  refreshStatus();
  renderCharacterSheet();
}

function renderCharacterSheet(){
  if(!S.run) return;""",
'weapon drop helper'
)


old_inventory = """  const inventoryHtml = P.inventory.length
    ? P.inventory.map((w,i)=>{
        const base = WEAPON_BASE[w.baseId];
        const equipped = w===P.weapon;
        const aff = affinityDef && w.baseId===affinityDef.baseId;
        return `<div class=\"sheetItem\">
          <b>${i+1}. ${w.name}</b> ${equipped?'<span class=\"sheetEquipped\">EQUIPPED</span>':''}
          <small>${base ? base.name : w.baseId} · ${w.dmg[0]}–${w.dmg[1]} dmg · ${Math.round(w.crit*100)}% base crit · ${w.hits||1} hit${(w.hits||1)>1?'s':''}${w.mutation?` · ${w.mutation.name}: ${w.mutation.desc}`:''}${aff?' · CLASS AFFINITY WEAPON':''}</small>
        </div>`;
      }).join('')
    : '<div class=\"sheetEmpty\">Inventory empty.</div>';"""

new_inventory = """  const inventoryHtml = P.inventory.length
    ? P.inventory.map((w,i)=>{
        const base = WEAPON_BASE[w.baseId];
        const equipped = w===P.weapon;
        const aff = affinityDef && w.baseId===affinityDef.baseId;
        const lastWeapon = P.inventory.length<=1;
        return `<div class=\"sheetItem\">
          <div class=\"sheetWeaponRow\">
            <div class=\"sheetWeaponInfo\">
              <b>${i+1}. ${w.name}</b> ${equipped?'<span class=\"sheetEquipped\">EQUIPPED</span>':''}
              <small>${base ? base.name : w.baseId} · ${w.dmg[0]}–${w.dmg[1]} dmg · ${Math.round(w.crit*100)}% base crit · ${w.hits||1} hit${(w.hits||1)>1?'s':''}${w.mutation?` · ${w.mutation.name}: ${w.mutation.desc}`:''}${aff?' · CLASS AFFINITY WEAPON':''}</small>
            </div>
            <button class=\"sheetDrop\" type=\"button\" ${lastWeapon?'disabled':''} onclick=\"dropWeapon(${i})\">DROP</button>
          </div>
        </div>`;
      }).join('')
    : '<div class=\"sheetEmpty\">Inventory empty.</div>';"""

replace_once(old_inventory, new_inventory, 'character sheet inventory drop controls')


# Also expose dropping from the combat weapon-management menu.
switch_pattern = re.compile(r"function switchWeaponMenu\(\)\{.*?\n\}\n\nfunction useStim", re.S)
if not switch_pattern.search(text):
    raise SystemExit('Patch target not found: switchWeaponMenu')

new_switch = r'''function switchWeaponMenu(){
  const P = S.run.player;
  const opts = P.inventory.map((w,i)=>({
    label:(w===P.weapon?'[Equipped] ':'')+w.name,
    sub:`${w.dmg[0]}-${w.dmg[1]} dmg, crit ${Math.round(w.crit*100)}%${w.mutation?' ⟨'+w.mutation.name+'⟩':''}`,
    fn:()=>{ P.weapon=w; print(`Switched to <b>${w.name}</b>.`); combatMenu(); }
  }));

  if(P.inventory.length>1){
    opts.push({
      label:'Drop Weapon',
      sub:'Discard a weapon from your inventory',
      cls:'danger',
      fn:()=>dropWeaponMenu()
    });
  }

  opts.push({label:'Back', fn:()=>combatMenu()});
  actions(opts);
}

function dropWeaponMenu(){
  const P = S.run.player;

  if(P.inventory.length<=1){
    print('You cannot drop your last weapon.', 'warn');
    return combatMenu();
  }

  const opts = P.inventory.map((w,i)=>({
    label:`Drop ${w.name}`,
    sub:w===P.weapon ? 'Currently equipped — another weapon will auto-equip' : 'Discard permanently for this run',
    cls:'danger',
    fn:()=>{
      dropWeapon(i);
      combatMenu();
    }
  }));

  opts.push({label:'Back', fn:()=>switchWeaponMenu()});
  actions(opts);
}

function useStim'''

text = switch_pattern.sub(new_switch, text, count=1)

path.write_text(text)
