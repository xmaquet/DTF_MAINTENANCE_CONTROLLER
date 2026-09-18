# 05 — Plan V0 dry-run (gel métier 2026-09-18)

**Statut :** plan validé par le Product Owner — **aucun clic mécanique, aucun Clean réel**  
**Cible :** `PrintExp_X64.exe` (UI Hosonsoft) sur `DESKTOP-MANFYQB`  
**Interdit :** TCP vers `192.168.127.10`, paquet expérimental, clic Clean/Check tant que le dry-run n’est pas relu

**CONFIRMÉ PO :** PrintExp absent → **refus V0**, pas de repli carte. Jamais UI PrintExp **et** TCP carte en même temps.

---

## 1. Règle gelée

```text
Tous les jours à 20:00 (heure Windows du PC DTF)
        |
        +-- print EN COURS à 20:00              → SAUTER + log
        +-- print utilisateur aujourd'hui       → SAUTER + log
        |     (InkOne Jobs/PrnList OU .prn ouvert dans PrintExp)
        |     → réinit compteur strong 3 jours
        |     Check et Clean ne comptent PAS comme print
        |
        +-- sinon
              |
              +-- 3 jours calendaires sans print → Clean STRONG puis Check
              +-- sinon                          → Clean NORMAL puis Check
```

**Ce soir 18/09/2026 :** SAUTER — `ERASMART Quality Evaluation.prn` lancé vers 15:28 (**CONFIRMÉ** log + PO). Compteur strong réinitialisé.

---

## 2. Préconditions (avant tout clic, même futur)

Toutes **READ ONLY** à vérifier :

**CONFIRMÉ :** V0 UI doit tourner dans la session **console** (`user` ID 1). SSH (session 0) ne voit pas les fenêtres PrintExp (`MainWindowHandle=0`, 0 élément UIA).
2. Processus `PrintExp_X64.exe` en cours.
3. Connexion carte : TCP `PrintExp_X64.exe` → `192.168.127.10:5001` ESTABLISHED **ou** UI connectée (champs MB non nuls).
4. Bandeau PrintExp **actif** (pas de job, pas de Clean/Check en cours).
5. `dry_run: true` dans la config.

Si une précondition échoue → **ne rien cliquer**, journaliser le refus.

---

## 3. Détection « print » (sans parler à la carte)

| Question | Source privilégiée | Ne pas utiliser seul |
|---|---|---|
| Print **aujourd’hui** | `PrnList` / `Jobs` InkOne **LastWriteTime** du jour **ou** log PrintExp `Log[YYYY_MM_DD].txt` contenant un nom de `.prn` fichier (ex. `ERASMART Quality Evaluation.prn`) | `PRNPrintExit()`, `GO-Print` (le **Check** les émet aussi) |
| Print **en cours** | `ReceiveSignal Moving` **et** un `.prn` / `~section` RIP ; ou bandeau PrintExp occupé | `GO-CleanInkStack` / `Auto Microwave Pump Ink` (pompe auto au repos) |
| Check | petit motif **~166×25 mm**, `GO-Print` sans nouveau PrnList | — |

**HYPOTHÈSE à valider en dry-run outillé :** lister les noms de contrôles UI (Inspect / `print_control_identifiers`) **sans cliquer**.

---

## 4. Séquence UI visée (ACTIVE COMMAND — pas maintenant)

```text
[dry-run] log: would click Clean
[dry-run] log: would select menu line Normal | Strong
          attendre : chariot rentré + bandeau rendu
          timeout → ABANDON (pas de relance)
[dry-run] log: would click Check
          attendre bandeau
          timeout → ABANDON
journaliser fin
```

**CONFIRMÉ UI :** clic **Clean** → **menu 3 lignes** Weak / Normal / Strong.

| Ligne | Usage V0 |
|---|---|
| Weak | **jamais** en auto |
| Normal | cycle quotidien sans print, si < 3 j |
| Strong | 3 jours sans print |

---

## 5. Ce que le dry-run doit écrire (exemple)

```text
2026-09-18 20:00:00 scheduler tick
2026-09-18 20:00:01 skip: user prn today (ERASMART Quality Evaluation.prn at 15:28)
2026-09-18 20:00:01 strong_counter reset
2026-09-18 20:00:01 dry_run=true no_click
```

Jour sans print (futur) :

```text
2026-09-20 20:00:00 printer idle, no user print today
2026-09-20 20:00:01 would: Clean -> Normal
2026-09-20 20:00:01 would: wait toolbar
2026-09-20 20:00:01 would: Check
2026-09-20 20:00:01 dry_run=true no_click
```

---

## 6. Prochaines étapes techniques (toujours sans Clean réel)

1. **Dump UI / Win32** de PrintExp — **CONFIRMÉ 2026-09-18 session 1 :** UIA vide ; boutons Win32 **Clean id=11030**, **Check id=11029**. Fenêtre minimisée au dump. Menu Weak/Normal/Strong non présent tant que Clean n’est pas cliqué. Mapping : [printexp-toolbar-map.md](evidence/printexp-toolbar-map.md). **Aucun clic.**
2. Script **dry-run** dans la **même session** que PrintExp.
3. Revue Vérificateur.
4. Premier clic réel : seulement après validation PO.

**Runtime (gel PO) :** une fenêtre Python sur le bureau du PC DTF. Fermer la fenêtre inhibe toute maintenance. `dry_run: true` : décision + log, **aucun clic**.

Controller copié : `C:\Users\User\DTF_Maintenance_Controller\`  
Lancer **sur le bureau** (pas SSH) :

```text
py -3 C:\Users\User\DTF_Maintenance_Controller\run_controller.py
```

**DÉCLARÉ (PO) 2026-09-18 18:25 :** fenêtre « DTF Maintenance Controller — dry-run » ouverte.  
**OBSERVÉ** log : `controller UI started dry_run=true require_ui=true`  
**OBSERVÉ 18:26 :** `would_clean_normal` **faux** (log PrintExp UTF-16 non lu → PrnList Agathe 17/09). Correcteur déployé : UTF-16 + `.prn` avec espaces.  
**CONFIRMÉ 18:30 :** après relance UI → `skip | print utilisateur aujourd'hui (15:31)`. Aucun clic.

**CONFIRMÉ 18:37 (PrintExp restauré) :** skip + localisation Win32 Clean `id=11030` `(498,75)-(579,156)` ; Check `id=11029` `(393,76)-(474,157)` ; `minimized=False` ; idle bandeau **OBSERVÉ**. Aucun `BM_CLICK`.

---

## 7. Hors périmètre V0

- Client TCP `192.168.127.10:5001`
- Wireshark / Phase C
- Service Session 0 (l’UI exige un bureau)
- RIP InkOne, interpréteur PRN
- Bouton physique nozzle check
- Weak automatique
