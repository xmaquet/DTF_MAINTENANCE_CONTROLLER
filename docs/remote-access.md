# Accès distant — PC DTF

**Cible :** PC imprimante `DESKTOP-MANFYQB`  
**Adresse d’admin :** `192.168.10.129` — **DÉCLARÉ (PO)** ; ICMP **OBSERVÉ** depuis `XAVIER`  
**OS :** Windows 10 Pro, build 19045.6466 — **DÉCLARÉ (PO)**  
**Compte :** `DESKTOP-MANFYQB\user` — **DÉCLARÉ (PO)** administrateur  
**SSH :** `user@192.168.10.129`  
**Interdit :** viser `192.168.127.10` (carte imprimante) depuis le poste de développement

---

## État

| Étape | Statut |
|---|---|
| ICMP vers `192.168.10.129` | **OBSERVÉ** (puis `Test-NetConnection` 2026-09-18 : TCP 22 OK, ping cette fois **False**) |
| OpenSSH Server installé | **DÉCLARÉ (PO)** : service **Running** |
| TCP 22 depuis `XAVIER` | **OBSERVÉ** : `TcpTestSucceeded = True` vers `192.168.10.129:22` |
| Authentification par clé | **CONFIRMÉ** 2026-09-18 depuis `XAVIER` : `ssh user@192.168.10.129` → `desktop-manfyqb\user` / `DESKTOP-MANFYQB` |
| Empreinte hôte actuelle | ED25519 `SHA256:KPHrgywRkY+6TeKQsFOJNtDYTiKgA6kj6y/E4gjpwok` — **OBSERVÉ** (nouvelle, OpenSSH vient d’être installé) |
| Écoute limitée à `192.168.10.129` (pas sur `192.168.127.3`) | pas encore |

Aucun mot de passe ne doit être stocké dans un script ou dans ce dépôt.

---

## 1. Installer OpenSSH Server (sur le PC imprimante)

À faire **sur `192.168.10.129`**, avec le compte administrateur déjà utilisé.

### Variante A — Paramètres Windows (recommandée)

1. Ouvre **Paramètres** → **Applications** → **Fonctionnalités facultatives**  
   (ou *Apps* → *Optional features* si l’UI est en anglais).
2. Clique **Afficher les fonctionnalités** / **Add a feature**.
3. Cherche **OpenSSH Server** (pas seulement *OpenSSH Client*).
4. Installe, attends la fin.
5. Ouvre **services.msc**.
6. Trouve **OpenSSH SSH Server**.
7. Démarrage : **Automatique**.
8. Démarre le service s’il est arrêté.

### Variante B — PowerShell **en administrateur**

```powershell
Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH*'
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Start-Service sshd
Set-Service -Name sshd -StartupType Automatic
Get-Service sshd
Get-NetFirewallRule -Name *ssh*
```

**Attendu :** `sshd` en état **Running**, type **Automatic**. Windows crée en général une règle de pare-feu **OpenSSH SSH Server (sshd)**.

Ne pas tester `ssh` avec mot de passe depuis `XAVIER` tant que le nom de compte n’est pas connu. La clé SSH est l’étape suivante.

---

## 2. Clé SSH (en cours)

Le compte `user` est **administrateur**. Sur OpenSSH Windows, les clés admin se placent ici (pas dans `C:\Users\user\.ssh\authorized_keys`) :

```text
C:\ProgramData\ssh\administrators_authorized_keys
```

Procédure sur le **PC imprimante**, PowerShell **administrateur** : créer le fichier, coller la clé **publique** du poste `XAVIER`, restreindre les ACL (sinon `sshd` ignore le fichier).

La clé privée reste sur `XAVIER`. Aucune clé dans ce dépôt.

Puis, depuis `XAVIER` :

```text
ssh user@192.168.10.129
```

**CONFIRMÉ** 2026-09-18 : connexion par clé OK (`whoami` / `hostname` distants).

Note : une ancienne empreinte pour `192.168.10.129` existait déjà dans `known_hosts` (même clé que `192.168.10.124` / `192.168.1.21`). Elle a été retirée (`ssh-keygen -R`) car OpenSSH Server vient d’être installé et a généré de nouvelles clés hôte. **HYPOTHÈSE :** réutilisation d’IP ou réinstall SSH, pas un MITM.

## 3. Suite prévue (après connexion par clé)

- Restreindre `ListenAddress` à `192.168.10.129` pour ne pas écouter sur `192.168.127.3`.
- Désactiver l’authentification par mot de passe SSH.

---

## 3. Commandes de diagnostic (plus tard)

Depuis `XAVIER`, uniquement vers le PC, jamais vers la carte :

```text
ping 192.168.10.129
ssh <compte>@192.168.10.129
```
