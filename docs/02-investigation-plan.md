# 02 — Plan d’investigation

**Date :** 2026-09-18  
**Phase concernée :** Phase A (Observer), puis préparation de la Phase B  
**Interdit à ce stade :** envoi de commandes inconnues à l’imprimante, reverse engineering actif du protocole, client Python « expérimental » de commandes

---

## Objectif de la Phase A

Construire un inventaire **OBSERVÉ / CONFIRMÉ** avant toute automatisation.

Comprendre précisément :

- processus Windows de Hosonsoft / PrintExp ;
- exécutables et chemins ;
- fichiers de configuration ;
- journaux ;
- ports réseau, connexions TCP/UDP, adresses IP ;
- échanges Hosonsoft ↔ carte de contrôle ;
- échanges RIP ↔ Hosonsoft.

Livrable de fin de Phase A : mise à jour de [01-system-inventory.md](01-system-inventory.md) et un **premier plan d’automatisation V0** (sans code de commande directe).

---

## Principes d’investigation

1. **Une variable à la fois.** Ne pas mélanger observation réseau, clic Clean, et impression.
2. **Lecture avant écriture.** `ipconfig`, `netstat`, listage de fichiers et processus d’abord ; aucune injection de paquet.
3. **Pas de test « pour voir »** sur la mécanique (chariot, pompes, têtes).
4. **Les valeurs `192.168.127.10` et TCP `5001` sont désormais DÉCLARÉES comme affichage Hosonsoft**, pas comme socket observée. Elles restent **interdites comme cibles d’envoi**. L’étape A1 les vérifiera en lecture (ARP, netstat).
5. Les questions au Product Owner se posent **une par une**. Chaque réponse peut modifier la suivante.

---

## Ordre des questions Product Owner (priorité)

Ces questions orientent l’investigation. Elles ne remplacent pas l’observation sur machine.

1. Architecture réseau réelle — **largement DÉCLARÉ + ICMP OBSERVÉ** : admin `192.168.10.129` ; Ethernet `192.168.127.3` → UI Hoson `192.168.127.10:5001`. Identité Windows de `.129` encore à confirmer.
2. Version Windows du PC DTF — **DÉCLARÉ (PO)** : Windows 10 Pro, build 19045.6466.
3. Version exacte de Hosonsoft / PrintExp — **OBSERVÉ** (UI) : Software `5.8.1.1.29.R.Unicode` ; Device Manager `5.8.1.1.27.R.BS` ; Data Process `5.8.1.1.27.R.BS_U`. MB Program (carte, **connecté**) `5.8.1.1.20.R.Unicode`.
4. Disponibilité d’un accès administrateur — **DÉCLARÉ (PO)** : oui. Nom du compte encore inconnu.
5. Configuration IP de la carte Ethernet imprimante — **partiellement DÉCLARÉ** via l’UI Hosonsoft (`192.168.127.10:5001`) ; masque / ARP / socket réelle encore à observer.
6. Présence de Wireshark — **DÉCLARÉ (PO)** : non (pas à sa connaissance). Installation éventuelle **après** V0, pour la Phase C.
7. Présence de Python — **OBSERVÉ** (PO) : `python` et `py` non reconnus. Installation plus tard, pas un prérequis d’observation.
8. Possibilité d’installer OpenSSH Server — **CONFIRMÉ** : `ssh user@192.168.10.129` par clé depuis `XAVIER`.
9. Comportement exact du bouton Clean — **DÉCLARÉ (PO)** : weak / normal / strong ; pompe plus longue selon le niveau ; chariot + capping ; **fin** = chariot revient + bandeau Hosonsoft à nouveau actif. **Reste :** UI de choix du niveau, niveau d’entretien habituel, durées.
10. Processus actuel utilisé pour imprimer le motif de test — **DÉCLARÉ (PO)** : Check Hosonsoft **ou** bouton physique nozzle check ; motif = carrés / traits par couleur. V0.1 visera le **Check logiciel**.

Le plan ci-dessous sera ajusté dès les premières réponses.

---

## Étape A0 — Cadrage humain (en cours)

- Produire les documents `docs/00` à `docs/04`.
- Examiner le dépôt et l’environnement du poste de développement.
- Interroger le Product Owner, **une question à la fois**.
- Chemin d’admin **DÉCLARÉ** (`192.168.10.129`) et **OBSERVÉ** en ICMP depuis `XAVIER`. OS **DÉCLARÉ** : Windows 10 Pro 19045.6466. Compte **administrateur** **DÉCLARÉ**. `docs/remote-access.md` attend encore le nom de compte et OpenSSH.

**Sortie attendue :** suffisamment d’informations pour un plan A1 ciblé, pas une checklist générique de dix actions simultanées.

---

## Étape A1 — Accès et topologie (lecture seule)

**Prérequis :** réponse à la question réseau, et idéalement un accès (local ou distant) au PC DTF.

Actions prévues (lecture seule) :

1. Identifier les interfaces réseau du PC DTF.
2. Noter l’adresse IP du PC, le masque, la passerelle, les routes.
3. Identifier l’interface reliée à l’imprimante (nom Windows, MAC, média connecté).
4. Consulter la table ARP pour d’éventuelles adresses de la carte Hoson.
5. Lister les connexions TCP/UDP établies **sans** lancer d’action imprimante, puis **avec** Hosonsoft ouvert au repos.
6. Documenter firewall et partage d’imprimante éventuel.

**Livrable :** section « Réseau réel » dans `01-system-inventory.md`, avec marqueurs OBSERVÉ / CONFIRMÉ.

**Non-objectif :** ping agressif, scan de ports large, envoi de payload sur 5001/9100.

Un `ping` unique vers une IP **déjà vue** dans ARP ou dans la config Hosonsoft pourra être discuté ; un scan de plage ne sera pas le premier réflexe.

---

## Étape A2 — Inventaire Hosonsoft / PrintExp (lecture seule)

Sur le PC DTF, Hosonsoft **ouvert mais sans action mécanique** :

1. Localiser les exécutables (raccourcis, `Program Files`, services).
2. Noter versions (propriétés fichier, À propos).
3. Lister processus et services associés (`Get-Process`, `Get-CimInstance Win32_Service`).
4. Repérer fichiers de configuration (`.ini`, `.xml`, `.json`, registre).
5. Repérer journaux.
6. Chercher une CLI, des arguments, des fichiers de commande, une IPC (pipes, sockets localhost, COM).

**Livrable :** fiche exécutable / config / logs.

---

## Étape A3 — Observation au repos (aucune action utilisateur)

Fenêtre d’observation courte (ordre de grandeur : 30 secondes à quelques minutes) :

- Hosonsoft connecté, **aucune** action.
- Relever heartbeats éventuels via `netstat` (renouvellement de connexions) — pas encore de capture Wireshark obligatoire si l’outil n’est pas installé.

**Objectif :** distinguer le trafic de vie de celui des commandes.

---

## Étape A4 — Cartographie RIP ↔ Hosonsoft (sans imprimer en production)

Identifier comment un job arrive jusqu’à Hosonsoft :

- dossier d’entrée (hot folder) ;
- file d’attente ;
- port localhost ;
- fichier temporaire ;
- imprimante Windows.

**Ne pas** lancer une impression utilisateur. Au plus, documenter le **processus actuel** décrit par le Product Owner, puis observer un fichier de test **déjà existant** s’il y en a un.

---

## Étape A5 — Préparation de l’accès distant

Si OpenSSH Server est autorisé :

- rédiger `docs/remote-access.md` ;
- privilégier l’authentification par clé ;
- aucun mot de passe dans les scripts ;
- documenter transfert de scripts et récupération de captures.

Cette étape est administrative. Elle ne déclenche aucune commande imprimante.

---

## Phase B — Automatiser Hosonsoft (après A)

Objectif V0, **via Hosonsoft**, pas via le protocole carte :

```text
ouvrir Hosonsoft
→ vérifier connexion imprimante
→ lancer Clean
→ attendre fin
```

Puis, second incrément V0.1 :

```text
ouvrir Hosonsoft
→ Clean
→ impression motif maintenance
```

Pistes à évaluer **dans cet ordre** :

1. Paramètres CLI / fichiers de commande / IPC documentés ou observables.
2. Automatisation Windows (tâches, UI Automation).
3. `pywinauto`.
4. AutoHotkey si pertinent.

**Critère d’entrée Phase B :** inventaire A1–A2 suffisant, droits adaptés, et description CONFIRMÉE ou au moins OBSERVÉE du bouton Clean.

---

## Phase C — Captures réseau (après V0 opérationnelle)

Captures isolées, une variable à la fois. Exemple :

| Capture | Condition |
|---|---|
| 01 | Hosonsoft connecté, aucune action pendant 30 s |
| 02 | 1 seul Clean, aucune autre opération |
| 03 | 1 déplacement chariot |
| 04 | 1 nozzle check |
| 05 | impression d’un très petit motif |

Comparer systématiquement. Consulter `docs/protocol-analysis.md` (à créer en Phase C).

**Interdit :** tester automatiquement une séquence découverte sans validation humaine.

---

## Phase D — Client Python expérimental (après identification claire)

Architecture envisagée :

```text
src/hoson/connection.py
src/hoson/protocol.py
src/hoson/commands.py
src/hoson/status.py
```

Distinction obligatoire :

- `READ ONLY`
- `ACTIVE COMMAND` (marquage explicite, potentiellement dangereux)

Ne jamais implémenter une commande à partir d’un paquet partiellement identifié.

---

## Outils prévus, par phase

| Phase | Outils | Usage |
|---|---|---|
| A | PowerShell, Gestionnaire des tâches | lecture |
| A/C | Wireshark, pcap/pcapng | observation, pas d’injection |
| A | Process Explorer, Process Monitor | observation |
| B | pywinauto / AHK / UI Automation | piloter l’UI existante |
| D | Python | client **après** identification |

Le hooking d’API n’est envisagé **que si** les pistes non invasives échouent, et seulement avec validation.

---

## Plan terrain A1 — maintenant autorisable (lecture seule)

Les informations Product Owner suffisent. SSH `user@192.168.10.129` est **CONFIRMÉ**.

**Prérequis humains :** Hosonsoft ouvert, imprimante **connectée**, **aucune** impression / Clean / Check en cours.

**Autorisé :**

```text
ssh user@192.168.10.129
  ipconfig /all
  Get-NetIPAddress, Get-NetAdapter, Get-NetRoute
  arp -a
  Get-NetTCPConnection | où RemoteAddress = 192.168.127.10 (si présent)
  Get-Process
  chemins Hosonsoft (Program Files, raccourcis)
```

**Interdit dans A1 :**

- ping / connect vers `192.168.127.10` **sauf** si l’adresse apparaît déjà en ARP ou en connexion établie — et encore, un ping unique seulement après consignation ;
- scan de ports ;
- clic Clean / Check / déplacement ;
- envoi de paquet « pour voir » ;
- installation Python / Wireshark dans cette étape.

**Livrable A1 2026-09-18 :** exécuté. Voir `01-system-inventory.md` — TCP 5001, ARP, PrintExp, NWReceive:9100 **CONFIRMÉS**. Pas de ping vers la carte.

Puis A2 (fichiers config, IPC) sans action mécanique.
