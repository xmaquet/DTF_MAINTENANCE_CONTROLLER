# 03 — Registre des risques

**Date :** 2026-09-18  
**Périmètre :** risques machine, logiciels, projet et humains  
**Règle :** une erreur logicielle peut endommager une imprimante physique. En cas de doute, ne pas agir.

Les niveaux sont une **HYPOTHÈSE** de criticité au cadrage ; ils seront réévalués après observation.

Légende : **C** = criticité (1 basse … 5 critique) · **P** = probabilité relative au cadrage · **Statut** = ouvert / surveillé / accepté / mitigé

---

## 1. Risques machine (intégrité de l’imprimante)

| ID | Risque | C | P | Cause typique | Mitigation obligatoire | Statut |
|---|---|---|---|---|---|---|
| M01 | Déplacement incorrect du chariot | 5 | moyenne si commandes brutes | paquet mal identifié, automatisation UI au mauvais moment | aucune commande inconnue ; `machine_busy` ; pas d’action pendant une impression | ouvert |
| M02 | Collision mécanique | 5 | moyenne | chariot envoyé hors course, capteur ignoré | ne pas envoyer de déplacement tant que le protocole n’est pas CONFIRMÉ ; V0 via Hosonsoft | ouvert |
| M03 | Sollicitation excessive des pompes | 4 | moyenne | boucle de clean, timeout mal géré, retry agressif | plafond `max_clean_per_day` ; pas de retry automatique non borné | ouvert |
| M04 | Aspiration prolongée | 5 | faible à moyenne | commande clean/maintenance mal terminée, attente absente | attendre une fin d’opération **observée** ; timeout de sécurité qui **arrête** le scénario, pas qui relance | ouvert |
| M05 | Surchauffe | 4 | faible | cycles trop fréquents, machine déjà en défaut | intervalles configurables ; refuse si statut non idle / erreur | ouvert |
| M06 | Projection d’encre | 4 | moyenne | clean ou purge inattendu | V0 = bouton Hosonsoft connu ; jamais de payload expérimental | ouvert |
| M07 | Détérioration de la tête | 5 | moyenne sur la durée | séchage **ou** maintenance trop agressive | objectif du projet = entretien ; plafonds et idle requis | ouvert |
| M08 | Consommation d’encre excessive | 3 | élevée si mal cadencé | motif trop grand, cleans trop fréquents | motif RIP unique et petit ; config d’intervalles ; journal des volumes si disponible | ouvert |
| M09 | Action pendant une impression utilisateur | 5 | élevée sans verrou | scheduler naïf | `require_idle: true` ; détection busy ; pas de maintenance si job en cours | ouvert |
| M10 | Envoi d’un paquet « pour voir » | 5 | élevée en l’absence de discipline | reverse engineering impatient | interdiction projet ; revue Vérificateur ; pas de client actif en Phase A/B | ouvert |

---

## 2. Risques liés au reverse engineering et aux commandes

| ID | Risque | C | Mitigation |
|---|---|---|---|
| R01 | Transformer une **HYPOTHÈSE** (`192.168.127.10:5001`) en cible d’envoi | 5 | documenter comme hypothèse ; aucun connect() expérimental avant Phase D validée |
| R02 | Coder une commande depuis un paquet partiellement identifié | 5 | règle de Phase D ; tests du Vérificateur qui rejettent les commandes « supposées » |
| R03 | Captures polluées (plusieurs actions mélangées) | 3 | une variable par capture ; journal horodaté de l’action humaine |
| R04 | Confondre heartbeat et commande | 4 | Capture 01 au repos obligatoire avant Capture 02 Clean |
| R05 | Tester automatiquement une séquence nouvellement découverte | 5 | validation humaine explicite ; `dry-run` par défaut |
| R06 | Hooking d’API trop tôt | 3 | uniquement si pistes non invasives épuisées, et avec accord |

---

## 3. Risques logiciel / exploitation

| ID | Risque | C | Mitigation |
|---|---|---|---|
| S01 | Automatisation UI fragile (focus, pop-up, langue, résolution) | 3 | V0 acceptable si robustesse prouvée ; logs d’échec ; pas de clic « au pixel » sans ancrage |
| S02 | Hosonsoft déjà ouvert / instance unique | 3 | détecter le processus avant lancement ; ne pas multiplier les instances |
| S03 | Faux positif « idle » | 4 | recouper UI + process + réseau + éventuellement capteur logiciel Hosonsoft |
| S04 | Timeout trop court → relance d’un clean | 4 | timeout = abandon + alerte, jamais relance aveugle |
| S05 | Service Windows qui démarre avant l’imprimante | 2 | retries bornés de **lecture d’état** seulement |
| S06 | Logs insuffisants pour diagnostiquer un incident machine | 3 | journaliser toute intention, tout refus sécurité, toute fin observée |
| S07 | Configuration codée en dur (mauvaise IP) | 4 | YAML externalisé ; pas d’IP dans le code |
| S08 | Mot de passe SSH dans un script | 3 | clés SSH ; `docs/remote-access.md` ; jamais de secret dans le dépôt |
| S09 | Accès distant compromis → commande imprimante | 4 | compte technique limité si possible ; pas d’écoute SSH exposée inutilement |
| S10 | Exécution depuis le poste de développement vers la carte, en contournant le PC DTF | 4 | le chemin opérationnel passe par le PC DTF ; pas de client sauvage depuis `XAVIER` |

---

## 4. Risques projet

| ID | Risque | C | Mitigation |
|---|---|---|---|
| P01 | Vouloir remplacer Hosonsoft trop tôt | 3 | succès = V0 robuste ; Phase C/D optionnelles |
| P02 | Développer un RIP inutile | 2 | réutiliser un `.prn` (ou équivalent) produit une fois par le RIP existant |
| P03 | Absence d’accès admin / SSH | 3 | question PO n°4 et n°8 ; plan B : présence physique ou autre outil distant déjà en place |
| P04 | Hosonsoft non automatisable (UI fermée, driver kernel) | 3 | alors seulement justifier Phase C ; pas d’impasse cachée |
| P05 | Deux postes, inventaire faux (observer `XAVIER` au lieu du PC DTF) | 4 | séparer clairement les observations par nom d’hôte |
| P06 | Product Owner indisponible pour valider une action dangereuse | 4 | pas d’action dangereuse par défaut ; le Vérificateur bloque |

---

## 5. Contrôles de sûreté à prévoir dans toute architecture

Ces contrôles sont des **exigences**, pas encore du code.

```text
dry-run          → décrit l’action, n’exécute rien de mécanique
simulation       → pas d’I/O imprimante
machine_busy     → doit être False
require_idle     → doit être True
max_clean_per_day
max_print_per_day (à décider)
timeout + abandon (pas de retry mécanique infini)
journalisation de chaque refus
```

Règle d’or :

```text
Une opération de maintenance ne doit jamais être lancée pendant une impression utilisateur.
```

---

## 6. Classification des actions

| Classe | Exemples | Autorisation Phase A | Autorisation V0 | Autorisation client direct |
|---|---|---|---|---|
| **READ ONLY** | lister process, netstat, lire config, status si lecture prouvée | oui | oui | seulement si trame de statut CONFIRMÉE |
| **UI KNOWN** | cliquer Clean dans Hosonsoft, comportement décrit | non (sauf observation humaine guidée) | oui, après description Clean | N/A |
| **ACTIVE COMMAND** | déplacement, clean protocolaire, impression brute | non | non | seulement commande identifiée + validation |
| **UNKNOWN PACKET** | payload hex « on essaie » | **jamais** | **jamais** | **jamais** |

---

## 7. Escalade

1. Toute **HYPOTHÈSE** de commande active → le Réalisateur ne code pas.
2. Toute observation ambiguë → l’Investigateur documente, le Vérificateur refuse la promotion en CONFIRMÉ.
3. Tout incident machine (bruit anormal, alarme, encre, collision) → **stop immédiat** de toute automatisation, consignation dans ce registre et dans les logs.

---

## 8. Revue

Ce registre doit être relu :

- avant le premier Clean automatisé (V0) ;
- avant la première capture d’une action mécanique (Phase C) ;
- avant le premier `connect()` applicatif vers la carte (Phase D).
