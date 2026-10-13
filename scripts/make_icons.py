"""Icône originale « style Babylon » : ziggourat dorée art déco sur rouge profond.

Régénérer : python scripts/make_icons.py docs/icons  (nécessite playwright + chromium)
"""
import asyncio, math, sys
from playwright.async_api import async_playwright

def svg(maskable=False):
    # Rayons du soleil art déco, depuis le sommet de la ziggourat.
    cx, cy = 256, 236
    rays = []
    for i in range(18):
        a0 = math.radians(180 + i * 10); a1 = math.radians(180 + i * 10 + 5)
        r = 300
        rays.append(f'<path d="M{cx},{cy} L{cx+r*math.cos(a0):.1f},{cy+r*math.sin(a0):.1f} L{cx+r*math.cos(a1):.1f},{cy+r*math.sin(a1):.1f}Z"/>')
    tiers = [(320, 356, 44), (252, 314, 42), (188, 274, 40), (128, 238, 36), (72, 206, 32)]
    steps = "".join(f'<rect x="{256-w/2}" y="{y}" width="{w}" height="{h-4}"/>' for w, y, h in tiers)
    # Lignes verticales décoratives (colonnes) sur les deux étages du bas.
    cols = "".join(f'<rect x="{x}" y="{364}" width="7" height="30" fill="#5A0D12"/>' for x in range(114, 400, 26))
    frame = ""
    k = 0.8 if maskable else 1.0
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  <defs>
    <radialGradient id="bg" cx="50%" cy="46%" r="72%">
      <stop offset="0" stop-color="#A3161F"/><stop offset=".55" stop-color="#5C0A10"/><stop offset="1" stop-color="#1A0306"/>
    </radialGradient>
    <radialGradient id="rayfade" gradientUnits="userSpaceOnUse" cx="256" cy="236" r="300">
      <stop offset=".3" stop-color="#F2C76A" stop-opacity=".35"/><stop offset="1" stop-color="#F2C76A" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="gold" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#FBE3A0"/><stop offset=".5" stop-color="#E0AE4A"/><stop offset="1" stop-color="#A9761F"/>
    </linearGradient>
  </defs>
  <rect width="512" height="512" fill="url(#bg)"/>
  <g transform="translate(256 256) scale({k}) translate(-256 -256)">
    <g fill="url(#rayfade)">{"".join(rays)}</g>
    <circle cx="{cx}" cy="{cy}" r="110" fill="none" stroke="url(#gold)" stroke-width="6"/>
    <circle cx="{cx}" cy="{cy}" r="92" fill="none" stroke="url(#gold)" stroke-width="2.5" opacity=".8"/>
    <g fill="url(#gold)">{steps}</g>
    {cols}
    <rect x="80" y="404" width="352" height="6" rx="3" fill="url(#gold)"/>
  </g>{frame}
</svg>'''

async def main(out):
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for name, size, mask in [("icon-512", 512, False), ("icon-192", 192, False),
                                 ("apple-touch-icon", 180, False), ("maskable-512", 512, True)]:
            pg = await b.new_page(viewport={"width": size, "height": size})
            await pg.set_content(f'<style>html,body{{margin:0}}svg{{width:{size}px;height:{size}px;display:block}}</style>{svg(mask)}')
            await pg.screenshot(path=f"{out}/{name}.png", omit_background=False)
            await pg.close()
        open(f"{out}/icon.svg", "w").write(svg(False))
        await b.close()
asyncio.run(main(sys.argv[1]))
