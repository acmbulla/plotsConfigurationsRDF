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

La verifica usa ROOT sintetici pesati e controlla proiezione dei conteggi,
sottrazione con SF dipendenti da eta, unione SF/DF, propagazione degli errori,
tutti i32 confronti per2flavor×2WP×2varianti, assenza di linee tra punti, scelta EWK-only, mascheramento dei denominatori invalidi e
rifiuto di mappe mancanti o prive di Sumw2. Per creare le fixture serve anche
`boost_histogram`, che non è richiesto dallo script di confronto.
