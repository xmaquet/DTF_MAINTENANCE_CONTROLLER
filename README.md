# DTF Maintenance Controller

Outil d’entretien périodique pour une imprimante DTF **Inkone DM3** aujourd’hui pilotée par **Hosonsoft / PrintExp**.

**Statut :** Phase A/B — V0 dry-run (UI PrintExp, aucun clic réel). Aucun client TCP vers la carte.

## Principe

```text
observer → comprendre → reproduire → automatiser
```

Une automatisation robuste d’Hosonsoft (V0) est un succès. Le remplacement du protocole n’est pas un objectif en soi.

Les faits sont marqués **HYPOTHÈSE**, **OBSERVÉ** ou **CONFIRMÉ**. Les adresses du type `192.168.127.10:5001` restent des hypothèses tant qu’elles n’ont pas été vérifiées sur **cette** machine.

## Documents

| Document | Contenu |
|---|---|
| [docs/00-project-context.md](docs/00-project-context.md) | Mission, phases, rôles, philosophie |
| [docs/01-system-inventory.md](docs/01-system-inventory.md) | Inventaire (très majoritairement à confirmer) |
| [docs/02-investigation-plan.md](docs/02-investigation-plan.md) | Plan d’investigation Phase A |
| [docs/03-risk-register.md](docs/03-risk-register.md) | Risques machine et sûreté |
| [docs/05-v0-dry-run-plan.md](docs/05-v0-dry-run-plan.md) | Plan V0 dry-run, gel métier 20:00 |

## Ce dépôt

## Lancer (dry-run)

Sur le **PC DTF**, session bureau, Python 3 installé :

```text
python run_controller.py
```

**Pas de fenêtre = pas de maintenance.** `dry_run` est à `true` : aucun clic PrintExp.
