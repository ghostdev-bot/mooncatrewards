import asyncio
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path='/usr/bin/google-chrome')
    for name,vp,mob in [('desktop',{'width':1366,'height':900},False),('mobile',{'width':390,'height':844},True)]:
      c=await b.new_context(viewport=vp,is_mobile=mob,device_scale_factor=2 if mob else 1);pg=await c.new_page();errs=[]
      pg.on('console',lambda m: m.type=='error' and errs.append(m.text));pg.on('pageerror',lambda e: errs.append(str(e)))
      for t in ['ov','fl','cy','wa']:
        await pg.goto('https://mooncatrewards.surge.sh/#'+t);await pg.wait_for_timeout(2500)
        if t=='wa': await pg.fill('#wi','88m73AvPrXFMa8u1Nzm31ytez3uBGedZwHeSNNSqyBFX');await pg.click('#wf button');await pg.wait_for_timeout(500)
        await pg.screenshot(path=f'shots/{name}-{t}.png')
      print(name,'errors',errs); await c.close()
asyncio.run(main())
