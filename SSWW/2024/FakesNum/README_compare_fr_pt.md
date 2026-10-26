# FR vs pT integrata su eta

Script standalone per i ROOT prodotti da `SSWW/2024/FakesNum/measureFakeRate.py`.
Dipendenze: Python3, numpy, uproot e matplotlib; non richiede PyROOT.

```sh
python compare_fr_pt.py \
  --input /percorso/FakeRateMeasured/2024 \
  --out confronti_FR_pt
```

`--input` può indicare anche la cartella principale con più anni, una sola WP,
oppure un URL `root://host//percorso`. Per la ricerca remota serve `xrdfs` nel
PATH e l'autenticazione del proprio ambiente; lo script non modifica i file di input.

Per ogni flavor e WP trovati vengono prodotti **quattro confronti per ciascuna variante**, PNG e PDF (punti con barre di errore, senza linee tra i punti):

1. Inclusive: 1lep vs 2lep/primo leptone vs 2lep/secondo leptone.
2. 1lep: inclusive vs bjet vs bveto.
3. 2lep/primo leptone: inclusive vs bjet vs bveto.
4. 2lep/secondo leptone: inclusive vs bjet vs bveto.

Per default vengono prodotte **entrambe** le varianti, in file distinti:

- `*_EWK.png/.pdf`: dati meno prompt MC, senza SF DY;
- `*_EWKcorr.png/.pdf`: dati meno prompt MC con SF DY.

Sono quindi otto grafici PNG/PDF per flavor/WP. `index.html` li raccoglie;
`curves_EWK.csv/.json` e `curves_EWKcorr.csv/.json` conservano separatamente
valori, errori e ingredienti integrati. `manifest.json` indica le varianti.

## Bin di molteplicità di jet

Se l'input contiene anche le mappe jet-binnate (`measureFakeRate.py --jetcat`,
nomi con suffisso `_j0`, `_j1`, `_j2`), ogni categoria b guadagna un confronto
in più: la sua curva inclusiva nei jet contro i suoi bin di jet, cioè
`<caso>_<bcat>_jetbins_<variante>.png/.pdf`. Con le tre categorie b e i tre
casi sono nove grafici per variante, in aggiunta ai quattro di sopra.

Oltre a questo, i tre casi di leptone vengono confrontati **dentro ogni bin di
jet**: `inclusive_1lep_vs_2lep_<jcat>`, cioè lo stesso confronto del punto 1
ma a molteplicità di jet fissata, sempre b-inclusivo.

`--bcat` limita le categorie b da elaborare. Per una misura fatta con
`measureFakeRate.py --bcat incl` si passa `--bcat incl`, così le mappe bveto e
btag assenti non vengono riportate come buchi e il confronto
inclusive/bjet/bveto, che avrebbe una sola curva, non viene disegnato.

Un confronto in cui non esiste **nessuna** delle curve richieste non viene
prodotto affatto: una figura di soli `[mancante]` dice meno della sua assenza.

Quelle mappe sono facoltative. Se non ci sono, non viene segnalato nulla,
perché lo split è opzionale al momento della misura; se però ne esiste solo
una parte -- per esempio `ee_lep1_incl_j1` senza `emu_lep1_incl_j1`, che
verrebbero sommati -- la mancanza viene riportata come per gli altri casi, e
senza `--allow-missing` lo script si ferma. `--jet-cat` restringe le categorie
da includere; il default sono tutte quelle trovate.

Nei CSV la colonna si chiama `cat` (prima `bcat`) e per queste curve contiene
la categoria b più il bin di jet, p.es. `bveto_j1`.

## Confronto con le mappe vecchie (jet di rinculo)

Con `--legacy-input` si aggiungono le mappe vecchie, quelle binnate nella
soglia del jet di rinculo che `fake_rate_reader_class.cc` legge davvero:

```sh
python compare_fr_pt.py \
  --input   ../../utils/data/FakeRate/2024_v15_pt_measured \
  --legacy-input ../../utils/data/FakeRate/2024_v15_pt \
  --out confronti_FR_pt
```

Per ciascuna variante si aggiungono:

5. `legacy_jet_scan`: tutte le soglie `*FR_jet<thr>.root` trovate, piu la
   curva nuova 2lep/primo leptone/bveto come riferimento.
6. `legacy_vs_measured`: la sola soglia che il peso usa (`--legacy-nominal-jet`,
   default 30 GeV) contro 1lep/bveto, 2lep/lep0/bveto e 2lep/lep1/bveto.
7. `prompt_rate_eta<k>`: il prompt rate vecchio (`ElePR.root` / `MuonPR.root`)
   contro quello nuovo di primo e secondo leptone, una figura per bin |eta|
   del file vecchio. Le curve finiscono in `prompt_rate_*.csv/.json`.
8. `legacy_vs_measured_<jcat>`: lo stesso confronto del punto 6 dentro un
   singolo bin di jet, una figura per categoria trovata. La mappa vecchia non
   è binnata nella molteplicità di jet — è binnata nel pT del jet di rinculo —
   quindi la sua curva è identica in tutte queste figure; quello che cambia è
   la fetta della misura nuova contro cui viene messa. Serve proprio a vedere
   quale bin di jet il singolo numero vecchio stia descrivendo.

9. `legacy_vs_measured_<jcat>_<caso>`: lo stesso del punto 8 ma **una figura
   per caso di leptone**, cioè la mappa vecchia contro una sola curva nuova.
   Con tre casi più la vecchia su un asse solo, la vecchia resta una riga
   piatta molto in basso e i tre casi si sovrappongono; separati, ognuno si
   legge contro di lei.

Nei confronti dei bin di jet (punto 8 della sezione precedente e i `_jetbins`)
la curva jet-inclusiva compare solo **se esiste**: `--jetcat` senza `incl`
misura i soli bin, e pretenderla segnerebbe ogni figura come parziale per una
curva che non era stata chiesta.

`--legacy-bcat` sceglie la categoria b delle curve nuove nei punti 5, 6, 8 e 9
(default `bveto`). `--legacy-jet` limita le soglie sovrapposte. Se per una WP le mappe vecchie
non ci sono, i confronti legacy vengono saltati e segnalati in stdout e in
`manifest.json` (`legacy_missing`): non e un errore, perche le WP prodotte
nelle due campagne non coincidono.

Tre differenze di contenuto da tenere presenti leggendo le figure:

- **Binning.** Le mappe vecchie arrivano a 50 GeV in pT e hanno due bin in
  **|eta|** (0, 1.479, 2.5); le nuove arrivano a 100 GeV e hanno dieci bin in
  eta **con segno**. Le curve sono disegnate ognuna sul proprio binning, non
  ribinnate.
- **Integrazione in eta.** Nelle mappe vecchie il numeratore e il denominatore
  sono salvati senza Sumw2, mentre la mappa del rate ha i suoi errori. Quindi
  si integra con `FR = Σ num / Σ den` e si propaga
  `Var(FR) = Σ (den_j/Σden)² Var(rate_j)`, cioe con i denominatori trattati
  come pesi fissi. Non e la stessa formula usata per le mappe nuove, dove i
  conteggi tight/rest hanno le loro varianze.
- **Varianti.** La produzione vecchia ha una sola versione sottratta, quindi
  `EWK` ed `EWKcorr` leggono lo stesso `FR_pT_eta_EWKcorr`; `raw` legge
  `FR_pT_eta`. Il PR vecchio non ha varianti del tutto.

Sul prompt rate c'e un dettaglio che conta per il peso: entrambe le macro
leggono `h_Ele_signal_pt_eta_bin` / `h_Muon_signal_pt_eta_bin`, e nei file
nuovi quell'istogramma e il PR **non sottratto** (`PR_pT_eta`), non
`PR_pT_eta_EWKcorr`. Per questo nelle figure del prompt rate compaiono anche
le due curve nuove senza sottrazione, etichettate come quelle che il peso usa
davvero. I bin |eta| vecchi non hanno un bordo corrispondente nel binning
nuovo (1.479 contro 1.5): il bordo viene agganciato al piu vicino e la banda
effettivamente usata e scritta nel titolo, nel JSON (`eta_band`) e nel
manifest.

## Definizioni

- **2lep** unisce i canali same-sign SF e DF, per flavor e posizione del
  leptone. `lep0` è il primo leptone della collezione selezionata, `lep1` il
  secondo; non sono il primo/secondo lepton *di quel flavor*.
- **inclusive** è la categoria `incl`; **bjet** corrisponde a `btag` nei nomi
  del producer; **bveto** a `bveto`. Sono lette separatamente, senza assumere
  che bjet e bveto siano complementari. Nel producer di riferimento, btag
  richiede almeno un jet b centrale sopra30GeV e bveto nessuno sopra20GeV.
  Il default è UParTAK4B loose, soglia 0.0246, con |eta| < 2.5; è modificabile
  in produzione con `--btag-wp` (medium 0.1272, tight 0.4648). Il compare non
  applica una nuova WP: legge quella delle mappe prodotte.
- EWK usa `h_tight_data`, `h_rest_data`, `h_tight_mc`, `h_rest_mc`.
- EWKcorr usa gli stessi dati e `h_tight_mc_SF`, `h_rest_mc_SF`: i fattori
  DY del producer sono già applicati per bin2D. Le due versioni non vengono
  sovrapposte nello stesso grafico e non si sovrascrivono.
- Si sommano **contenuti e varianze** nelle eta visibili, poi nei canali SF/DF
  disgiunti. Non si media la mappa FR e non si moltiplicano i conteggi per la
  larghezza dei bin eta. I dati pT oltre gli estremi seguono il folding già
  effettuato dal producer.

Con `T = tight_data − tight_promptMC` e
`R = rest_data − rest_promptMC`, dopo l'integrazione:

```text
FR = T / (T + R)
Var(FR) = [R² Var(T) + T² Var(R)] / (T + R)⁴
```

Tight e rest sono disgiunti; la covarianza fra numeratore e denominatore è
così trattata correttamente. Gli errori sono statistici, con i Sumw2 salvati
dal producer; i fattori SF sono trattati come fissi, come nei suoi ROOT.
Non si attribuiscono errori indipendenti a ratio o chi2 tra curve sovrapposte:
inclusive/bjet/bveto e primo/secondo leptone possono condividere eventi.

Denominatori non positivi: FR non definita, mascherata nei plot e vuota nei
CSV. FR negative o sopra1 dopo sottrazione: conservate, segnalate nel JSON e
cerchiate in rosso; nessun clipping. Si richiedono binning compatibili e
Sumw2 espliciti. Una mappa mancante non viene interpretata come zero.

## Opzioni

```sh
# Solo elettroni e una WP
python compare_fr_pt.py --input MAPPE --out CONFRONTI --flavor ele --wp NOME_WP

# Solo il canale SS di stesso flavor per le curve2lep
python compare_fr_pt.py --input MAPPE --two-lepton-channels sf

# Solo EWK, senza correzione SF DY
python compare_fr_pt.py --input MAPPE --variant ewk

# Solo EWKcorr (il nome CLI "corrected" resta valido)
python compare_fr_pt.py --input MAPPE --variant corrected

# Entrambi, default; oppure dati senza sottrazione
python compare_fr_pt.py --input MAPPE --variant both
python compare_fr_pt.py --input MAPPE --variant raw
```

Per default tutte le mappe necessarie devono esistere. `--allow-missing`
consente esplicitamente grafici parziali, indicandoli: se manca un componente
SF/DF, l'intera curva combinata viene omessa, senza cambiarne la definizione.

## Controllo del producer per piu WP

Nel `measureFakeRate.py` locale esaminato, i nomi delle mappe e le chiavi
dell'accumulatore `('map', name, part, source, moment)` non includono la WP.
Se più WP dello stesso flavor sono elaborate nella stessa invocazione, le
mappe si sovrascrivono nell'accumulatore. Per confrontare WP realmente
distinte servono produzioni con una sola WP per flavor per invocazione,
oppure una correzione delle chiavi del producer. Questo script non può
ricostruire una WP già persa nei ROOT. Il producer non è stato modificato.

## Verifica

```sh
python check_compare_fr_pt.py
```

La verifica usa ROOT sintetici pesati e controlla, oltre ai confronti legacy
(integrazione con i denominatori come pesi, bande |eta| agganciate, prompt
rate vecchio contro nuovo, mappe vecchie assenti segnalate e non fatali),
proiezione dei conteggi,
sottrazione con SF dipendenti da eta, unione SF/DF, propagazione degli errori,
tutti i32 confronti per2flavor×2WP×2varianti, assenza di linee tra punti, scelta EWK-only, mascheramento dei denominatori invalidi e
rifiuto di mappe mancanti o prive di Sumw2. Per creare le fixture serve anche
`boost_histogram`, che non è richiesto dallo script di confronto.
