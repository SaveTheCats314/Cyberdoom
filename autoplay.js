/* Cyberdoom Autoplay: local rules, visible choices, no network or personal-save writes. */
(() => {
  'use strict';
  const TEST_SLOT = 'autoplay';
  const bot = {
    running:false, busy:false, timer:null, choices:[], revision:0,
    style:'cautious', delay:900, steps:0, decisions:[], repeat:0, signature:'', note:'Choose a class, then press Play.',
  };
  const panel = document.createElement('section');
  panel.id = 'botPanel'; panel.hidden = true;
  panel.setAttribute('aria-label', 'Autoplay Lab');
  panel.innerHTML = `
    <details><summary>AUTOPLAY LAB · separate test save</summary>
      <div class="botControls">
        <label>Style <select id="botStyle"><option value="cautious">Cautious</option><option value="aggressive">Aggressive</option><option value="experimental">Experimental</option></select></label>
        <label>Speed <select id="botSpeed"><option value="1800">Slow</option><option value="900" selected>Normal</option><option value="250">Fast</option></select></label>
        <button id="botExit" type="button">Exit lab</button>
      </div>
      <p class="botHelp">Choose your class normally. Play runs one test at a time. Completed results persist here; refreshing ends an unfinished run. Your three personal saves are separate.</p>
      <div id="botHistory"></div>
    </details>
    <div class="botControls"><button id="botPlay" type="button">Play</button><button id="botStep" type="button">One move</button></div>
    <p id="botNote" role="status"></p><p id="botStats"></p>`;
  document.querySelector('#log').before(panel);
  const el = id => document.getElementById(id);
  const inLab = () => SLOT === TEST_SLOT && !panel.hidden;
  const live = () => inLab() && S.run && !S.run.over;
  const text = s => String(s || '').replace(/<[^>]*>/g, '');
  const mean = a => (a[0]+a[1])/2;
  function render() {
    el('botNote').textContent = bot.note;
    el('botPlay').textContent = bot.running ? 'Pause' : 'Play';
    el('botPlay').disabled = !live();
    el('botStep').disabled = !live() || bot.running || bot.busy;
    if(inLab()) {
      const records = META.botRecords || [];
      el('botStats').textContent = `${bot.running?'PLAYING':'PAUSED'} · ${bot.steps} moves · Test record: ${META.runsWon} wins / ${META.botLosses||0} losses · ${META.runsStarted} starts`;
      el('botHistory').replaceChildren(...records.slice(0,5).map(r => {
        const p = document.createElement('p');
        p.textContent = `${r.won?'WON':'DIED'} · ${r.className} · ${r.district} · ${r.style} · ${r.steps} moves`;
        return p;
      }));
    }
  }
  function pause(note) {
    clearTimeout(bot.timer); bot.timer = null; bot.running = false;
    if(note && inLab()) bot.note = note;
    render();
  }
  function schedule() {
    clearTimeout(bot.timer); bot.timer = null;
    if(bot.running && live() && !bot.busy) bot.timer = setTimeout(() => step(), bot.delay);
  }
  function observe(choices) {
    bot.choices = choices.slice(); bot.revision++;
    render(); schedule();
  }
  async function enter() {
    if(S.run && !S.run.over) return; // Never transfer an active personal run.
    pause();
    await loadSlot(TEST_SLOT);
    panel.hidden = false;
    bot.note = 'Choose a class below, then press Play. All rewards stay in the test save.';
    showClassSelect(); render();
  }
  function leave() { pause(); panel.hidden = true; bot.choices = []; bot.revision++; }
  function beginRun() {
    pause(); bot.steps=0; bot.decisions=[]; bot.repeat=0; bot.signature='';
    if(inLab()) bot.note = 'Run ready — press Play, or One move to inspect each decision.';
  }
  function finishRun(won) {
    if(!inLab()) return;
    pause(won ? 'Run won. Choose New run to test another build.' : 'Run ended. Choose New run to try again.');
    const P = S.run.player;
    if(!won) META.botLosses=(META.botLosses||0)+1;
    META.botRecords = [{won, className:P.className, district:S.run.actName,
      style:bot.style, steps:bot.steps, date:new Date().toISOString(),
      weapon:P.weapon.name, relics:P.relics.map(r=>r.name), classCores:(P.classRelics||[]).map(r=>r.name), cyberware:P.cyberware.map(c=>c.name),
      decisions:bot.decisions.slice(-120)}, ...(META.botRecords||[])].slice(0,20);
    // endRun saves this together with the normal test-slot progression.
  }
  function weaponDamage(P, w, armor=0, minimum=false) {
    const affinity = getClassWeaponAffinity({...P, weapon:w});
    let base = (minimum?w.dmg[0]:mean(w.dmg)) + P.dmgBonus + (w.tech?P.tech:0);
    if(P._ballisticMastery && w.tag==='ballistic') base += P._ballisticMastery;
    if(affinity) base = (base+(affinity.flatDamage||0)+(affinity.techBonus||0))*(affinity.damageMult||1);
    const hits = (w.hits||1)+(w.mutation?.id==='fragment'?1:0);
    const crit = minimum ? 0 : clamp(w.crit+P.critBonus+(affinity?.critBonus||0),0,1);
    return Math.max(1,base*(1+crit*.8)-(hits>1?Math.ceil(armor/hits):armor))*hits;
  }
  function abilityDamage(P, c) {
    const w=mean(P.weapon.dmg), d=mean(P.dmgRange), bonus=P.dmgBonus, armor=c.enemy.def;
    switch(P.ability.id) {
      case 'solo_overwatch': return Math.max(1,Math.round((d+bonus)*1.6)-Math.max(0,armor-2));
      case 'solo_killshot': return weaponDamage(P,P.weapon,0)*2;
      case 'netrunner_quickhack': return 8.5+P.tech+bonus+Math.max(1,Math.round(c.enemy.maxHp*.08));
      case 'netrunner_daemon': return 4.5+P.tech+bonus+Math.max(1,Math.round(c.enemy.maxHp*.05))+Math.max(2,Math.round(P.tech*.7));
      case 'chrome_berserk': return Math.max(1,d+Math.round((1-P.hp/P.maxHp)*10)+bonus-armor);
      case 'chrome_groundpound': return Math.max(1,w+bonus+P.def+Math.round((1-P.hp/P.maxHp)*6)-armor);
      case 'samurai_blade_dance': return Math.max(1,d+bonus-armor)*2+Math.max(1,(d+bonus-armor)*(.6+(P._samuraiMastery ? 0.2 : 0)));
      case 'samurai_iaijutsu': return Math.max(1,(w+bonus)*(P._samuraiMastery?3.4:3)-Math.floor(armor*.5));
      case 'rocker_feedback': return Math.max(1,5.5+P.cool+bonus+(P._rockerEncore?2:0)-Math.floor(armor*.5));
      case 'nomad_roadwarrior': return Math.max(1,(w+bonus+P.def)*1.3-armor);
      case 'fixer_connections': return Math.max(1,6.5+P.tech+P.cool+bonus);
      case 'fixer_professional': return Math.max(1,5+P.tech+P.cool+bonus);
      default: return 0;
    }
  }
  function combatChoice(available, P) {
    const c=S.run.combat, e=c.enemy;
    const find = label => available.find(a=>a.label===label);
    const choose = (a,why) => a ? {a,why} : null;
    const attack=find('Attack'), stim=find('Use Stim');
    const worstHit = c.enemyStunned ? 0 : Math.max(0,Math.round((e.dmg[1]-Math.floor(P.def))*(e.berserk&&e.hp<e.maxHp*.4?1.5:1)));
    const attackMean=weaponDamage(P,P.weapon,e.def);
    if(weaponDamage(P,P.weapon,e.def,true)>=e.hp) return choose(attack,'The current weapon can finish the enemy without spending a stim.');
    const healAmount=Math.round(P.maxHp*(hasRelic(P,'medtech_patch')?.35:.25));
    const healAt=bot.style==='aggressive'?.35:.6;
    if(stim && P.maxHp-P.hp>=healAmount && (P.hp/P.maxHp<=healAt || P.hp<=worstHit))
      return choose(stim,`Healing before more damage; enemy can hit for about ${worstHit}.`);
    const best=P.inventory.reduce((a,w)=>weaponDamage(P,w,e.def)>weaponDamage(P,a,e.def)?w:a,P.weapon);
    if(best!==P.weapon && weaponDamage(P,best,e.def)>attackMean*1.05)
      return choose(find('Switch Weapon'),'A carried weapon has better estimated damage against this armor.');
    const ability=available.find(a=>a.label===P.ability.name);
    if(ability) {
      const id=P.ability.id;
      const humCost=id==='chrome_groundpound'?Math.max(1,5-(P._chromeAbilityDiscount||0)):Math.max(1,3-(P._chromeAbilityDiscount||0));
      const chromeSafe=(!id.startsWith('chrome_') || P.humanity-humCost>P.maxHumanity*.25) && (!P._netBlackwallTap || P.humanity-4>P.maxHumanity*.25);
      if(id==='rocker_rally' && !c.rallyTurns && e.hp>attackMean*2 && P.hp>worstHit*2)
        return choose(ability,'A longer fight makes the damage and defense buff useful.');
      if(id==='nomad_scavenger' && !c.guaranteedLoot && P.hp>worstHit*3 && bot.style!=='cautious')
        return choose(ability,'Health is sufficient to spend a turn securing bonus loot.');
      if(chromeSafe && abilityDamage(P,c)>attackMean*1.05)
        return choose(ability,'The ready ability offers more estimated damage than a normal attack.');
    }
    if(c.enemyBleed>=e.hp && !c.enemyStunned)
      return choose(find('Guard'),'Bleed can finish the enemy this turn; guard as a precaution.');
    return choose(attack,'Attack to make progress while conserving resources.');
  }
  function scoreChoice(a,P) {
    const label=text(a.label), sub=text(a.sub), t=`${label} ${sub}`.toLowerCase();
    const cautious=bot.style==='cautious', missing=1-P.hp/P.maxHp;
    let score=10, why='Choose a useful available reward.';
    if(a.bot?.kind==='equip') return {score:weaponDamage(P,a.bot.weapon,S.run.combat?.enemy.def||0), why:'Equip the weapon with the best estimated damage for this enemy.'};
    if(a.bot?.kind==='shop') {
      const {item, itemKind, price}=a.bot;
      if(itemKind==='weapon') {
        const current=Math.max(...P.inventory.map(w=>weaponDamage(P,w)));
        const gain=weaponDamage(P,item)/Math.max(1,current)-1;
        return {score:gain>.15?25+gain*20-price*.08:-20,why:'Buy a meaningful weapon upgrade.'};
      }
      if(itemKind==='stim') return {score:P.items.stims<(cautious?3:2)?30+missing*30-price*.1:-20,why:'Keep a reserve of healing stims.'};
      if(itemKind==='cyber') {
        if(P.cyberware.some(c=>c.id===item.id) || P.humanity-item.hum<P.maxHumanity*(cautious?.4:.28))
          return {score:-50,why:'Preserve humanity and avoid duplicate chrome.'};
        return {score:24-price*.08,why:'Install an affordable upgrade while retaining a humanity reserve.'};
      }
    }
    if(/^(back|drop|\[equipped\])/.test(t)) return {score:-100,why:'Avoid unneeded menu changes.'};
    if(/^(leave|skip|walk away|keep moving|not interested|ghost the ping|kill the terminal|stay invisible|keep your current|close the case)/.test(t))
      return {score:0,why:'Move on without taking an unnecessary risk.'};
    if(/^reroll/.test(t)) return {score:-5,why:'No worthwhile purchase; conserve time and move on.'};
    if(/heal|restore.*hp|rest with|run with family/.test(t)) {score+=missing*90-10; why='Recover missing health.';}
    if(/meditate|\+\d+%? (max )?humanity|humanity regen/.test(t)) {score+=(1-P.humanity/P.maxHumanity)*50;why='Restore humanity before it becomes critical.';}
    if(/defense|regen|dodge|heal.*combat/.test(t)) score+=cautious?16:8;
    if(/damage|crit|weapon/.test(t)) score+=cautious?8:16;
    if(/stim/.test(t)) score+=P.items.stims<2?20:0;
    if(/eddies|relic/.test(t)) score+=8;
    if(/tech/.test(t) && (P.weapon.tech || P.cls==='netrunner')) score+=8;
    if(/random|risky|risk|tracer|chance|heat/.test(t)) {score-=cautious?22:7;why='Weigh the displayed reward against its risk.';}
    const humanity=t.match(/-(\d+) humanity/);
    if(humanity && P.humanity-Number(humanity[1])<P.maxHumanity*(cautious?.4:.28)) score-=100;
    if(/lose.*hp|pay in blood/.test(t)) score-=cautious?35:18;
    if(a.bot?.kind==='relic') { score+=15; why='Take a relic that supports this build.'; }
    if(bot.style==='experimental') score+=Math.random()*20;
    return {score,why};
  }
  function decide() {
    const available=bot.choices.filter(a=>!a.disabled);
    if(!available.length) return null;
    const P=S.run.player;
    if(available.some(a=>a.label==='Attack') && S.run.combat?.enemy.hp>0) return combatChoice(available,P);
    const ranked=available.map(a=>({a,...scoreChoice(a,P)})).sort((a,b)=>b.score-a.score);
    return ranked[0];
  }
  async function step() {
    if(!live() || bot.busy || document.hidden) return pause('Paused — return to the game and press Play.');
    if(document.querySelector('#charSheet')?.classList.contains('on')) return pause('Close the character sheet before continuing.');
    const choice=decide();
    if(!choice) return pause('No available action — take manual control to continue.');
    if(bot.steps>=2000) return pause('Reached the 2,000-move safety limit for this run.');
    const sig=JSON.stringify([S.run.act,S.run.node,S.run.player.hp,S.run.player.eddies,S.run.combat?.enemy.hp,choice.a.label]);
    bot.repeat=sig===bot.signature?bot.repeat+1:0; bot.signature=sig;
    if(bot.repeat>=4) return pause('Repeated action without progress — take manual control.');
    clearTimeout(bot.timer); bot.timer=null;
    const revision=bot.revision;
    bot.busy=true; bot.steps++;
    bot.note=`${text(choice.a.label)} — ${choice.why}`;
    bot.decisions.push({move:bot.steps,action:text(choice.a.label),reason:choice.why,hp:S.run.player.hp,district:S.run.actName});
    if(bot.decisions.length>120) bot.decisions.shift();
    render();
    try {
      // Only execute a current, enabled action exposed by the game's normal menu.
      if(revision===bot.revision && !choice.a.disabled) await choice.a.fn();
      if(live() && revision===bot.revision) pause('Action did not open a new choice — take manual control.');
    } catch(error) {
      console.error('Autoplay action failed',error);
      pause('Autoplay hit an error and stopped. You can take manual control.');
    } finally { bot.busy=false; render(); schedule(); }
  }
  el('botPlay').onclick = () => {
    if(bot.running) return pause('Paused — play manually or press Play to resume.');
    if(!live()) return;
    bot.running=true; bot.note='Autoplay running.'; render(); schedule();
  };
  el('botStep').onclick = () => { pause(); step(); };
  el('botExit').onclick = () => {
    if(live() && !window.confirm('End this unfinished test run and return to your personal save files?')) return;
    S.run=null; SLOT=null; META=null; showSaveSelect();
  };
  el('botStyle').onchange = event => {bot.style=event.target.value;};
  el('botSpeed').onchange = event => {bot.delay=Number(event.target.value);schedule();};
  document.addEventListener('visibilitychange',()=>{if(document.hidden && bot.running) pause('Paused while the game is in the background. Press Play to continue.');});
  window.addEventListener('pagehide',()=>pause());
  window.CyberdoomBot = {enter,leave,observe,pause,beginRun,finishRun};
  render();
})();
