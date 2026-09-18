# Mapping barre PrintExp — dump Win32 2026-09-18 18:33 (session 1)

**Statut :** lecture seule. Aucun clic.  
**Build :** `PrintExp_X64` 5.8.1.1.29, PID 23912, hwnd principal `985482`, titre `PrintExp`, classe `#32770`.

**OBSERVÉ :** UI Automation = 0 descendant. Les boutons sont des `Button` Win32 (GetWindowText).

**OBSERVÉ :** fenêtre principale `rect=-32000,-32000` → **minimisée** au moment du dump. Les coordonnées écran des boutons ne sont pas exploitables tant que PrintExp n’est pas restauré.

**CONFIRMÉ 18:37 dry-run, fenêtre restaurée :** `PrintExp rect=0,0-1920,1040 minimized=False`. Check `(393,76)-(474,157)` ; Clean `(498,75)-(579,156)`. `bandeau_idle_hypothese=True`.

## Boutons barre (parent toolbar `#32770`)

| Texte | GetDlgCtrlID | Enabled (idle) | Visible |
|---|---|---|---|
| OpenFiles | 5 | oui | oui |
| Print | 4 | **non** | oui |
| Pause | 11027 | **non** | oui |
| Cancel | 1324 | **non** | oui |
| **Check** | **11029** | oui | oui |
| **Clean** | **11030** | oui | oui |
| Flash | 11042 | oui | oui |

**HYPOTHÈSE idle :** Print / Pause / Cancel désactivés **et** Check / Clean activés = bandeau au repos. À revalider fenêtre restaurée, hors job.

**Non vu (attendu) :** Weak / Normal / Strong — menu 3 lignes **après** clic Clean. Pas dans l’arbre tant que le menu n’est pas ouvert.

**OBSERVÉ hors V0 :** page cachée `Auto Clean:` + combos `Normal` / `Strong A`. Ce n’est **pas** le menu Clean V0. Ne pas s’en servir.

Dump brut : [printexp-ui-dump.txt](printexp-ui-dump.txt) (1019 enfants).
