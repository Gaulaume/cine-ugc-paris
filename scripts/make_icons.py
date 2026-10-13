"""Icônes de l'appli : le clap de cinéma « clapperboard » de Lucide (https://lucide.dev).

Lucide est sous licence ISC (libre, avis de licence dans docs/icons/LICENSE-lucide.txt).
Régénérer : python scripts/make_icons.py docs/icons  (nécessite playwright + chromium)
"""
import asyncio
import sys

from playwright.async_api import async_playwright

# Tracés de lucide-static 1.56.0, icons/clapperboard.svg (grille 24×24).
CLAPPERBOARD = """
  <path d="m12.296 3.464 3.02 3.956" />
  <path d="M20.2 6 3 11l-.9-2.4c-.3-1.1.3-2.2 1.3-2.5l13.5-4c1.1-.3 2.2.3 2.5 1.3z" />
  <path d="M3 11h18v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
  <path d="m6.18 5.276 3.1 3.899" />
"""
BLUE, YELLOW = "#1B2A4E", "#F2C230"  # couleurs de l'appli (bandeau et « ticket »)


def svg(maskable: bool = False) -> str:
    # Taille du pictogramme : plus petit en « maskable » (Android rogne jusqu'à un cercle).
    size = 250 if maskable else 300
    scale = size / 24
    offset = (512 - size) / 2
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  <rect width="512" height="512" fill="{BLUE}"/>
  <g transform="translate({offset} {offset + 6}) scale({scale})" fill="none" stroke="{YELLOW}"
     stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{CLAPPERBOARD}</g>
</svg>'''


async def main(out: str) -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for name, px, mask in [("icon-512", 512, False), ("icon-192", 192, False),
                               ("apple-touch-icon", 180, False), ("maskable-512", 512, True)]:
            page = await browser.new_page(viewport={"width": px, "height": px})
            await page.set_content(f'<style>html,body{{margin:0}}svg{{width:{px}px;height:{px}px;display:block}}</style>{svg(mask)}')
            await page.screenshot(path=f"{out}/{name}.png")
            await page.close()
        with open(f"{out}/icon.svg", "w") as f:
            f.write(svg())
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1]))
