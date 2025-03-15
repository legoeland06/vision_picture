# Analyseur d'Images avec API Gemini

Ce projet est une application Python qui utilise l'API Gemini pour analyser des images et fournir des descriptions détaillées en français. L'application utilise également Tkinter pour l'interface utilisateur et PIL pour la manipulation des images.

## Structure du Projet

- `hello_api.py` : Module principal qui analyse les images et appelle `visa_reco` avec les coordonnées des boîtes englobantes.
- `visa_reco.py` : Module fournissant une fonction pour afficher des images avec des boîtes englobantes colorées.
- `Constants.py` : Fichier contenant des constantes utilisées dans le projet.
- `secret.py` : Fichier contenant les clés API et autres informations sensibles.
- `requirements.txt` : Fichier listant les dépendances du projet.

## Installation

1. Clonez le dépôt :
    ```sh
    git clone <URL_DU_DEPOT>
    cd <NOM_DU_DEPOT>
    ```

2. Créez un environnement virtuel et activez-le :
    ```sh
    python -m venv venv
    source venv/bin/activate  # Sur Windows, utilisez `venv\Scripts\activate`
    ```

3. Installez les dépendances :
    ```sh
    pip install -r requirements.txt
    ```

## Utilisation

1. Assurez-vous que les clés API dans `secret.py` sont correctes et valides.

2. Exécutez le script principal :
    ```sh
    python hello_api.py
    ```

3. Une fenêtre Tkinter s'ouvrira. Cliquez sur le bouton pour choisir une image à analyser.

## Fonctionnalités

- **Analyse d'images** : Utilise l'API Gemini pour analyser les images et fournir des descriptions détaillées.
- **Affichage des résultats** : Affiche les images avec des boîtes englobantes colorées autour des objets détectés.
- **Synthèse vocale** : Lit les descriptions des images à haute voix.

## Dépendances

- `tkinter` : Interface utilisateur.
- `Pillow` : Manipulation des images.
- `pyttsx3` : Synthèse vocale.
- `google-genai` : API Gemini pour l'analyse des images.

## Contribuer

Les contributions sont les bienvenues ! Veuillez soumettre une pull request ou ouvrir une issue pour discuter des changements que vous souhaitez apporter.

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.
