(()=>{const $=s=>document.querySelector(s),S=n=>(+n).toFixed(4)+' SOL',sh=a=>a.slice(0,4)+'…'+a.slice(-4),
tx=s=>`<a href="https://solscan.io/tx/${s}" rel="noopener">tx</a>`,ac=(a,l)=>`<a class="mono" href="https://solscan.io/account/${a}" rel="noopener">${l||sh(a)}</a>`,
dt=t=>new Date(t*1000).toLocaleDateString(undefined,{year:'numeric',month:'short',day:'numeric'}),esc=s=>String(s).replace(/[<>&"]/g,c=>({'<':'&lt;','>':'&gt;','&':'&amp;','"':'&quot;'}[c]));
document.querySelectorAll('nav button').forEach(b=>b.onclick=()=>{document.querySelectorAll('nav button').forEach(x=>x.classList.toggle('on',x===b));document.querySelectorAll('main section').forEach(s=>s.hidden=s.id!==b.dataset.t);history.replaceState(0,'','#'+b.dataset.t)});
fetch('data/data.json',{cache:'no-cache'}).then(r=>r.json()).then(D=>{
const T=D.treasury,tot=D.feesTotalAll,agg={};D.inflows.forEach(f=>f.shares.forEach(s=>agg[s.w]=(agg[s.w]||0)+s.sol));
const split=Object.entries(agg).sort((a,b)=>b[1]-a[1]);const last=D.batches[D.batches.length-1];
$('#upd').textContent='Data updated '+new Date(D.updated*1000).toLocaleString()+'.';
$('#ov').innerHTML=`<div class="grid">
<div class="card"><b>${S(D.feesTotalAll)}</b><span>creator fees split by Pump.fun so far</span></div>
<div class="card"><b>${S(D.feesIn)}</b><span>of that sent to the Rewards Treasury</span></div>
<div class="card"><b>${S(D.paidOut)}</b><span>paid out to ${D.recipients} wallets in ${D.payoutCount} payouts</span></div>
<div class="card"><b>${S(D.balance)}</b><span>in the treasury right now</span></div></div>
<p class="note">How it works (per <a href="https://www.thecatmoons.com" rel="noopener">thecatmoons.com</a>): Pump.fun creator fees for $MOONCAT are shared between fee wallets. The Rewards Treasury share builds up and is paid out each lunar cycle (~29.5 days): 33% to token lockers (Streamflow locks) and 21% to the top 5 creators. The rest carries over. This page only shows what the chain shows.</p>
<div class="grid"><div class="card"><span>Last payout cycle</span><b>${last?S(last.total):'–'}</b><span>${last?dt(last.start)+' · '+last.count+' payouts':''}</span></div>
<div class="card"><span>Token</span><div>${ac(D.mint,sh(D.mint))}</div><span>Market cap ≈ $${D.market.fdv?Math.round(D.market.fdv).toLocaleString():'–'}</span></div>
<div class="card"><span>Rewards Treasury</span><div>${ac(T)}</div><span>${D.otherIn>0?S(D.otherIn)+' extra came in from donations/top-ups':''}</span></div></div>`;
$('#fl').innerHTML=`<h2>Where the creator fees go</h2><p class="muted">Every Pump.fun <i>DistributeCreatorFees</i> transaction for $MOONCAT, split across the fee-share wallets.</p>
<table><tr><th>Wallet</th><th class="r">SOL received</th><th class="r">Share</th></tr>${split.map(([w,v])=>`<tr><td>${ac(w,w===T?'Rewards Treasury':sh(w))}</td><td class="r">${v.toFixed(4)}</td><td class="r">${(100*v/tot).toFixed(1)}%</td></tr><tr><td colspan="3"><div class="bar" data-w="${(100*v/tot).toFixed(1)}"></div></td></tr>`).join('')}</table>
<h3>Fee distributions</h3><table><tr><th>Date</th><th class="r">Total</th><th class="r">To treasury</th><th></th></tr>${D.inflows.slice().reverse().map(f=>`<tr><td>${dt(f.ts)}</td><td class="r">${f.total.toFixed(4)}</td><td class="r">${f.sol.toFixed(4)}</td><td>${tx(f.sig)}</td></tr>`).join('')}</table>`;
document.querySelectorAll('.bar').forEach(b=>b.style.width=b.dataset.w+'%');
$('#cy').innerHTML=`<h2>Payout cycles</h2><p class="muted">SOL sent out of the Rewards Treasury, grouped into batches by date.</p>`+D.batches.slice().reverse().map(b=>`<details><summary>Cycle batch ${b.n} · ${dt(b.start)} · ${S(b.total)} to ${b.count} wallets</summary><table><tr><th>Wallet</th><th class="r">SOL</th><th></th></tr>${b.items.slice().sort((a,c)=>c.sol-a.sol).map(p=>`<tr><td>${ac(p.to)}</td><td class="r">${p.sol.toFixed(4)}</td><td>${tx(p.sig)}</td></tr>`).join('')}</table></details>`).join('');
$('#lead').innerHTML=`<table><tr><th>#</th><th>Wallet</th><th class="r">SOL</th><th class="r hide-sm">Payouts</th></tr>${D.leaders.slice(0,25).map((l,i)=>`<tr><td>${i+1}</td><td>${ac(l.w)}</td><td class="r">${l.sol.toFixed(4)}</td><td class="r hide-sm">${l.count}</td></tr>`).join('')}</table>`;
const chk=a=>{a=a.trim();if(!/^[1-9A-HJ-NP-Za-km-z]{32,44}$/.test(a)){$('#wr').innerHTML='<p>That does not look like a Solana address.</p>';return}
const ps=D.batches.flatMap(b=>b.items.filter(p=>p.to===a).map(p=>({...p,n:b.n})));
$('#wr').innerHTML=ps.length?`<div class="card"><b>${S(ps.reduce((s,p)=>s+p.sol,0))}</b><span>received in ${ps.length} payouts</span></div><table><tr><th>Cycle</th><th>Date</th><th class="r">SOL</th><th></th></tr>${ps.map(p=>`<tr><td>${p.n}</td><td>${dt(p.ts)}</td><td class="r">${p.sol.toFixed(4)}</td><td>${tx(p.sig)}</td></tr>`).join('')}</table>`:`<p>No treasury payouts found for <span class="mono">${esc(a)}</span> yet.</p>`};
$('#wf').onsubmit=e=>{e.preventDefault();chk($('#wi').value)};
const go=()=>{const h=location.hash.slice(1);if(h)document.querySelector(`nav button[data-t="${h}"]`)?.click()};go();addEventListener('hashchange',go);
}).catch(()=>{$('#ov').innerHTML='<p>Could not load data. Try again in a minute.</p>'})})();
