# 00 — Contexte du projet

**Projet :** DTF Maintenance Controller  
**Machine cible :** imprimante DTF Inkone DM3  
**Pilotage actuel :** Hosonsoft / PrintExp  
**Date de cadrage :** 2026-09-18  
**Statut :** cadrage initial — aucune automatisation, aucun envoi de commande

---

## Mission

Concevoir et développer, de manière progressive, documentée et prudente, un service ou programme Python capable d’assurer **l’entretien périodique automatique** d’une imprimante DTF Inkone DM3 aujourd’hui pilotée manuellement via Hosonsoft / PrintExp.

L’objectif n’est **pas** de réécrire Hosonsoft. L’objectif est :

1. comprendre son fonctionnement ;
2. automatiser les opérations d’entretien nécessaires ;
3. n’envisager un remplacement partiel par des commandes directes **que** si cela apporte un avantage réel, après observation et validation.

Une solution robuste qui pilote Hosonsoft lui-même est considérée comme **parfaitement valide**.

---

## Scénario fonctionnel cible

```text
Machine sous tension
        |
        v
Surveillance périodique
        |
        v
Vérification état imprimante
        |
        v
Clean de maintenance
        |
        v
Attente fin de clean
        |
        v
Impression d'un petit motif de maintenance
        |
        v
Attente fin d'impression
        |
        v
Journalisation
        |
        v
Retour en attente
```

La fréquence est configurable (intervalles de clean, d’impression, éventuellement selon l’inactivité).

---

## Philosophie

Toujours privilégier :

```text
observer → comprendre → reproduire → automatiser
```

et non :

```text
deviner → envoyer une commande → voir ce qui se passe
```

La priorité est de **préserver l’intégrité de l’imprimante**.

---

## Discipline des faits

Toute information portée par ce dépôt doit être classée :

| Marqueur | Signification |
|---|---|
| **HYPOTHÈSE** | Affirmation non vérifiée sur cette machine. Ne doit jamais être traitée comme un fait. |
| **DÉCLARÉ (PO)** | Information donnée par le Product Owner, non encore recoupée par observation sur la machine. |
| **OBSERVÉ** | Constat réel, mais pas encore recoupé / reproductible. |
| **CONFIRMÉ** | Observation recoupée, reproductible, ou validée par le Product Owner **et** vérifiée sur le système. |

Une déclaration Product Owner ne devient **CONFIRMÉ** qu’après vérification sur le système concerné.

Exemple de formulation attendue :

```text
OBSERVÉ:
Hosonsoft ouvre une connexion TCP vers 192.168.127.10:5001.

CONFIRMÉ:
la connexion disparaît lorsque Hosonsoft est fermé.

HYPOTHÈSE:
le port 5001 transporte les commandes de contrôle.
```

**Règle :** ne jamais transformer implicitement une hypothèse en fait établi. Ne jamais coder une commande à partir d’un paquet supposé ou partiellement identifié.

---

## Phases du projet

| Phase | Nom | Objectif | État au cadrage |
|---|---|---|---|
| A | Observer | Inventaire Windows, réseau, fichiers, processus, échanges | **À démarrer** |
| B | Automatiser Hosonsoft | Prototype V0 : ouvrir, vérifier connexion, Clean, attendre | Non commencée |
| C | Reverse engineering réseau | Captures isolées, analyse protocole, `docs/protocol-analysis.md` | Interdite tant que V0 n’est pas opérationnelle **et** que Phase A n’a pas produit un inventaire |
| D | Client Python expérimental | Commandes **identifiées** uniquement, distinction READ ONLY / ACTIVE COMMAND | Interdite tant que les commandes ne sont pas clairement identifiées |

**Règle fondamentale :** ne jamais commencer par envoyer des commandes inconnues directement à l’imprimante.

---

## Rôles logiques des agents

| Rôle | Responsabilité | Interdit |
|---|---|---|
| **Investigateur** | Analyse Windows, réseau, Wireshark, protocole, observation Hosonsoft | Envoyer des commandes non identifiées |
| **Architecte** | Architecture Python, séparation des responsabilités, sécurité, configuration, journalisation | Implémenter des commandes actives non validées |
| **Réalisateur** | Code uniquement ce qui a été validé par les étapes précédentes | Anticiper le protocole ou « essayer » des paquets |
| **Vérificateur** | Tests, revue de sécurité, contrôle des hypothèses, interdiction des commandes supposées | Valider une hypothèse sans preuve |

---

## Environnements

Deux postes distincts sont prévus.

### Poste de développement

**OBSERVÉ** (2026-09-18, machine locale du dépôt) :

- nom d’hôte : `XAVIER`
- OS : Windows 10 Home, version 2009, build 26200
- Python : 3.13.14
- Git : 2.55.0.windows.3
- interfaces IPv4 notables : Wi-Fi `192.168.10.126`, VirtualBox/host-only `192.168.56.1`
- dépôt : vide au démarrage du cadrage (aucun code, aucun document préexistant)

**HYPOTHÈSE :** ce poste n’est **pas** le PC dédié à l’imprimante. Le développement se fait depuis un autre poste que le PC DTF, conformément au brief.

### PC DTF (cible d’exploitation)

**HYPOTHÈSE** (brief Product Owner, non vérifié sur machine) :

- PC Windows dédié à l’imprimante ;
- Hosonsoft / PrintExp installé ;
- imprimante reliée directement par Ethernet RJ45 ;
- accès réseau permettant une administration distante ;
- PC et imprimante pouvant rester sous tension en permanence.

**DÉCLARÉ (PO) :** Windows 10 Pro, build 19045.6466 ; admin `192.168.10.129` ; Ethernet `192.168.127.3` ; UI Hosonsoft Server IP `192.168.127.10:5001`.

**OBSERVÉ (UI, connecté) :** Hosonsoft `5.8.1.1.29.R.Unicode` ; MB Program `5.8.1.1.20.R.Unicode` ; firmware `CSD_2.75_DL_XP600_1HWC_5.7.6.5.X_20240220`.

**CONFIRMÉ :** UI Main Board à zéro ⇔ déconnecté ; champs peuplés ⇔ connecté.

**Politique entretien (DÉCLARÉ PO) :** tous les jours 20:00 ; sauter si print en cours ou print du jour (InkOne **ou** `.prn` PrintExp) ; Check/Clean ne sautent pas ; sinon Clean normal (strong si 3 j sans print) puis Check.

**Gel métier + runtime PO :** UI Python obligatoire sur le PC DTF ; voir [05-v0-dry-run-plan.md](05-v0-dry-run-plan.md). Python 3.13.7 **OBSERVÉ**. Fenêtre dry-run ouverte **DÉCLARÉ (PO)** 2026-09-18 18:25. **PrintExp absent = refus V0, pas de repli carte** (**CONFIRMÉ PO**).

---

## Périmètre inclus

- Entretien périodique (clean, motif de maintenance, journalisation).
- Automatisation de Hosonsoft en priorité (V0).
- Accès SSH reproductible vers le PC DTF.
- Service Windows ou programme lancé au démarrage.
- Modes `dry-run` / `simulation` et verrouillage `machine_busy`.
- Configuration externalisée (YAML ou équivalent).
- Documentation des observations et des risques.

## Périmètre exclu (sauf décision ultérieure explicite)

- Réécriture d’un RIP.
- Interpréteur du format d’impression, tant qu’un fichier RIP existant (`maintenance-pattern.prn` ou équivalent) peut être réutilisé.
- Envoi de commandes réseau « pour voir ».
- Remplacement du protocole Hoson sans avantage réel démontré.
- Toute action mécanique non validée (déplacement chariot, pompes, têtes).

---

## Critères de succès (cadrage)

1. L’imprimante n’est jamais sollicitée par une commande inconnue.
2. Un inventaire **OBSERVÉ / CONFIRMÉ** du système existe avant toute automatisation active.
3. Un prototype V0 peut, via Hosonsoft, enchaîner connexion → Clean → attente de fin, de façon journalisée et interruptible.
4. Une solution V0 robuste suffit : le succès n’exige pas le remplacement d’Hosonsoft.
5. Toute commande active est explicitement marquée dangereuse, protégée par `dry-run`, `require_idle` et un plafond de fréquence.

---

## Documents associés

- [01-system-inventory.md](01-system-inventory.md) — inventaire (majoritairement à confirmer)
- [02-investigation-plan.md](02-investigation-plan.md) — plan d’investigation Phase A
- [03-risk-register.md](03-risk-register.md) — risques machine et projet
- [04-architecture-options.md](04-architecture-options.md) — options d’architecture, sans implémentation
- `docs/remote-access.md` — procédure OpenSSH (installation en cours)
- [05-v0-dry-run-plan.md](05-v0-dry-run-plan.md) — plan V0 dry-run (gel 2026-09-18)
