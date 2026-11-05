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
| ropa | rostlinný olej | lněná semínka nebo řasy → trávicí komora | ✅ |
| vápenec (obnovitelný) | vápenec z rákosu | rákosový filtr na vodě | ✅ |

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
- **Budovy na vodě:** řasová farma (řasy ze slunce), rákosový filtr (vápenec a cukr z vody), lotosový
  reaktor. Stojí jen na vodě, i jejich zárodky se sází na vodu. ✅

## Energie
- **Malé budovy jí:** burner s `fuel_categories = {"cozy-food"}`, slot s ikonou jídla. Krmí se
  ručně nebo inserterem. ✅
- **Síť podhoubí:** elektrická síť přejmenovaná na mycelium. ✅
  - Energii vyrábějí **fotosyntetické listy** (solár), **kvasná komora** (pálí cukr nebo seno, 300 kW)
    a **lotosový reaktor** na vodě (pálí jídlo, nejlépe rostlinný olej, 1,5 MW).
  - Uchovává ji **škrobová hlíza** (akumulátor).
  - Rozvádějí ji **houbové uzly** a velké houbové uzly (sloupy).
  - Na síti běží velké budovy: sekvenátor, mravenčí dílna II a III, zahradní a lesní věž, řasová farma
    a rákosový filtr.

## Výzkum
1. **Vzorek DNA:** mrkev, vejce a lněné vlákno (i ručně). ✅
2. **Sekvence genomu:** vzorek DNA, hedvábí a cukr (mravenčí dílna). ✅
3. **CRISPR-Cas9 sada:** bakteriální kultura, sekvence genomu a nervová tkáň. Odemyká bioroboty. ✅
4. **Syntetický genom:** CRISPR sada, řasy, rostlinný olej a nervová tkáň (mravenčí dílna). Odemyká
   lotosový reaktor a syntetické enzymy (+20 % produktivity trávicí komory). ✅

Výzkum odemyká nové druhy, budovy a vlastnosti (rychlejší růst, větší výnos).

## Voda (pozdní hra) ✅
Lotosový reaktor (energie), rákosový filtr (vápenec, cukr) a řasová farma (řasy → olej a cukr) stojí přímo na vodě.
- Technicky: kolizní maska jako offshore pumpa (`object`, `train`, `is_object`, `is_lower_object`, bez vrstev
  vody) a `tile_buildability_rules` s `required_tiles = {layers = {water_tile = true}}` přes celou budovu.
- Zárodek přebírá masku i pravidla od vzrostlé budovy (`prototypes/growth.lua`), takže se sází taky na vodu.
- Recepty řasové farmy a rákosového filtru nemají vstupy, berou si jen vodu a slunce (a energii ze sítě).
- **Proč rákosový filtr dělá vápenec:** skály jsou jediný zdroj vápence a časem dojdou. Filtr je obnovitelný zdroj.
- **Proč místo rychlejšího růstu enzymy:** Factorio nemá technologický efekt na rychlost růstu rostlin,
  `change-recipe-productivity` na receptech trávicí komory ano.

## Fáze
| # | Obsah | Verze |
|---|---|---|
| 0 | plodiny, zvířata, kuchyně, zahradní věž | 0.1.0 ✅ |
| 1 | svět bez kovů, nové suroviny, trávicí komora, živé budovy jí, kořenová logistika | 0.2.0 ✅ |
| 2 | sekvenování DNA (balíčky 1–2), sekvenátor, mravenčí dílna I–II, pavoučí přadlena, strom technologií | 0.3.0 ✅ |
| 3 | síť podhoubí: listy, kvasná komora, hlíza, houbové uzly | 0.4.0 ✅ |
| 4 | pěstované budovy, houbová farma, nervová tkáň, chitin, mravenčí dílna III | 0.5.0 ✅ |
| 5 | CRISPR-Cas9 (balíček 3), bioroboti: úl, včely dělnice, čmeláci stavitelé, plástve | 0.6.0 ✅ |
| 6 | rostlinný olej, budovy na vodě, syntetický genom (balíček 4), syntetické enzymy | 0.7.0 ✅ |
| 7 | ? (viz nápady) | – |

## Nápady na později
- Rychlejší růst plodin přes výzkum (jen skriptem, např. kratší `growth_ticks` u nově zasazených rostlin).
- Vlastní grafika budov na vodě (teď přebarvená montážka, chemička a jaderný reaktor).
- Animace růstu plodin (`growth_variations` potřebuje speciální textury). Teď rostlina vypadá
  od zasazení jako dorostlá.
- Lepší grafika budov, zatím jsou to přebarvené vanilla stroje.
- Úl (složité díly).
- Pěstování přes blueprinty: roboti zatím staví budovu rovnou dospělou (jako materiál použijí zárodek).
- Zárodek by mohl potřebovat zalévání nebo hnojivo, aby rostl rychleji.

## Technické poznámky
- Testy běží headless: `factorio --create` (načtení prototypů) a `--benchmark` s testovacím modem.
  Vlastní `config.ini` s `write-data` mimo `~/.factorio`, aby test nepřepisoval logy hry.
  `surface.create_entity` nekontroluje technologie: recept v testu funguje až po `technologies[..].researched = true`.
- Zrádnosti Factoria 2.1:
  - recept má `categories = {..}`, ne `category`,
  - produkt má `independent_probability`, ne `probability`,
  - předmět má `fuel_categories = {..}`, ne `fuel_category`,
  - inserter nesmí mít emise ve zdroji energie,
  - sekce v locale se nesmí opakovat.
