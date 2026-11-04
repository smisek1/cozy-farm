# Cozy Farm – koncept

Živý dokument se záměrem modu. Aktualizuje se s každou fází, aby myšlenka nezůstala jen v hlavě.

## Myšlenka
Odpočinkové farmaření ve Factoriu, kde se všechno dá zautomatizovat. Svět je **solarpunk**
(příjemná zelená budoucnost, rostlinné technologie, mycelium, slunce) a **všechno je živé,
včetně budov**. Kovy, uhlí, ropa ani uran nejsou potřeba.

## Rozhodnutí
| Téma | Rozhodnutí |
|---|---|
| Atmosféra | solarpunk |
| Energie | kombinace: malé budovy **jí** (cukr, seno), velké budou na **síti podhoubí** |
| Výzkum | **sekvenování DNA → CRISPR-Cas9 → syntetický genom** |
| Zkáza (spoilage) | ne, jídlo se nekazí |
| Voda | jen pozdě: budovy, které **stojí přímo na vodě** |
| Továrny | hmyzí kolonie, trávicí komory, pěstované budovy, houby a mycelium |
| Space Age (planety, rakety) | zatím neřešit |
| Kvalita (Space Age) | **nepoužívá se** (technologie kvality jsou skryté) |

## Suroviny (místo kovů)
| Vanilla | Cozy Farm | Odkud | Stav |
|---|---|---|---|
| železo | dřevo, prkna | stromy (lesní věž) | ✅ |
| měď | lněné vlákno → pavoučí hedvábí | len → přadlena | ✅ |
| kámen, cihly | vápenec → biocement | skály → trávicí komora | ✅ |
| plast | pryskyřice | dřevo → trávicí komora | ✅ |
| palivo | cukr, seno | trávicí komora, pšenice | ✅ |
| ocel | chitin | mravenci chovají brouky (mravenčí dílna) | ✅ |
| obvody | nervová tkáň | mycelium (houbová farma) + hedvábí | ✅ |
| ropa | olej ze semen | trávicí komora | plán |

## Budovy
- **Zvířata:** kurník, stáj, ovčín (vejce, mléko, vlna, odchov). ✅
- **Zpracování:** mlýn, kuchyně. ✅
- **Trávicí komora:** živý žaludek (grafika biokomory z Gleby). ✅
- **Hmyzí kolonie:** mravenčí dílna I–III (montážky) ✅, pavoučí přadlena ✅; úl (složité díly) je v plánu.
- **Věže:** zahradní (plodiny) a lesní (stromy). ✅
- **Výzkum:** genetická laboratoř, sekvenátor DNA (grafika biolabu). ✅
- **Logistika:** kořenové pásy, tunely, rozdělovače, úponky (inserterty). ✅
- **Síť podhoubí:** houbové uzly (sloupy), fotosyntetické listy, kvasná komora, škrobová hlíza. ✅
- **Bioroboti:** úl (roboport), včely dělnice (logistické), čmeláci stavitelé (stavební), plástve
  (logistické truhly). ✅
- **Pěstované budovy:** ✅ Recept dá „zárodek“, a když ho zasadíš, za 1–3 minuty vyroste
  v budovu (nad zárodkem jsou procenta). Vytěžená budova vrátí zárodek. Pěstují se trávicí komora,
  mravenčí dílny, přadlena, houbová farma, kvasná komora a sekvenátor. Kurník, stáj, ovčín, mlýn a
  kuchyně se pořád staví normálně. Seznam je v `scripts/grown_list.lua`.
- **Houby a mycelium:** houbová farma (mycelium ze dřeva a sena) ✅, nervová tkáň ✅.

## Energie
- **Malé budovy jí:** burner s `fuel_categories = {"cozy-food"}`, slot s ikonou jídla. Krmí se
  ručně nebo inserterem. ✅
- **Síť podhoubí:** elektrická síť přejmenovaná na mycelium. ✅
  - Energii vyrábějí **fotosyntetické listy** (solár) a **kvasná komora** (pálí cukr nebo seno, 300 kW).
  - Uchovává ji **škrobová hlíza** (akumulátor).
  - Rozvádějí ji **houbové uzly** a velké houbové uzly (sloupy).
  - Na síti běží velké budovy: sekvenátor, mravenčí dílna II, zahradní a lesní věž.

## Výzkum
1. **Vzorek DNA:** mrkev, vejce a lněné vlákno (i ručně). ✅
2. **Sekvence genomu:** vzorek DNA, hedvábí a cukr (mravenčí dílna). ✅
3. **CRISPR-Cas9 sada:** bakteriální kultura, sekvence genomu a nervová tkáň. Odemyká bioroboty. ✅
4. **Syntetický genom:** pozdní hra, budovy na vodě (plán).

Výzkum odemyká nové druhy, budovy a vlastnosti (rychlejší růst, větší výnos).

## Voda (pozdní hra, plán)
Lotosový reaktor (energie), rákosový filtr a řasová farma (olej, cukr) stojí přímo na vodě.
Technicky jde o `tile_buildability_rules` s `required_tiles = {layers = {water_tile = true}}`.

## Fáze
| # | Obsah | Verze |
|---|---|---|
| 0 | plodiny, zvířata, kuchyně, zahradní věž | 0.1.0 ✅ |
| 1 | svět bez kovů, nové suroviny, trávicí komora, živé budovy jí, kořenová logistika | 0.2.0 ✅ |
| 2 | sekvenování DNA (balíčky 1–2), sekvenátor, mravenčí dílna I–II, pavoučí přadlena, strom technologií | 0.3.0 ✅ |
| 3 | síť podhoubí: listy, kvasná komora, hlíza, houbové uzly | 0.4.0 ✅ |
| 4 | pěstované budovy, houbová farma, nervová tkáň, chitin, mravenčí dílna III | 0.5.0 ✅ |
| 5 | CRISPR-Cas9 (balíček 3), bioroboti: úl, včely dělnice, čmeláci stavitelé, plástve | 0.6.0 ✅ |
| 6 | budovy na vodě, balíček 4 | – |

## Nápady na později
- Animace růstu plodin (`growth_variations` potřebuje speciální textury). Teď rostlina vypadá
  od zasazení jako dorostlá.
- Lepší grafika budov, zatím jsou to přebarvené vanilla stroje.
- Úl (složité díly).
- Pěstování přes blueprinty: roboti zatím staví budovu rovnou dospělou (jako materiál použijí zárodek).
- Zárodek by mohl potřebovat zalévání nebo hnojivo, aby rostl rychleji.

## Technické poznámky
- Testy běží headless: `factorio --create` (načtení prototypů) a `--benchmark` s testovacím modem.
- Zrádnosti Factoria 2.1:
  - recept má `categories = {..}`, ne `category`,
  - produkt má `independent_probability`, ne `probability`,
  - předmět má `fuel_categories = {..}`, ne `fuel_category`,
  - inserter nesmí mít emise ve zdroji energie,
  - sekce v locale se nesmí opakovat.
