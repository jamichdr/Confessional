# Confessionnal Automatique

Ce projet implémente un système de confessionnal automatique qui capture des vidéos de petits mots pour des occasions spéciales comme des anniversaires ou des mariages. Le système détecte automatiquement les mouvements, lance un compte à rebours avant de commencer l'enregistrement, et enregistre des clips vidéo avec de l'audio. Après chaque enregistrement, le système fait une pause avant de relancer la détection de mouvement.

# Execution
Lors de l'exécution, le système commencera en attente de mouvement. Lorsque le mouvement est détecté, le compte à rebours commence, suivi de l'enregistrement. Après chaque enregistrement, une pause de 10 secondes est appliquée avant de revenir à l'état de détection de mouvement.

Ce système peut être utilisé pour capturer des messages vidéo lors de mariages, anniversaires, ou toute autre occasion spéciale, offrant une expérience amusante et interactive pour les invités.
## Fonctionnalités

1. **Détection de Mouvement** :
   - Le système utilise la webcam pour détecter les mouvements.
   - Lorsqu'un mouvement est détecté, le système démarre un compte à rebours de 20 secondes.

2. **Compte à Rebours** :
   - Un compte à rebours de 20 secondes est affiché en plein écran.
   - Pendant ce compte à rebours, un fond rouge avec le temps restant est affiché.

3. **Enregistrement Vidéo et Audio** :
   - Après le compte à rebours, l'enregistrement commence automatiquement.
   - L'enregistrement continue tant qu'il y a du mouvement détecté.
   - Si aucun mouvement n'est détecté pendant 5 secondes, l'enregistrement s'arrête.

4. **Point Rouge Clignotant** :
   - Un point rouge clignotant apparaît en haut à gauche de l'affichage en temps réel pour indiquer que l'enregistrement est en cours.
   - Ce point n'apparaît pas dans la vidéo finale.

5. **Fusion de la Vidéo et de l'Audio** :
   - Après l'enregistrement, les fichiers vidéo et audio sont fusionnés en un fichier MP4 unique.

6. **Pause Après Enregistrement** :
   - Une pause de 10 secondes est appliquée après chaque enregistrement avant de relancer la détection de mouvement.
   - Pendant cette pause, le système affiche un message "Pause...".

7. **Nom des Fichiers** :
   - Les fichiers enregistrés sont nommés selon le format `CONFESSDDMMYYYY-HHMM.mp4`, où `DDMMYYYY-HHMM` représente le jour, le mois, l'année, l'heure et les minutes de l'enregistrement.

## Prérequis

- Python 3.x
- Bibliothèques Python : `opencv-python`, `pyaudio`, `numpy`, `moviepy`
- Une webcam fonctionnelle

## Installation des Dépendances

Vous pouvez installer les dépendances requises avec pip :

```bash
pip install opencv-python pyaudio numpy moviepy
