# Cozy Farm

Odpočinkový solarpunkový mod pro **Factorio 2.1 + Space Age**, ve kterém je všechno živé.
Žádné kovy, uhlí ani ropa. Pěstuješ plodiny, chováš zvířata a krmíš živé budovy.
Postupně to všechno zautomatizuješ.

*A relaxing solarpunk overhaul for Factorio 2.1 + Space Age where everything is alive: no metals,
coal or oil – grow crops, raise animals, feed living buildings and automate it all.*

## Co je hotové (0.6.0)
- **Ornice a 6 plodin:** mrkev, brambory, pšenice, rajčata, dýně a len. Rostou jen v ornici.
  Sklízíš je ručně, nebo přes **zahradní věž**.
- **Zvířata:** kurník, stáj a ovčín (vejce, mléko, vlna), krmení senem, odchov.
- **Zpracování:** mlýn, kuchyně (chléb, sýr, polévka, dýňový koláč) a farmářský vědecký balíček.
- **Svět bez kovů:** rudy nejsou, skály dávají vápenec. Materiály jsou prkna, lněné vlákno,
  pryskyřice, biocement a cukr.
- **Trávicí komora:** živý žaludek, který rozkládá dřevo, plodiny a vápenec.
- **Živé budovy jedí** cukr nebo seno.
- **Logistika:** kořenové pásy, úponky (inserterty) a lesní věž.
- **Výzkum = sekvenování DNA:** vzorek DNA a sekvence genomu, genetická laboratoř a sekvenátor DNA,
  vlastní strom technologií.
- **Hmyzí továrny:** mravenčí dílna I–III (montážky) a pavoučí přadlena (hedvábí).
- **Pěstované budovy:** větší budovy se nestaví, zasadíš zárodek a budova vyroste.
- **Houby:** houbová farma (mycelium), nervová tkáň místo obvodů, chitin místo oceli.
- **CRISPR-Cas9** (3. balíček) a **bioroboti:** úl, včely dělnice, čmeláci stavitelé, plástve.
- **Síť podhoubí:** houbové uzly, fotosyntetické listy, kvasná komora (cukr → energie) a škrobová
  hlíza. Napájí velké budovy.

## Plán
syntetický genom (4. balíček),
pěstované budovy, genetické odrůdy (kvalita) a budovy na vodě.

Celý záměr, rozhodnutí a plán fází jsou v [KONCEPT.md](KONCEPT.md).

## Struktura
- `cozy-farm/`: samotný mod
- `tools/make_graphics.py`: generátor ikon a spritů (čistý Python, bez PIL):
  `python3 tools/make_graphics.py cozy-farm`
- `tools/build.sh`: zabalí mod do `~/.factorio/mods/cozy-farm_<verze>.zip`

**Pozor:** mod předělává celou hru (skrývá vanilla recepty a technologie). Hraj ho v samostatné
sadě modů, ne v rozehrané hře s jinými overhauly.
