# Modulo comune (fasegroove-common): cose da fare più avanti

Fonti: report-condiviso.md + le voci condivise di report-piano.md (P), report-drums.md (D) e report-guitar.md (G).
Repo: piano = fasegroovepiano, drums = fasegroovedrums, guitar = fasegrooveguitar. Ordine: beneficio/rischio decrescente.

1. **Updater** (condiviso 1, 9; P11, P14; D9; G8)
   - Cosa: un solo `Updater.{h,cpp}` con `struct ProductInfo { repo, assetPrefix, productName }` passato al `Checker`; togliere `isBusy()` (`Updater.h:80`, nessun chiamante in nessun repo).
   - File: `Source/Updater.h`, `Source/Updater.cpp` in tutti e tre (~27 righe di differenza: URL, asset, User-Agent, nome di cartella e thread).
   - Note/rischi: rischio basso. Il ramo 2.x->0.x (`Updater.cpp:440-442`) c'è solo in piano: nel modulo comune va tenuto come opzione di ProductInfo finché ci sono utenti piano su 2.x (P14, da verificare). Provare l'aggiornamento su tutte e tre le piattaforme.

2. **Localisation** (condiviso 4; P5, P2; D11; G11)
   - Cosa: un solo modulo con tabella comune + `Translations.inc` per prodotto; piano passa a `bindText/bindTip/bindItems` ed elimina `applyLanguage` (~190 righe). Nel modulo: `bind()` senza `erase/remove_if` a ogni chiamata (pulizia solo in `refreshBindings`, senza copiare il vettore); `setting()/tipsEnabled()/setSetting()` con un `PropertiesFile` unico e pigro (oggi piano rilegge il `.settings` a ogni chiamata).
   - File: piano `Source/Localisation.cpp:11-870, 884-966` + `PluginEditor.cpp:5565-5756`; drums e guitar `Source/Localisation.{h,cpp}` (cambia solo il nome dell'app, righe 38-39 e 78) + `Translations.inc`.
   - Note/rischi: rischio medio. Testi in comune 315 (drums/guitar) e 163 (piano/drums): unire senza perdere traduzioni specifiche; in piano ogni controllo va legato con `bind*` (controllare tutte le lingue a schermo). Il `PropertiesFile` deve ricaricarsi quando un'altra istanza scrive.

3. **Widget dell'editor** (condiviso 2)
   - Cosa: IconButton, Knob, ParamCombo, DragTile e UpdateOverlay nel modulo, parametrizzati da un piccolo trait (numero di lane, colori, nomi, prefisso `fgd/fgg`, chiave `fgdShown/fggShown`); poi i metodi identici dell'editor (applyTips, toggleFullScreen, enterMiniMode, undo/redo, showPresetsMenu, saveMidiFile…).
   - File: drums `PluginEditor.cpp:87-339` ≈ guitar `86-338`, `PluginEditor.h`; UpdateOverlay anche in piano.
   - Note/rischi: rischio medio. Tenere le chiavi di salvataggio di ogni prodotto (non far ricomparire i suggerimenti già visti). I widget quasi identici (VelocityView, GrooveBrowser, MixerView…) vengono dopo, solo se il trait resta semplice.

4. **Processor: export MIDI, preset/groove, analisi audio** (condiviso 3)
   - Cosa: funzioni libere o base CRTP per writeMidiFileSafely, createMidiClip, writeMidiClip, get/setStateInformation, loadPreset, setTemplate, linkFile, previewPlay/Stop/ToStart, songArrangementParts, resetSong; DSP dei template (filterBand/findHits).
   - File: `Source/PluginProcessor.cpp` (es. writeMidiFileSafely drums 1709-1721 / guitar 1473-1485; filterBand/findHits drums 2470-2552 ≈ guitar 2271-2350); piano per gli helper identici.
   - Note/rischi: rischio medio. Lo stato salvato (get/setStateInformation, preset, groove) deve restare compatibile byte per byte: test di caricamento di progetti/preset vecchi in tutti e tre.

5. **LINK** (condiviso 5; P8; D5; G5)
   - Cosa: una classe `LinkClient` comune (lettura/scrittura di `Link.xml`, updateLink, localLinkState) che controlla data di modifica e dimensione prima di `loadFileAsString()`, e mette in `linkSeenText` il testo appena scritto. In piano anche `readGuitarLead`; in guitar `writeLead` resta ogni 2 s (heartbeat).
   - File: piano `PluginProcessor.cpp:2951-3053`; drums `1984-2062` (circa); guitar `1791-1887`.
   - Note/rischi: rischio medio, protocollo condiviso: provare con 3 istanze. Attenzione: la data di modifica ha risoluzione di 1-2 s su alcuni file system (HFS+, FAT); due scritture nello stesso secondo con la stessa dimensione (es. bpm 120 -> 121) non verrebbero viste: tenere anche una rilettura completa periodica. Già fatto in drums: solo `linkSeenText = xml.toString()` dopo la scrittura (niente rilettura).

6. **Branding** (condiviso 6; P1; D1; G1)
   - Cosa: un solo `Branding.{h,cpp}` con icona e nome come parametri, e cache del Drawable dell'icona (e dei Path del wordmark, ricalcolati solo se cambia la dimensione).
   - File: `Source/Branding.{h,cpp}` in tutti e tre (`drawFullLogo` 62-69).
   - Note/rischi: rischio basso. Già fatto in drums: cache dell'icona con un singleton `DeletedAtShutdown` + `clipRegionIntersects` prima di disegnare il logo in `paintContent`; usare lo stesso schema nel modulo.

7. **File già identici** (condiviso 7; P15; D12; G15)
   - Cosa: spostare nel modulo `FamilyTheme.h`, `FamilySoundProfiles.h`, `tests/FamilyAudioEvidence.h` (md5 identici) e `CircleOfFifths.{h,cpp}` (piano ≡ guitar a parte l'intestazione).
   - Note/rischi: rischio basso. bassFeel/bassGate/pianoReverb/pianoChorus (`FamilySoundProfiles.h:46-49`) servono solo a piano, `freeMode`/`setFreeMode` (`CircleOfFifths.h:37`, `.cpp:238, 298, 371`) solo a guitar: nel modulo si tengono, nei singoli repo non vanno tolti.

8. **Accesso ai parametri `raw()`** (condiviso 8)
   - Cosa: enum di indici + array di `std::atomic<float>*` riempito una volta sola, stesso accessor nei tre.
   - File: piano `PluginProcessor.cpp:1078-1081` (deref senza controllo); drums `298-330`; guitar `304-309`.
   - Note/rischi: rischio basso, ma tocca decine di chiamate. In drums è già stato fatto solo il confronto per puntatore prima di `strcmp` (API invariata).

9. **Harness dei test** (condiviso 10)
   - Cosa: `tests/TestSupport.h` comune con la macro `CHECK` e il mock `PlayHead`.
   - File: `tests/PluginTests.cpp:23-40`, `tests/EngineTests.cpp:19-30` circa, in 6 file.
   - Note/rischi: rischio basso.

10. **Wrapper di Timer** (condiviso 11)
    - Cosa: `juce::TimedCallback` (JUCE 8) al posto di `Refresher` (piano `PluginProcessor.h:411`), `LinkTimer` e `PatternTimer` (drums/guitar). In drums i due bin per gli shared_ptr ritirati sono già un solo `RetireBin<T>`: da riusare in guitar quando ci arriva il pattern preparato (G2).
    - Note/rischi: rischio basso.

## Arranger (fasegroovearranger) contro plugin

Fonte: report-arranger.md (A31) + confronto dei file dopo l'allineamento dei motori vendorizzati (Piano 0.31.1, Drums 0.20.1, Guitar 0.10.1).

11. **FamilyTheme e CircleOfFifths nell'arranger** (A31; condiviso 7)
    - Cosa: l'arranger usa la stessa `FamilyTheme.h` (identica a quella dei tre plugin e alle copie in `ThirdParty/*/Source`) e una `CircleOfFifths.{h,cpp}` quasi identica (5-7 righe di differenza da piano/guitar). Quando nasce il modulo comune, l'arranger lo include invece delle sue copie.
    - File: arranger `Source/FamilyTheme.h`, `Source/CircleOfFifths.{h,cpp}`, `ThirdParty/fasegroove*/Source/FamilyTheme.h`.
    - Note/rischi: rischio basso. `scripts/verify-family.py` controlla già i blob del tema: va puntato sul modulo.

12. **Branding** (A31; condiviso 6)
    - Cosa: `Source/Branding.{h,cpp}` dell'arranger ha già la cache dell'icona (singleton `DeletedAtShutdown`, come drums) e ha assorbito `drawFamilyLogo`. Nel modulo: stesso `drawFullLogo` parametrizzato (icona, wordmark "GROOVE ARRANGER"). Le copie `ThirdParty/*/Source/Branding.*` non sono compilate (CMakeLists.txt:28-38): toglierle dal vendoring.
    - Note/rischi: rischio basso.

13. **Localisation e traduzioni** (A31; condiviso 4)
    - Cosa: `Source/Localisation.cpp` differisce da drums/guitar per ~135 righe (cache di `tr()` per lingua e per thread, tabella `Translations.inc` + `ArrangerTranslations.inc`, voce "Close"). Nel modulo: cache di `tr()` (già nell'arranger) e tabella comune + file per prodotto. Le chiavi doppie vincono per ultime in inglese ma per prime in italiano (`emplace`): 22 voci morte sono già state tolte dall'arranger; le altre ~38 differiscono solo per maiuscole (es. "Strings" -> "ARCHI") e vanno risolte nel modulo con chiavi sensibili alle maiuscole o una sola voce.
    - Note/rischi: rischio medio, testare le sei lingue (`--smoke-test` produce `language-*.png`).

14. **Updater** (condiviso 1)
    - Cosa: l'Updater dell'arranger diverge di ~183 righe da quello dei plugin (stesso `Checker`, repo/asset/nome diversi): usarlo con `ProductInfo` come i plugin.
    - Note/rischi: rischio basso; `tests/UpdaterTests.cpp` dell'arranger va mantenuto.

15. **Origine di PianoComping** (A31)
    - Cosa: `Source/core/PianoComping.cpp` è la logica del `PluginProcessor` di piano al commit `026f0451`, con helper std. Spostare quella logica nel motore di piano (`engine/`, senza JUCE) così che plugin e arranger compilino lo stesso file.
    - Note/rischi: rischio medio: l'arranger deve restare bit-identico (`verify-midi.py`, club audit).

16. **Script di sincronizzazione dei motori vendorizzati** (A31)
    - Cosa: `scripts/sync-engines.py` nell'arranger: per ogni plugin applica `git diff <versione vendorizzata>..HEAD -- Source/engine Source/Guide*.h` su `ThirdParty/*/Source` e segnala i conflitti; un test confronta `FamilyTheme.h` e la versione registrata. Tenere in un file le modifiche proprie dell'arranger (piano `separateBass`, cambio di lunghezza degli accordi di guitar).
    - Note/rischi: rischio basso. Caso reale: `GrooveEngine::sameSettings` di piano 0.31.1 non compila sul vendorizzato (manca `bassGate`/`editedLoop` in `GrooveSettings`); serve solo a processor/editor, quindi non è stato portato. Drums 0.20.1 e guitar 0.10.1 (gruppo preparato fuori dal thread audio) sono portati, con MIDI identico.
