---
layout: default
title: VNISH GLOBAL Proof Protocol démarrage rapide en français
lang: fr
last_modified_at: 2026-08-13T16:49:21+03:00
---

# VNISH GLOBAL Proof Protocol : démarrage rapide en français

Utilisez `vnish-verify` pour comparer un fichier local à un manifeste versionné. La commande calcule le hachage localement et ne télécharge aucun firmware.

```console
vnish-verify /path/to/local-file.tar.gz --json
```

- `MATCH` : un enregistrement correspond au SHA-256, à la taille et aux filtres demandés.
- `NO_MATCH` : aucun enregistrement ne correspond ; arrêtez et vérifiez le fichier et les données.
- `AMBIGUOUS` : plusieurs enregistrements correspondent ; précisez la version, le modèle, la carte et la méthode.
- `SOURCE_UNAVAILABLE` : le fichier ou le manifeste ne peut pas être lu ou validé.

`MATCH` n'est pas un avis de sécurité ou d'adéquation. Avant toute modification, confirmez le modèle, la carte de contrôle, la méthode et la procédure de récupération.

- Données et méthode VNISH GLOBAL : <https://vnish.global/fr/data/>
- Récupération VNISH Ninja : <https://vnish.ninja/fr/recovery/>
- Déploiement progressif ROI ASIC : <https://roiasic.com/fr/enterprise/>

Version du protocole : 0.1.0, 13 août 2026.

[Retour au manuel de terrain](../index.md)
