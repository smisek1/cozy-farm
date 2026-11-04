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
| Kvalita (Space Age) | = **genetická odrůda** (lepší semínko → lepší plodina, zvíře i budova) |

## Suroviny (místo kovů)
| Vanilla | Cozy Farm | Odkud | Stav |
|---|---|---|---|
| železo | dřevo, prkna | stromy (lesní věž) | ✅ |
| měď | lněné vlákno → pavoučí hedvábí | len → přadlena | ✅ |
| kámen, cihly | vápenec → biocement | skály → trávicí komora | ✅ |
| plast | pryskyřice | dřevo → trávicí komora | ✅ |
| palivo | cukr, seno | trávicí komora, pšenice | ✅ |
| ocel | chitin | hmyzí kolonie (svlečené krunýře) | plán |
| obvody | nervová tkáň | houbová farma (mycelium) | plán |
| ropa | olej ze semen | trávicí komora | plán |

## Budovy
- **Zvířata:** kurník, stáj, ovčín (vejce, mléko, vlna, odchov). ✅
- **Zpracování:** mlýn, kuchyně. ✅
- **Trávicí komora:** živý žaludek (grafika biokomory z Gleby). ✅
- **Hmyzí kolonie:** mravenčí dílna I–II (montážky) ✅, pavoučí přadlena ✅; mravenčí dílna III a úl (složité díly) jsou v plánu.
- **Věže:** zahradní (plodiny) a lesní (stromy). ✅
- **Výzkum:** genetická laboratoř, sekvenátor DNA (grafika biolabu). ✅
- **Logistika:** kořenové pásy, tunely, rozdělovače, úponky (inserterty). ✅
- **Síť podhoubí:** houbové uzly (sloupy), fotosyntetické listy, kvasná komora, škrobová hlíza. ✅
- **Pěstované budovy** (plán): recept dá „zárodek“, po položení vyroste mladá forma, ze které za
  pár minut skript udělá dospělou budovu (`on_built_entity` → `storage` → `on_nth_tick`).
- **Houby a mycelium** (plán): houbová farma, nervová tkáň, uzly sítě podhoubí.

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
3. **CRISPR-Cas9 sada:** enzym z bakteriální kultury (plán).
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
| 4 | pěstované budovy, houbová farma, nervová tkáň, chitin | – |
| 5 | CRISPR + odrůdy (kvalita), balíček 3 | – |
| 6 | budovy na vodě, balíček 4 | – |

## Nápady na později
- Animace růstu plodin (`growth_variations` potřebuje speciální textury). Teď rostlina vypadá
  od zasazení jako dorostlá.
- Lepší grafika budov, zatím jsou to přebarvené vanilla stroje.
- Mravenčí dílna III, úl.

## Technické poznámky
- Testy běží headless: `factorio --create` (načtení prototypů) a `--benchmark` s testovacím modem.
- Zrádnosti Factoria 2.1:
  - recept má `categories = {..}`, ne `category`,
  - produkt má `independent_probability`, ne `probability`,
  - předmět má `fuel_categories = {..}`, ne `fuel_category`,
  - inserter nesmí mít emise ve zdroji energie,
  - sekce v locale se nesmí opakovat.
