// Dependency-free gameplay integration checks using a minimal DOM adapter.
// This executes the real game and bot scripts, but does not verify browser layout or a real service worker.
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const elements=new Map();
class Element {
  constructor(){this.children=[];this.classes=new Set();this.style={};this.disabled=false;this.hidden=false;this._html='';this.textContent='';this.classList={add:(...x)=>x.forEach(v=>this.classes.add(v)),remove:(...x)=>x.forEach(v=>this.classes.delete(v)),contains:x=>this.classes.has(x),toggle:(x,on)=>{on??=!this.classes.has(x);on?this.classes.add(x):this.classes.delete(x);}};}
  set id(x){this._id=x;elements.set(x,this);} get id(){return this._id;}
  set innerHTML(x){this._html=x;this.children=[];for(const m of x.matchAll(/id="([^"]+)"/g)) get(m[1]);}
  get innerHTML(){return this._html;}
  setAttribute(k,v){this[k]=v;}
  appendChild(x){this.children.push(x);return x;}
  replaceChildren(...x){this.children=x;}
  before(){}
  click(){if(!this.disabled)return this.onclick?.();}
}
const get=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id);};
const storage=new Map(),listeners={};
const document={hidden:false,createElement:()=>new Element(),querySelector:s=>get(s.replace(/^#/,'')),getElementById:get,addEventListener:(n,fn)=>{listeners[n]=fn;}};
let timer=0;const timers=new Map();
const sandbox={document,console,structuredClone,setTimeout:(fn)=>{timers.set(++timer,fn);return timer;},clearTimeout:id=>timers.delete(id),localStorage:{getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,v)},navigator:{},addEventListener(){},confirm:()=>true};
sandbox.window=sandbox;
const ctx=vm.createContext(sandbox);
const run=code=>vm.runInContext(code,ctx);
const flush=async()=>{for(let i=0;i<8;i++)await Promise.resolve();};
const step=async()=>{get('botStep').click();await flush();};
(async()=>{
  const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
  const scripts=[...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
  scripts.filter(s=>s.trim()).forEach(s=>run(s));await flush();
  run(fs.readFileSync(path.join(root,'autoplay.js'),'utf8'));
  run("for(let n=1;n<=3;n++) localStorage.setItem(slotKey(n),JSON.stringify({...defaultMeta(),credits:n*100}));");
  const personal=[1,2,3].map(n=>storage.get(`meta_v2_slot${n}`));
  await run('loadSlot(1)');await run('CyberdoomBot.enter()');
  await run('startRun(structuredClone(CLASSES[0]),false)');
  await step();assert.equal(run('S.run.starting'),false);assert.equal(timers.size,0);
  get('botPlay').click();assert.equal(timers.size,1);
  get('botPlay').click();assert.equal(timers.size,0);
  get('botPlay').click();get('actions').children.find(b=>!b.disabled).click();await flush();assert.equal(timers.size,0);
  // Backgrounding pauses with no automatic resume.
  get('botPlay').click();document.hidden=true;listeners.visibilitychange();assert.equal(timers.size,0);document.hidden=false;
  await run('startRun(structuredClone(CLASSES[0]),false); S.run.player.hp=5; S.run.player.items.stims=2; startCombat({name:"Training enemy",hp:100,dmg:[5,5],def:1},false);');
  await step();assert.equal(run('S.run.player.items.stims'),1);assert.match(get('botNote').textContent,/^Use Stim/);
  // Cooldowns, empty stim inventory, equipment switching and sheet pause.
  run('S.run.player.hp=S.run.player.maxHp; S.run.player.items.stims=0; S.run.player.ability.cdLeft=2; combatMenu();');
  await step();assert.match(get('botNote').textContent,/^Attack/);
  run('S.run.player.inventory.push({...S.run.player.weapon,name:"Test upgrade",dmg:[50,60]}); combatMenu();');
  await step();assert.match(get('botNote').textContent,/^Switch Weapon/);
  await step();assert.equal(run('S.run.player.weapon.name'),'Test upgrade');
  get('charSheet').classList.add('on');const hp=run('S.run.combat.enemy.hp');await step();assert.equal(run('S.run.combat.enemy.hp'),hp);get('charSheet').classList.remove('on');
  run('let testSeed=8675309; Math.random=()=>{testSeed=(Math.imul(1664525,testSeed)+1013904223)>>>0;return testSeed/4294967296;};');
  const results=[];
  for(const style of ['cautious','aggressive','experimental']) {
    get('botStyle').onchange({target:{value:style}});
    for(let i=0;i<run('CLASSES.length');i++) {
      await run(`startRun(structuredClone(CLASSES[${i}]),false)`);
      let moves=0;
      while(!run('S.run.over') && moves<500){await step();moves++;}
      assert.equal(run('S.run.over'),true,`Stalled ${style}/${i}: ${get('botNote').textContent}`);
      results.push({style,cls:run('S.run.player.cls'),moves,district:run('S.run.actName')});
    }
  }
  assert.equal(results.length,21);
  assert.deepEqual([1,2,3].map(n=>storage.get(`meta_v2_slot${n}`)),personal);
  assert.equal(JSON.parse(storage.get('meta_v2_slotautoplay')).botRecords.length,20);
  await run('startRun(structuredClone(CLASSES[0]),false); S.run.act=4; S.run.actName="Arasaka Tower"; endRun(true);');await flush();
  assert.equal(JSON.parse(storage.get('meta_v2_slotautoplay')).botRecords[0].won,true);
  assert.deepEqual([1,2,3].map(n=>storage.get(`meta_v2_slot${n}`)),personal);
  // Worker asset list points to files that really exist.
  const worker=fs.readFileSync(path.join(root,'service-worker.js'),'utf8');
  for(const asset of [...worker.matchAll(/'\.\/([^']*)'/g)].map(m=>m[1]))assert.ok(!asset||fs.existsSync(path.join(root,asset)),`Missing offline asset: ${asset}`);
  console.log(JSON.stringify({passed:true,completedRuns:results.length,results,checks:['single step','play/pause timer','manual takeover','background pause','low-HP healing','cooldown and disabled actions','weapon switch','sheet pause','all classes/styles','personal-save isolation','bounded persisted records','victory record','offline asset references']},null,2));
})().catch(e=>{console.error(e);process.exitCode=1;});
