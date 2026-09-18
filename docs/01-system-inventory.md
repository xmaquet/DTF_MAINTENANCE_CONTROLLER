# 01 — Inventaire système

**Date :** 2026-09-18  
**Périmètre :** ce qui est connu, observé, ou seulement hypothétique  
**Règle :** toute case non vérifiée sur la machine concernée reste **HYPOTHÈSE** ou **À CONFIRMER**

Cet inventaire sera mis à jour au fil des observations. Il ne constitue **pas** une autorisation d’agir.

---

## 1. Poste de développement (dépôt actuel)

| Élément | Valeur | Statut |
|---|---|---|
| Nom d’hôte | `XAVIER` | **OBSERVÉ** 2026-09-18 |
| OS | Windows 10 Home, version 2009, build 26200 | **OBSERVÉ** |
| Python | 3.13.14 | **OBSERVÉ** |
| Git | 2.55.0.windows.3 | **OBSERVÉ** |
| IPv4 Wi-Fi (réseau actuel) | `192.168.10.126` | **OBSERVÉ** 2026-09-18 |
| IPv4 Ethernet 2 | `192.168.56.1` | **OBSERVÉ** — **HYPOTHÈSE :** interface VirtualBox / host-only |
| Contenu du dépôt au cadrage | vide | **OBSERVÉ** |
| Hosonsoft / PrintExp sur ce poste | inconnu | **À CONFIRMER** |
| Accès réseau vers le PC DTF | ICMP vers `192.168.10.129` : 2/2 réponses, 4–5 ms, TTL=128 | **OBSERVÉ** depuis `XAVIER` le 2026-09-18 — **DÉCLARÉ (PO)** : cet hôte est le PC imprimante |
| Accès SSH vers le PC DTF | `ssh user@192.168.10.129` par clé | **CONFIRMÉ** 2026-09-18 depuis `XAVIER` |

**HYPOTHÈSE :** le développement principal se fait depuis ce poste (`XAVIER`), distinct du PC dédié à l’imprimante.

---

## 2. PC DTF (cible d’exploitation)

Aucune observation directe n’a encore été faite sur cette machine.

| Élément | Valeur brief | Statut |
|---|---|---|
| Rôle | PC Windows dédié à l’imprimante | **HYPOTHÈSE** (brief) |
| OS / édition / build | Windows 10 Pro, build 19045.6466 | **DÉCLARÉ (PO)** 2026-09-18 — **HYPOTHÈSE :** 22H2 ; non lu via `winver` / `Get-ComputerInfo` sur l’hôte |
| Nom d’hôte | `DESKTOP-MANFYQB` | **CONFIRMÉ** 2026-09-18 via SSH `ipconfig` / `hostname` |
| Compte Windows / utilisateur technique | `DESKTOP-MANFYQB\user` | **DÉCLARÉ (PO)** : administrateur ; SSH : `user@192.168.10.129` |
| Adresse IP du PC (lien imprimante) | `192.168.127.3/24` statique, Intel I217-LM, MAC `98-90-96-AA-05-6F`, passerelle configurée `192.168.127.1` | **CONFIRMÉ** SSH `ipconfig` — `192.168.127.1` **absente** de l’ARP |
| Interface Wi-Fi (admin / local) | Realtek 8812BU USB, `192.168.10.129/24` DHCP, GW/DNS `192.168.10.254`, suffixe `box.freepro.com` | **CONFIRMÉ** |
| Adresse IP Wi-Fi / admin du PC DTF | `192.168.10.129` | **CONFIRMÉ** |
| Hosonsoft / PrintExp | `PrintExp_X64.exe` (UI **Hosonsoft-PrintExp**) | **CONFIRMÉ** |
| Version exacte Hosonsoft / PrintExp | dossier `C:\InkONE\PrintExp_X64_5.8.1.1.29_Unicode_20240508\` ; UI `5.8.1.1.29.R.Unicode` ; FileDescription `Hosonsoft-PrintExp` ; ProductVersion fichier `5.7.0.35` | **CONFIRMÉ** chemin / **OBSERVÉ** versions |
| Chemin d’installation | `C:\InkONE\PrintExp_X64_5.8.1.1.29_Unicode_20240508\` | **CONFIRMÉ** |
| Python installé | 3.13.7 user (`%LOCALAPPDATA%\Programs\Python\Python313\`) ; `py -3` OK | **OBSERVÉ** 2026-09-18 via SSH |
| Wireshark installé | non, pas à la connaissance du PO | **DÉCLARÉ (PO)** 2026-09-18 — non vérifié dans Programmes / `Get-Package` |
| OpenSSH Server | service `sshd` Running | **DÉCLARÉ (PO)** 2026-09-18 ; TCP 22 **OBSERVÉ** depuis `XAVIER` |
| Process Explorer / Process Monitor | inconnu | **À CONFIRMER** |
| RIP (lequel, version, chemin) | InkOne V2.11.0 — `C:\Program Files (x86)\InkOne\InkOne.exe` ; installer `C:\InkONE\InkOne+V2.11.0.09262024-x64.exe` | **CONFIRMÉ** (registre Uninstall + fichiers) ; processus `InkOne.exe` **non vu** au moment A1 ; `MtFlatbedPrinterApp.exe` **était** en cours |
| Sous tension permanente | possible selon brief | **HYPOTHÈSE** |

---

## 3. Imprimante et carte de contrôle

| Élément | Valeur | Statut |
|---|---|---|
| Modèle imprimante | Inkone DM3 | **HYPOTHÈSE** (brief Product Owner — non vérifié sur plaque / firmware) |
| Carte de contrôle | type Hoson | **HYPOTHÈSE** (brief) |
| Liaison physique | Ethernet PC ↔ imprimante | **DÉCLARÉ (PO)** 2026-09-18 — câble direct vs switch **non précisé** |
| IP carte Hoson (réelle) | `192.168.127.10` MAC `00-0a-35-18-54-bb` (ARP) ; suffixe Chip ID UI `351854BB` | **CONFIRMÉ** présence ARP + corrélation MAC / Chip ID |
| Port de contrôle réellement utilisé | TCP `5001` | **CONFIRMÉ** : `PrintExp_X64.exe` PID 23912, `192.168.127.3:55104 → 192.168.127.10:5001` ESTABLISHED |
| Réception RIP locale | `NWReceive.exe` écoute `127.0.0.1:9100` | **CONFIRMÉ** ; `Project.ini` `[TCP_IP] ADDR=127.0.0.1 PORT=9100` |
| Port 9100 exposé sur le LAN | non | **OBSERVÉ** : bind **localhost seulement** |
| Firmware carte (UI) | `CSD_2.75_DL_XP600_1HWC_5.7.6.5.X_20240220` | **OBSERVÉ** si connecté |
| Serial Main Board | `00EB-203241003793 (2.75_cable)` | **OBSERVÉ** si connecté |
| Tête (log Check 15:24) | `XP600_One Heads 4C1W` ; motif Check 166,51×25,40 mm | **OBSERVÉ** dans `Log[2026_09_18].txt` |
| Nombre de têtes / canaux (CMJN + blanc) | CMJN + blanc évoqués pour le motif | **HYPOTHÈSE** fonctionnelle |

### Architecture réseau — A1 SSH 2026-09-18

```text
XAVIER 192.168.10.126
        |
        | Wi-Fi 192.168.10.0/24  GW box 192.168.10.254
        | SSH CONFIRMÉ
        v
DESKTOP-MANFYQB
  Wi-Fi  192.168.10.129     CONFIRMÉ
  Eth    192.168.127.3/24   CONFIRMÉ  Intel I217-LM
        |
        | TCP ESTABLISHED  PrintExp_X64.exe → :5001
        v
192.168.127.10              CONFIRMÉ ARP 00-0a-35-18-54-bb
        (carte Hoson / FPGA Xilinx OUI — HYPOTHÈSE OUI)

RIP / job  →  127.0.0.1:9100  NWReceive.exe   CONFIRMÉ
```

**CONFIRMÉ (A1, lecture seule) :**

- deux interfaces actives : Ethernet imprimante `192.168.127.3/24` (IP statique) et Wi-Fi admin `192.168.10.129/24` (DHCP box Free) ;
- `192.168.127.10` est dans l’ARP de l’interface Ethernet ; MAC `00-0a-35-18-54-bb` correspond au suffixe Chip ID UI `351854BB` ;
- `PrintExp_X64.exe` maintient une connexion TCP vers `192.168.127.10:5001` (Hosonsoft ouvert / connecté) ;
- `Project.ini` : `DEFAULT_COMM_TYPE=1` (TCP), `ServerIP=192.168.127.10`, `ServerPort=5001` ;
- `NWReceive.exe` (même dossier PrintExp) écoute `127.0.0.1:9100` ; `Project.ini` `[TCP_IP] ADDR=127.0.0.1 PORT=9100` ;
- `sshd` écoute `0.0.0.0:22` (donc aussi sur `192.168.127.3` — à restreindre plus tard).

**Toujours interdit :** envoyer quoi que ce soit vers `192.168.127.10:5001` depuis `XAVIER` ou un client expérimental.

**Non ping :** `192.168.127.10` déjà vu en ARP **et** en session TCP ; `192.168.127.1` (passerelle Ethernet) **n’est pas** dans l’ARP — **HYPOTHÈSE** passerelle fantôme / inutilisée. Aucun ping A1.

**HYPOTHÈSE RIP :** InkOne V2.11.0 envoie vers `127.0.0.1:9100` via `NWReceive` / `MtTcpSender.dll` / `MtPrintEngine_Port.dll`. Driver observé : `C:\InkONE\DTF-HS-1H-XP600.mt_driver`. Un PRN existe déjà : `C:\InkONE\ERASMART Quality Evaluation.prn` (évaluation, pas forcément le motif d’entretien).

**InkOne.exe** n’était pas dans la liste des processus au moment A1. **HYPOTHÈSE :** l’UI RIP en cours était `MtFlatbedPrinterApp.exe`.

**Autre logiciel InkOne OBSERVÉ :** `C:\Program Files (x86)\InkOne\MtFlatbedPrinterApp.exe` (processus distinct, hors socket 5001).

---

## 4. Logiciel Hosonsoft / PrintExp

### 4.1 Connexion : comparaison déconnecté vs connecté (2026-09-18)

**DÉCLARÉ (PO) :** la première capture a été faite **imprimante déconnectée** ; les captures suivantes **imprimante connectée**.

| Champ | Déconnecté | Connecté | Lecture |
|---|---|---|---|
| MB Chip ID | `0000-00000000-00000000 (0000)` | `00EB-408D0A25-351854BB (2.75_cable)` | **OBSERVÉ** |
| MB Serial Number | `0000-(0000)` | `00EB-203241003793 (2.75_cable)` | **OBSERVÉ** |
| MB Logic Version | `0.0.0.0.0` | `1.1.1.2.0.5001` | **OBSERVÉ** |
| MB Program Version | `0.0.0.0.0.R.` | `5.8.1.1.20.R.Unicode` | **OBSERVÉ** |
| MB Firmware Configure Info | (vide) | `CSD_2.75_DL_XP600_1HWC_5.7.6.5.X_20240220` | **OBSERVÉ** (chaîne complète dans l’écran Version Info) |
| MB Firmware Parameter Info | (vide) | `CSD_2.75_DL_XP600_1HWC_5.7.6.5.X_20240220` | **OBSERVÉ** |
| Head Board 1 | (absent) | Chip `0316-00793504-142B1792` ; Logic `1.0.1.0.12` ; Program `5.1.0.0.3.D.` | **OBSERVÉ** seulement si connecté |
| Extern Board 1 | (absent) | Logic `0.0.0.0.R.` ; Program `0.6.0.11.13.R.` | **OBSERVÉ** |
| Software Version | `5.8.1.1.29.R.Unicode` | identique | **OBSERVÉ** — ne dépend pas de la carte |
| Device Manager Version | `5.8.1.1.27.R.BS` | identique | **OBSERVÉ** |
| Data Process Version | `5.8.1.1.27.R.BS_U` | identique | **OBSERVÉ** |
| Machine status code1 | `1825` | `1825` | **OBSERVÉ** — **inchangé** |
| Machine status code2 | `F(0)-M(0)` | `F(235)-M(235)` | **OBSERVÉ** |
| Machine status code3 | `F(0)-M(0)` | `F(0)-M(1)` | **OBSERVÉ** |
| Machine status code4 | `0` | `2` | **OBSERVÉ** |
| Machine status code5 | `2000-01-01 01:01:01` | `2026-09-18 22:37:47` | **OBSERVÉ** |

Captures archivées :

- [evidence/hoson-detailed-version-info-2026-09-18.png](evidence/hoson-detailed-version-info-2026-09-18.png) — déconnecté
- [evidence/hoson-detailed-version-info-connected-2026-09-18.png](evidence/hoson-detailed-version-info-connected-2026-09-18.png) — connecté (Details)
- [evidence/hosonsoft-ui-version-info-connected-2026-09-18.png](evidence/hosonsoft-ui-version-info-connected-2026-09-18.png) — écran principal Version Info

**CONFIRMÉ :** les champs Main Board / Head Board à zéro ou absents, et la date `2000-01-01`, correspondent à l’état **déconnecté** déclaré par le PO. Ils se peuplent lorsque l’imprimante est **connectée**. Ce n’est **pas** un firmware `0.0.0.0`.

**HYPOTHÈSE :** `code1 = 1825` n’est **pas** un indicateur de connexion (identique dans les deux états).

**HYPOTHÈSE :** `code2 F(n)-M(n)` et `code4` varient avec l’état machine ; signification précise **inconnue**. Ne pas en déduire de commande.

**HYPOTHÈSE :** `CSD_2.75_DL_XP600_1HWC_…` désigne une config tête **XP600**, câble **2.75**, 1 tête / canal blanc (`1HWC`). Lecture du **nom de firmware**, pas une ouverture de capot.

**HYPOTHÈSE :** Extern Board Logic `0.0.0.0.R.` même connecté = carte externe absente, inactive, ou non rapportée.

**HYPOTHÈSE :** horloge `22:37:47` vs heure locale de session ~17:13 UTC+2 = fuseau carte/PC différent (souvent UTC+8 sur matériels Hoson) **ou** horloge mal réglée.

Logiciel PC vs firmware carte :

- Hosonsoft (PC) : `5.8.1.1.29.R.Unicode`
- MB Program (carte) : `5.8.1.1.20.R.Unicode`

Ce n’est **pas** la même build. **HYPOTHÈSE :** le logiciel PC et le programme carte sont appariés mais pas identiques.

### 4.2 Chrome UI Hosonsoft (connecté)

**OBSERVÉ** sur l’écran principal (titre **Hosonsoft**) :

- menus : File, Print, Setting, Adjust, Voltage, Advance
- barre : OpenFiles, Print, Pause, Cancel, **Check**, **Clean**, Flash, Margin, Left, Right, Ahead, Back, X Reset, Move Y2, Spot, Load, Save
- volet gauche : Factory, **Version Info** (sélectionné), **Rip Print**, Advance
- boutons Version Info : Upgrade, Refresh, Details

**HYPOTHÈSE V0 :** le bouton **Clean** de cette barre est l’entrée d’entretien à automatiser (UI), pas une trame réseau. Left / Right / Ahead / Back / X Reset / Move Y2 sont des **ACTIVE COMMAND** mécaniques — hors V0 tant que non validés.

**CONFIRMÉ dump Win32 2026-09-18 18:33 (session 1) :** UIA = 0 enfant. Boutons = `Button` Win32. **Clean** id **11030**, **Check** id **11029**, tous deux enabled. Print/Pause/Cancel **disabled** (idle). Fenêtre **minimisée** (`-32000`). Weak/Normal/Strong **absents** (menu pas ouvert). Détail : [printexp-toolbar-map.md](evidence/printexp-toolbar-map.md).

**CONFIRMÉ dry-run 18:37 (PrintExp restauré, 1920×1040) :** `skip` ERASMART 15:31. Coords écran : Check `(393,76)-(474,157)` ; Clean `(498,75)-(579,156)`. `bandeau_idle_hypothese=True`. Aucun clic. Deux autres `Flash` invisibles (ids 1042, 1084) — V0 ciblera uniquement `vis=True` + ids 11030/11029.

**CONFIRMÉ A1 :** le chrome **Hosonsoft** est le produit `PrintExp`. Processus :

- `C:\InkONE\PrintExp_X64_5.8.1.1.29_Unicode_20240508\PrintExp_X64.exe` — UI + TCP `192.168.127.10:5001`
- `...\NWReceive.exe` — écoute `127.0.0.1:9100` (entrée RIP)
- DLLs notables : `HsSocketClient.dll`, `TcpIp.dll`, `HSKRipFile.dll`, `KMaintain.dll`

Raccourci Bureau : `PrintExp_X64.exe - Raccourci.lnk`

Config : `Project.ini` (modifié 2026-09-18 17:12). Dossiers `Config\`, `Log\`, `temp\`. Aperçus jobs : `~section*.prn.bmp`.

### 4.3 Fonctions déclarées / restantes

### 4.5 Motif de test — déclaration Product Owner (2026-09-18)

**DÉCLARÉ (PO) :** deux déclencheurs possibles, **même type de motif** :

1. bouton **Check** dans Hosonsoft ;
2. bouton physique **nozzle check** sur l’imprimante.

Motif : **patterns de chaque couleur**, « carré avec petits traits à l’intérieur ».

**HYPOTHÈSE :** Check Hosonsoft = équivalent logiciel du nozzle check physique (pas un job RIP).

**HYPOTHÈSE V0.1 :** automatiser **Check** dans l’UI, pas le bouton machine. Le bouton physique n’est pas pilotable sans protocole carte.

**Non établi :** le Check Hosonsoft couvre-t-il le blanc ; fichier RIP `maintenance-pattern.prn` encore nécessaire ou non ; critère de fin d’un Check (probablement le même bandeau — **HYPOTHÈSE**).

Un fichier RIP unique reste un plan B si Check ne suffit pas à l’entretien (blanc, surface, etc.). Pas de RIP maison.

### 4.4 Clean — déclaration Product Owner (2026-09-18)

**DÉCLARÉ (PO) :**

- trois niveaux : **weak**, **normal**, **strong** ;
- plus le niveau est élevé, plus **la pompe tourne longtemps** ;
- le **chariot se déplace** avec **montée du capping** (station de capuchonnage).

**Non établi :** durées approximatives par niveau.

**DÉCLARÉ (PO) — fin d’opération :** le Clean est considéré terminé lorsque **le chariot revient** et qu’**Hosonsoft rend la main sur le bandeau** (boutons de la barre à nouveau utilisables).

**HYPOTHÈSE V0 :** clic **Clean** → menu 3 lignes → **Normal** ou **Strong** → attendre bandeau. Check ensuite, même bandeau.

**DÉCLARÉ (PO) — politique d’entretien visée (tous les jours, week-end inclus) :**

```text
Tous les jours à 20:00 (heure Windows PC DTF — HYPOTHÈSE fuseau)
        |
        +-- print EN COURS à 20:00     → SAUTER
        +-- print utilisateur aujourd'hui → SAUTER
        |     job InkOne OU .prn PrintExp (ex. ERASMART)
        |     (réinit aussi le compteur strong 3 jours)
        |     Check / Clean NE comptent PAS
        |
        +-- sinon
              |
              +-- 3 jours sans print → Clean STRONG puis Check
              +-- sinon              → Clean NORMAL puis Check
```

- le Check laisse une **trace horodatée** ;
- **Weak** non retenu ;
- **UI Clean CONFIRMÉE :** menu **3 lignes** après clic Clean.

**Gel métier 2026-09-18 :** règle + geste UI figés. Plan : [05-v0-dry-run-plan.md](05-v0-dry-run-plan.md). **Aucun clic réel.**

**HYPOTHÈSE V0 :** le Check auto n’est **pas** un print utilisateur et **ne** réinitialise **pas** le compteur 3 jours.

**Interdit :** lancer un Clean automatisé sans attendre la restitution du bandeau, et sans timeout d’abandon.

---

## 5. Chaîne d’impression (RIP → Hosonsoft → carte)

**HYPOTHÈSE** de chaîne, à infirmer ou confirmer :

```text
InkOne V2.11.0  CONFIRMÉ (registre)
        |
        | HYPOTHÈSE : TCP 127.0.0.1:9100
        v
NWReceive.exe     CONFIRMÉ
        |
        v
PrintExp_X64.exe  CONFIRMÉ
        |
        | TCP 192.168.127.10:5001
        v
carte Hoson
```

`Project.ini` déclare aussi `E:\PrnTempData` comme dossier temp PRN (**existence non vérifiée**).

Formats / vecteurs à rechercher (aucun n’est confirmé) :

| Vecteur | Statut |
|---|---|
| Fichier `.prn` | **HYPOTHÈSE** — solution privilégiée si le RIP peut le produire une fois |
| Raster propriétaire | **HYPOTHÈSE** |
| Spool Windows | **HYPOTHÈSE** |
| TCP localhost | **HYPOTHÈSE** |
| Port 9100 | **HYPOTHÈSE** générique |
| Fichiers temporaires | **HYPOTHÈSE** |

**Décision de cadrage :** ne pas développer de RIP ni d’interpréteur de format tant qu’un fichier de maintenance unique, produit par le RIP existant, peut être réutilisé.

---

## 6. Réseau — ce qu’il faudra inventorier sur le PC DTF

Sans observation, aucune topologie n’est retenue.

À collecter (Phase A) :

- `Get-NetAdapter`, `Get-NetIPAddress`, `Get-NetRoute`
- `arp -a`
- `Get-NetTCPConnection` / `netstat -ano`
- association PID ↔ exécutable
- VLAN / lien dédié vs réseau partagé
- présence d’un switch, d’un routeur, ou d’un câble direct
- firewall Windows (règles Hosonsoft)
- résolution DNS éventuelle du contrôleur

**HYPOTHÈSE à traiter avec prudence :** deux réseaux distincts sur le PC DTF (Ethernet `192.168.127.0/24` vers la carte, Wi-Fi vers l’admin). Le routage Windows ne doit pas exposer la carte Hoson au poste de développement. L’investigation distante cible le **PC DTF**, pas `192.168.127.10`.

---

## 7. Outils de diagnostic attendus (PC DTF)

| Outil | Rôle | Présence |
|---|---|---|
| PowerShell | inventaire, netstat, services | **À CONFIRMER** (probable sur Windows moderne) |
| Wireshark | captures isolées Phase C | **DÉCLARÉ (PO)** : absent (pas à sa connaissance) — pas requis avant Phase C |
| OpenSSH Server | administration depuis le poste de développement | **DÉCLARÉ (PO)** : Running ; TCP 22 **OBSERVÉ** depuis `XAVIER` |
| Python | 3.13.7 user — UI controller dry-run | **OBSERVÉ** ; fenêtre ouverte **DÉCLARÉ (PO)** 18:25 |
| Process Explorer / Process Monitor | processus, fichiers, registre | **À CONFIRMER** |
| AutoHotkey / pywinauto | V0 GUI | **À CONFIRMER** (installation ultérieure possible) |

---

## 8. Dépôt logiciel (ce workspace)

**OBSERVÉ** au 2026-09-18 :

- aucun code source ;
- aucun fichier de configuration ;
- aucun capture réseau ;
- documentation de cadrage créée dans `docs/`.

Arborescence cible (prévue, non implémentée au-delà du cadrage) :

```text
dtf-maintenance/
├── src/           # scheduler, hoson, printexp, maintenance, safety, logging
├── captures/
├── config/
├── docs/
├── tools/
├── tests/
└── README.md
```

---

## 9. Synthèse — ce qui est réellement connu

**CONFIRMÉ :** Hosonsoft UI vide (MB à zéro, date `2000-01-01`) ⇔ imprimante **déconnectée** ; champs carte / tête peuplés ⇔ **connectée** (déclaration PO + deux captures).

**DÉCLARÉ (PO) 2026-09-18 :** Windows 10 Pro build 19045.6466 ; Ethernet `192.168.127.3` → UI Hoson `192.168.127.10:5001` ; PC imprimante joignable en `192.168.10.129`.

**OBSERVÉ (UI Hoson, connecté) :** Software `5.8.1.1.29.R.Unicode` ; MB Program `5.8.1.1.20.R.Unicode` ; firmware `CSD_2.75_DL_XP600_1HWC_5.7.6.5.X_20240220` ; bouton **Clean** visible ; entrée **Rip Print**.

**OBSERVÉ :** `XAVIER` `192.168.10.126` ; ICMP `192.168.10.129` OK (TTL=128).

**HYPOTHÈSE structurante :** deux réseaux — admin `192.168.10.0/24`, lien imprimante `192.168.127.0/24`. V0 = cliquer Clean dans Hosonsoft, pas parler à `192.168.127.10` depuis `XAVIER`.

**CONFIRMÉ A1 (SSH, 2026-09-18) :** `PrintExp_X64.exe` → `192.168.127.10:5001` ; ARP MAC `00-0a-35-18-54-bb` ; `NWReceive.exe` sur `127.0.0.1:9100` ; install `C:\InkONE\PrintExp_X64_5.8.1.1.29_Unicode_20240508\`.

**Toujours interdit :** client vers `192.168.127.10` depuis `XAVIER`. V0 = UI PrintExp (Clean / Check).

### 4.6 Détection print — A2 logs (2026-09-18, lecture seule)

Sources **OBSERVÉES** :

| Source | Chemin | Rôle |
|---|---|---|
| Jobs InkOne | `C:\Program Files (x86)\InkOne\Jobs\` + `history.json` | un dossier par job ; dernier : `…_44` le **2026-09-17 21:13** |
| PrnList | `C:\Program Files (x86)\InkOne\PrnList\*.prn` | dernier PRN RIP : `Agathe_DTF_30x100_150ppp (17).prn` **2026-09-17 21:13** |
| Log PrintExp quotidien | `…\Log\main\Log[YYYY_MM_DD].txt` | **OBSERVÉ** UTF-16 LE BOM (`FF FE`) ; `Log[2026_09_18].txt` |
| rp.log | `…\Log\rp.log` | UTF-16 ; `CNWReceive::Init` (récepteur 9100) |

**CONFIRMÉ (corrélation 17/09) :** un print InkOne laisse un job `Jobs\…`, un `.prn` dans `PrnList`, et dans le log PrintExp : `~section0.prn`, `PRNPrintExit()`, `ReceiveSignal Moving/Stop`.

**CONFIRMÉ (PO) :** vers 15:24, Clean et Check ; **ensuite un `.prn` lancé depuis PrintExp**.

**CONFIRMÉ (log 15:28–15:31) :** `ERASMART Quality Evaluation.prn` (fichier déjà présent dans `C:\InkONE\`). **Pas** d’entrée nouvelle dans InkOne `PrnList` / `Jobs`. Extrait : [erasmart-log-lines.txt](evidence/erasmart-log-lines.txt).

**OBSERVÉ 2026-09-18 18:26 dry-run :** `would_clean_normal` à tort — le parser lisait le log en UTF-8/latin-1, donc 0 `.prn` vu, et retombait sur `PrnList` Agathe **17/09**. Correction : lecture UTF-16 + noms `.prn` avec espaces.

**CONFIRMÉ 18:30 (dry-run, après correctif) :** `skip | print utilisateur aujourd'hui (15:31)`. Aucun clic PrintExp.

**CONFIRMÉ :** un print utilisateur peut donc être :
1. un job **InkOne** (`PrnList` / `Jobs`) ;
2. un **OpenFiles** PrintExp d’un `.prn` existant (ex. ERASMART).

`PrnList` **seul** est insuffisant. Le Check (15:24, 166×25 mm, `GO-Print`) **n’est pas** ce `.prn`.

**CONFIRMÉ (UI Clean) :** il **faut choisir** parmi les **3 niveaux** Weak / Normal / Strong (fenêtre ou liste). V0 devra cibler **Normal** ou **Strong**, jamais un clic Clean sans niveau.

**HYPOTHÈSE (print en cours) :** `GO-Print` / fichier `.prn` nommé, distinct du petit motif Check.

**HYPOTHÈSE (print en cours) :** job InkOne / `~section*.prn` dans `temp\<timestamp>\` / `ReceiveSignal Moving` associé à ce temp RIP — pas `GO-Print` seul (Check).

**OBSERVÉ 18:05 :** `Auto Microwave Pump Ink` / `GO-CleanInkStack` sans Clean demandé dans A2. **HYPOTHÈSE :** pompe auto au repos. Le token `Clean` du log ≠ Clean utilisateur à lui seul.

**Interdit :** parser ces logs pour envoyer une commande. Lecture seulement.
