const {chromium} = require('playwright');
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const server = http.createServer((req,res) => {
  const file=path.join(root,new URL(req.url,'http://localhost').pathname.replace(/^\//,'')||'index.html');
  if(!file.startsWith(root+path.sep)) {res.writeHead(403);return res.end();}
  const types={'.html':'text/html','.js':'text/javascript','.json':'application/json','.css':'text/css','.png':'image/png'};
  fs.readFile(file,(err,data)=>{res.writeHead(err?404:200,{'Content-Type':types[path.extname(file)]||'text/plain'});res.end(err?'Not found':data);});
});
(async()=>{
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const browser=await chromium.launch({headless:true});
  try {
    const context=await browser.newContext({viewport:{width:390,height:844}});
    const page=await context.newPage();
    const errors=[]; page.on('pageerror',e=>errors.push(e.message));
    const url=`http://127.0.0.1:${server.address().port}/`;
    await page.goto(url);
    await page.evaluate(()=>{
      for(let n=1;n<=3;n++) localStorage.setItem(slotKey(n),JSON.stringify({...defaultMeta(),credits:100*n}));
    });
    await page.reload();
    await page.locator('.card').first().click();
    const personal=await page.evaluate(()=>[1,2,3].map(n=>localStorage.getItem(slotKey(n))));
    await page.getByRole('button',{name:/Autoplay Lab/}).click();
    await page.locator('.card').first().click();
    assert.equal(await page.evaluate(()=>SLOT),'autoplay');
    await page.getByRole('button',{name:'One move',exact:true}).click();
    assert.equal(await page.evaluate(()=>S.run.starting),false);
    // One move must not schedule subsequent actions.
    const afterStep=await page.locator('#botStats').textContent();
    await page.waitForTimeout(350);
    assert.equal(await page.locator('#botStats').textContent(),afterStep);
    await page.locator('#botPanel summary').click();
    await page.selectOption('#botSpeed','250');
    await page.getByRole('button',{name:'Play',exact:true}).click();
    await page.waitForTimeout(650);
    await page.getByRole('button',{name:'Pause',exact:true}).click();
    const paused=await page.locator('#botStats').textContent();
    await page.waitForTimeout(350);
    assert.equal(await page.locator('#botStats').textContent(),paused);
    // Manual action stops an active timer before it can execute an old choice.
    await page.getByRole('button',{name:'Play',exact:true}).click();
    await page.locator('#actions button:not([disabled])').first().click();
    assert.match(await page.locator('#botStats').textContent(),/^PAUSED/);
    // Tactical check: spend a stim at low HP rather than attacking or using a cooldown.
    await page.evaluate(async()=>{
      await startRun(structuredClone(CLASSES[0]),false);
      S.run.player.hp=5;
      S.run.player.items.stims=2;
      startCombat({name:'Training enemy',hp:100,dmg:[5,5],def:1},false);
    });
    await page.getByRole('button',{name:'One move',exact:true}).click();
    assert.equal(await page.evaluate(()=>S.run.player.items.stims),1);
    assert.match(await page.locator('#botNote').textContent(),/^Use Stim/);
    // Several complete runs exercise shops, events, combat, loot and end-of-run saves.
    const results=await page.evaluate(async()=>{
      let seed=8675309;
      Math.random=()=>{seed=(Math.imul(1664525,seed)+1013904223)>>>0;return seed/4294967296;};
      const out=[];
      for(const style of ['cautious','aggressive','experimental']) {
        document.querySelector('#botStyle').value=style;
        document.querySelector('#botStyle').dispatchEvent(new Event('change'));
        for(const cls of CLASSES) {
          await startRun(structuredClone(cls),false);
          let moves=0;
          while(!S.run.over && moves<500) {
            document.querySelector('#botStep').click();
            await new Promise(r=>setTimeout(r,0));
            moves++;
          }
          if(!S.run.over) throw new Error(`Stalled ${style}/${cls.id}: ${document.querySelector('#botNote').textContent}`);
          out.push({style,cls:cls.id,moves,district:S.run.actName});
        }
      }
      return out;
    });
    assert.equal(results.length,21);
    assert.deepEqual(await page.evaluate(()=>[1,2,3].map(n=>localStorage.getItem(slotKey(n)))),personal);
    assert.equal(await page.evaluate(()=>JSON.parse(localStorage.getItem(slotKey('autoplay'))).botRecords.length),20);
    await page.evaluate(async()=>{
      await startRun(structuredClone(CLASSES[0]),false);
      S.run.act=4;S.run.actName='Arasaka Tower';
      await endRun(true);
    });
    assert.equal(await page.evaluate(()=>META.botRecords[0].won),true);
    assert.deepEqual(await page.evaluate(()=>[1,2,3].map(n=>localStorage.getItem(slotKey(n)))),personal);
    await page.screenshot({path:'/tmp/cyberdoom-autoplay-mobile.png',fullPage:true});
    // Ensure the real service worker caches all assets and serves an offline reload.
    await page.evaluate(()=>navigator.serviceWorker.ready);
    await page.reload();
    await page.waitForFunction(()=>navigator.serviceWorker.controller);
    await context.setOffline(true);
    await page.reload();
    await page.locator('.card').first().click();
    await page.getByRole('button',{name:/Autoplay Lab/}).click();
    await page.locator('.card').first().click();
    await page.getByRole('button',{name:'One move',exact:true}).click();
    assert.equal(await page.evaluate(()=>S.run.starting),false);
    assert.deepEqual(await page.evaluate(()=>[1,2,3].map(n=>localStorage.getItem(slotKey(n)))),personal);
    assert.deepEqual(errors,[]);
    console.log(JSON.stringify({passed:true,completedRuns:results.length,results,checks:['single step','timer play/pause','manual takeover','low-HP healing','all classes/styles','personal save isolation','bounded persistent records','victory record','offline reload and play','no runtime errors']},null,2));
    await browser.close();
  } finally {await browser.close();server.close();}
})().catch(error=>{console.error(error);server.close();process.exitCode=1;});
