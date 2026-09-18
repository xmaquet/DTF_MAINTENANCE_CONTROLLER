# 04 — Options d’architecture

**Date :** 2026-09-18  
**Statut :** options de cadrage — **aucun code d’exploitation**  
**Contrainte :** préférer l’automatisation d’Hosonsoft au remplacement du protocole, sauf avantage réel démontré

---

## 1. Arborescence cible (commune à toutes les options)

```text
dtf-maintenance/
│
├── src/
│   ├── scheduler/      # périodicité, inactivité
│   ├── hoson/          # client protocole — Phase D seulement
│   ├── printexp/       # interaction Hosonsoft / PrintExp (V0)
│   ├── maintenance/    # scénarios clean + motif
│   ├── safety/         # idle, busy, plafonds, dry-run
│   └── logging/        # journal horodaté
│
├── captures/           # pcap isolées, Phase C
├── config/             # YAML, pas de secrets
├── docs/               # cadrage, protocole, accès distant
├── tools/              # scripts d’observation lecture seule
├── tests/
└── README.md
```

Cette arborescence est un **objectif de structuration**. Elle ne justifie pas d’implémenter `hoson/` tant que la Phase D n’est pas ouverte.

---

## 2. Modes d’exécution

**DÉCLARÉ (PO) 2026-09-18 :** le controller tourne dans une **UI Python sur le PC DTF**. **Pas d’UI = pas de maintenance.** Pas de service Session 0, pas de tâche invisible.

La V0 s’exécute dans la session console (PrintExp est en session 1 ; SSH session 0 ne voit pas l’UI).

| Mode | Description | Intérêt | Risque |
|---|---|---|---|
| Tâche planifiée Windows | `python` lancé par le Planificateur | simple, visible | session utilisateur / UI |
| Programme au démarrage | raccourci startup | simple | même contrainte UI |
| Service Windows | tourne sans session interactive | robuste 24/7 | **incompatible** avec une V0 100 % UI si Hosonsoft exige un bureau |
| Service + session interactive | service qui délègue à une session | compromis | plus complexe |

**HYPOTHÈSE :** Hosonsoft est une application graphique de session. Si cela se **CONFIRME**, un service Session 0 pur ne pourra pas cliquer l’UI. La V0 devra alors s’exécuter dans une session ouverte (compte technique connecté, écran allumé ou session persistante).

### 2.1 Cible PO — deux backends (pas V0)

**DÉCLARÉ (PO) 2026-09-18 :** à terme, un controller à **deux niveaux** :

1. **PrintExp démarré** → piloter son **UI** (canal actuel, V0) ;
2. **PrintExp absent** → piloter **l’imprimante** (client protocole, Phase D).

**Gel V0 (CONFIRMÉ PO 2026-09-18) :** niveau 1 seulement. PrintExp absent → **refus**, pas de TCP vers `192.168.127.10`.

**Règle de sûreté (CONFIRMÉ PO) :** **jamais les deux canaux à la fois**. PrintExp tient déjà `192.168.127.10:5001` (**CONFIRMÉ**). Un second client pendant que PrintExp tourne est **interdit**.

Le niveau 2 reste **interdit** tant que des commandes ne sont pas **clairement identifiées** (Phase D). `src/hoson/` n’est pas ouvert.

---

## 3. Option V0 — Piloter Hosonsoft (recommandée en premier)

**Idée :** ne pas parler à la carte. Faire faire le travail à Hosonsoft, comme un opérateur.

### Variantes V0

| Variante | Mécanisme | Avantages | Inconvénients |
|---|---|---|---|
| V0-A CLI / IPC / fichier de commande | arguments, pipe, socket local, fichier job | plus robuste qu’une UI | peut ne pas exister |
| V0-B UI Automation (`pywinauto`) | inspecte contrôles, clique Clean | rapide si l’UI est accessible | fragile (pop-ups, focus) |
| V0-C AutoHotkey | scripts de clics / raccourcis | pragmatique | très fragile, peu testable |
| V0-D Mixte | CLI pour le job, UI pour Clean | réaliste | deux mécanismes à fiabiliser |

**Scénario V0 minimal :**

```text
ouvrir Hosonsoft (si nécessaire)
→ vérifier connexion imprimante
→ lancer Clean
→ attendre fin
→ journaliser
```

**Scénario V0.1 :**

```text
Clean
→ impression du motif de maintenance (fichier RIP existant)
→ attendre fin
```

**Critère de succès V0 :** robustesse, pas d’élégance protocolaire.

**Couche safety V0 :**

- refuser si processus d’impression utilisateur détecté ;
- `dry-run` qui loggue les clics/étapes sans les exécuter ;
- plafond quotidien de cleans.

---

## 4. Option V1 — Automatiser l’entrée d’impression, garder Hosonsoft pour la mécanique

**Idée :** Hosonsoft reste maître du Clean et de la connexion. Le motif d’entretien est un fichier déjà RIPé, déposé ou spoulé de façon répétable.

**HYPOTHÈSE de vecteur** (à confirmer en Phase A4) :

- hot folder ;
- fichier `.prn` / raster ;
- imprimante Windows ;
- TCP localhost.

**Décision de cadrage :** produire **une fois** avec le RIP un fichier du type `maintenance-pattern.prn` (CMJN + blanc), puis le réutiliser. Pas de RIP maison.

---

## 5. Option V2 — Client Python direct vers la carte (Phase D)

**Idée :** `src/hoson/` parle TCP (ou autre) à la carte.

```text
printer.connect()
status = printer.get_status()
if status.is_idle:
    printer.clean()   # ACTIVE COMMAND
```

**Conditions d’ouverture :**

- V0 opérationnelle **ou** V0 démontrée impossible ;
- captures isolées ;
- handshake / commandes / fin d’opération **CONFIRMÉS** ;
- distinction READ ONLY / ACTIVE COMMAND dans le code ;
- `dry-run` par défaut.

**Cette option n’est pas un objectif en soi.** Elle n’est retenue que si elle apporte un avantage réel (fiabilité, fonctionnement sans session UI, statut plus fiable, etc.).

---

## 6. Configuration (commune)

Les paramètres ne sont pas codés en dur. Exemple **illustratif** — les IP/ports sont des **HYPOTHÈSES** :

```yaml
printer:
  ip: 192.168.127.10    # DÉCLARÉ (PO) via UI Hosonsoft — pas une cible d'envoi
  port: 5001            # DÉCLARÉ (PO) via UI Hosonsoft — socket non observée

maintenance:
  clean_interval_hours: 6
  print_interval_hours: 12

safety:
  require_idle: true
  max_clean_per_day: 6
  dry_run: true
```

Le fichier réel ne devra être peuplé qu’avec des valeurs observées, ou clairement marquées comme hypothèses dans les commentaires.

---

## 7. Journalisation (commune)

Toutes les actions, y compris les refus de sûreté, sont journalisées.

Exemple de format cible :

```text
2026-09-18 08:00:00 printer online
2026-09-18 08:00:02 printer idle
2026-09-18 08:00:03 maintenance clean requested
2026-09-18 08:01:10 clean completed
2026-09-18 08:01:15 maintenance print requested
2026-09-18 08:02:02 maintenance print completed
```

Les erreurs aussi. Pas de log silencieux en cas de skip (`machine_busy`, plafond atteint).

---

## 8. Accès distant

```text
poste développement (XAVIER)  192.168.10.126     OBSERVÉ
        |
        | Wi-Fi 192.168.10.0/24
        | ICMP vers 192.168.10.129               OBSERVÉ
        | SSH (clé) — pas encore en place
        v
PC DTF Windows   192.168.10.129                  DÉCLARÉ (PO)
        |
        +--- Hosonsoft
        |
        +--- Ethernet 192.168.127.3 → (HYPOTHÈSE) 192.168.127.10:5001
```

**Règle :** depuis `XAVIER`, n’adresser que `192.168.10.129`. Ne pas viser `192.168.127.10`.

Priorité : **OpenSSH Server** Windows (fonctionnalité optionnelle plausible sur Windows 10 Pro 19045 ; compte **administrateur** **DÉCLARÉ**). Document : `docs/remote-access.md` (non rédigé tant que le nom de compte n’est pas connu).

---

## 9. Recommandation d’architecture au cadrage

| Priorité | Choix | Justification |
|---|---|---|
| 1 | **V0-A d’abord** (CLI/IPC si elle existe) | plus sûr et plus stable qu’un clic |
| 2 | **V0-B** si pas d’IPC | atteint le scénario Clean sans toucher la carte |
| 3 | **V1** pour le motif | un fichier RIP unique, pas de RIP maison |
| 4 | **Service Windows** seulement si la V0 n’exige pas d’UI, sinon tâche en session | éviter Session 0 vs GUI |
| 5 | **V2** seulement après Phase C et avantage clair | préserve la machine |

**Non-choix au cadrage :** client TCP vers `192.168.127.10:5001`. L’UI Hosonsoft **DÉCLARE** ces valeurs ; ce n’est toujours pas une architecture retenue, ni une autorisation d’envoyer des paquets.

---

## 10. Séparation des responsabilités (quand le code existera)

| Module | Autorisé à | Interdit de |
|---|---|---|
| `scheduler/` | décider *quand* | parler à la carte |
| `safety/` | autoriser / refuser | contourner un refus |
| `printexp/` | piloter Hosonsoft | forger des paquets carte |
| `hoson/` | protocole CONFIRMÉ | paquets hypothétiques |
| `maintenance/` | orchestrer le scénario | ignorer `safety` |
| `logging/` | tout tracer | décider d’une action |

Le Réalisateur n’implémente un module que lorsque les phases amont l’ont validé.
