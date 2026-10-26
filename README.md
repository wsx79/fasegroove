# FaseGroove — modulo comune

Codice condiviso da Fase Groove Piano, Drums, Guitar, Lead e Arranger.

Ogni plugin resta un prodotto indipendente: questo codice viene incluso in ciascuno al momento della compilazione, non si installa a parte.

L'elenco delle modifiche da portare qui è in [MODULO_COMUNE.md](MODULO_COMUNE.md).

## Come si usa

- Il codice comune è in `common/` (Updater, Localisation + `CommonTranslations.inc`, Branding, FamilyTheme, FamilySoundProfiles, CircleOfFifths, LinkFile, MidiExport, aiuti per i test). Ogni prodotto lo compila dalla sua copia `ThirdParty/fasegroove-common/`, quindi la CI di ogni repo non ha bisogno di questo.
- Ciò che cambia tra i prodotti sta in `Source/Product.cpp` di ciascuno: `FaseGroove::product()` (nome, repo, prefisso degli asset, wordmark, icona), `Branding::appName/tagline/sourceUrl` e le traduzioni proprie (`Source/Translations.inc`).
- Dopo una modifica in `common/`: `scripts/sync.sh` (tutti i repo vicini, oppure `scripts/sync.sh ../fasegroovedrums`), poi compilare e provare ogni prodotto. `scripts/check.sh` elenca le copie non allineate (esce con 1 se ce n'è una).
- Non modificare `ThirdParty/fasegroove-common/` nei prodotti: la prossima sincronizzazione la sovrascrive.

## Provenienza e controlli automatici

Prima di sincronizzare, commetti le modifiche a `common/`. `scripts/sync.sh` include
anche Lead e registra `ThirdParty/fasegroove-common.lock.json` in ogni prodotto:
SHA della repo canonica e SHA-256 di tutti i file, con LF/CRLF equivalenti.

`python3 ThirdParty/fasegroove-common/VerifyModule.py` verifica la copia offline.
Con `--canonical /percorso/fasegroove` verifica anche il contenuto del checkout
canonico, che deve essere allo SHA registrato. La CI dei prodotti usa quella
revisione precisa, mantenendo le build autonome dalla main remota corrente.

`python3 ThirdParty/fasegroove-common/CheckTranslations.py` rifiuta chiavi ripetute
nei cataloghi del prodotto; gli override intenzionali di `CommonTranslations.inc`
restano supportati. `python3 tests/test_tools.py` prova drift, file mancanti/aggiunti,
CRLF, revisione errata, lock alterato e sincronizzazione predefinita di Lead.
