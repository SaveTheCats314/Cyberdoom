from pathlib import Path

path = Path('index.html')
text = path.read_text()


def replace_once(old, new, label):
    global text
    if old not in text:
        raise SystemExit(f'Patch target not found: {label}')
    text = text.replace(old, new, 1)


# Fixer Network gets its own scroll layout instead of letting a large action list overflow the app.
replace_once(
"""  #actions.single{grid-template-columns:1fr;}
  button.act{""",
"""  #actions.single{grid-template-columns:1fr;}

  #app.metaShopOpen #log{
    flex:0 0 auto;
    max-height:24dvh;
    overflow-y:auto;
  }

  #app.metaShopOpen #actions{
    flex:1 1 auto;
    min-height:0;
    overflow-y:auto;
    -webkit-overflow-scrolling:touch;
    align-content:start;
    padding-bottom:calc(10px + env(safe-area-inset-bottom));
  }

  button.act{""",
'Fixer Network scroll CSS'
)


# Enable scroll mode only for the Fixer Network screen.
replace_once(
"""function showMetaShop(){
  log.innerHTML='';""",
"""function showMetaShop(){
  $('#app').classList.add('metaShopOpen');
  log.innerHTML='';""",
'Fixer Network mode on'
)

# Make sure leaving meta shop clears the special layout.
replace_once(
"""function showTitle(){
  S.run=null; setStatus(false);""",
"""function showTitle(){
  $('#app').classList.remove('metaShopOpen');
  S.run=null; setStatus(false);""",
'title clears Fixer Network mode'
)

replace_once(
"""async function showSaveSelect(){
  log.innerHTML=''; actionsEl.innerHTML=''; setStatus(false);""",
"""async function showSaveSelect(){
  $('#app').classList.remove('metaShopOpen');
  log.innerHTML=''; actionsEl.innerHTML=''; setStatus(false);""",
'save select clears Fixer Network mode'
)

replace_once(
"""function showClassSelect(hardMode){
  hardMode = !!hardMode;""",
"""function showClassSelect(hardMode){
  $('#app').classList.remove('metaShopOpen');
  hardMode = !!hardMode;""",
'class select clears Fixer Network mode'
)


# Add Back to class selection while preserving the Overwatch toggle.
replace_once(
"""  if(overwatchUnlocked){
    actions([{ label: hardMode?'Turn Overwatch Mode OFF':'Turn Overwatch Mode ON', cls:hardMode?'':'danger', fn:()=>showClassSelect(!hardMode) }], {single:true});
  } else {
    actionsEl.innerHTML='';
  }
}""",
"""  if(overwatchUnlocked){
    actions([
      { label: hardMode?'Turn Overwatch Mode OFF':'Turn Overwatch Mode ON', cls:hardMode?'':'danger', fn:()=>showClassSelect(!hardMode) },
      { label:'Back', fn:()=>showTitle() }
    ]);
  } else {
    actions([{ label:'Back', fn:()=>showTitle() }], {single:true});
  }
}""",
'class selection Back button'
)

path.write_text(text)
