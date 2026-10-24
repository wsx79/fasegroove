# FaseGroove — modulo comune

Codice condiviso da Fase Groove Piano, Drums, Guitar e Arranger.

Ogni plugin resta un prodotto indipendente: questo codice viene incluso in ciascuno al momento della compilazione, non si installa a parte.

L'elenco delle modifiche da portare qui è in [MODULO_COMUNE.md](MODULO_COMUNE.md).

## Come si usa

- Il codice comune è in `common/` (Updater, Localisation + `CommonTranslations.inc`, Branding, FamilyTheme, FamilySoundProfiles, CircleOfFifths, LinkFile, MidiExport, aiuti per i test). Ogni prodotto lo compila dalla sua copia `ThirdParty/fasegroove-common/`, quindi la CI di ogni repo non ha bisogno di questo.
- Ciò che cambia tra i prodotti sta in `Source/Product.cpp` di ciascuno: `FaseGroove::product()` (nome, repo, prefisso degli asset, wordmark, icona), `Branding::appName/tagline/sourceUrl` e le traduzioni proprie (`Source/Translations.inc`).
- Dopo una modifica in `common/`: `scripts/sync.sh` (tutti i repo vicini, oppure `scripts/sync.sh ../fasegroovedrums`), poi compilare e provare ogni prodotto. `scripts/check.sh` elenca le copie non allineate (esce con 1 se ce n'è una).
- Non modificare `ThirdParty/fasegroove-common/` nei prodotti: la prossima sincronizzazione la sovrascrive.
