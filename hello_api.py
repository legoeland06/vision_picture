"""Module providing a function analysing picture
and call visa_reco with bounding-boxes coordinates parameters"""

import tkinter as tk
from tkinter import filedialog
import pyttsx3 as lecteur
import PIL.Image
from google import genai as gn
from Constants import ZEFONT
import visa_reco as vr
from secret import GEMINI0_KEY

# importer moteur audio pour lire le texte
# importer moteur de synthèse vocale pour lire le texte

images_paths = [
    "IMG_20250226_164649.jpg",
    "IMG_20250306_090458.jpg",
    "IMG_20241218_124305.jpg",
    "20171115_165635.jpg",
]


def lire(texte: str):
    """
    reads the given text using a text-to-speech engine.

    Args:
        texte (str): The text to be read aloud.

    Returns:
        None
    """
    lecteur.speak(texte)


def surveillance(image: PIL.Image):
    """
    Analyzes carefully an image using the Gemini API and provides a detailed description in French.

    Args:
        image (PIL.Image.Image, optional): The image to be analyzed. Defaults to opening "IMG_20231108_200124.jpg".

    Returns:
        None: The function runs an asynchronous task to read and process the response text.
    """

    image: PIL.Image = (
        PIL.Image.open(fp=filedialog.askopenfilename()) if not image else image
    )
    client = gn.Client(api_key=GEMINI0_KEY)
    before_response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            image,
            """
            Contexte : 
                Tu es un modèle d’intelligence artificielle multimodal conçu pour analyser et décrire des images avec un niveau de détail élevé.
            Objectif : 
                Analyser très attentivement l'image ci-dessus et de fournir une description complète, précise et nuancée du contenu visuel et en tenant compte des éléments suivants :
            Consignes :
                **Format attendu** : Répond en français sous la forme d’un texte descriptif fluide et bien structuré, en évitant les listes brutes. Ta réponse doit être exhaustive mais concise. Utilise un vocabulaire varié et précis, en adaptant ton niveau de détail en fonction de la complexité de l’image. Si nécessaire, propose plusieurs interprétations.
                **Exemple d’application** :
                    * exemple 1 : Si l’image représente une scène urbaine avec des passants sous la pluie, mentionne l’ambiance (mélancolique, dynamique), les effets visuels (gouttes de pluie sur le sol, lumières floues des néons), ainsi que les émotions potentielles des personnages.
                    * exemple 2 : Si l’image montre du texte, même en langue étrangère, essaie de le traduire ou de proposer une interprétation contextuelle (panneau indicateur, enseigne de magasin, etc.).
                    * exemple 3 : Si l’image est abstraite ou conceptuelle, essaie de décrire les formes, les couleurs et les motifs de manière poétique ou métaphorique.
                    * exemple 4 : Si l’image est une œuvre d’art, essaie de reconnaître le style, l’époque ou l’artiste, en proposant une analyse esthétique et symbolique.
                    * exemple 5 : Si l’image est une partition musicale, essaie de décrire les accords, les notes, les rythmes et les nuances de manière imagée et expressive et enfin d'élaborer le fichier midi correspondant.
                    * exemple 6 : Si l’image contien un monument historique, essaie de décrire l'architecture, l'histoire et l'importance culturelle de manière détaillée et informative.

            Consigne finale : ajoute une liste à puces avec tous les éléments retenus de l'image, une ligne par objet
            """,
        ],
    )

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            image,
            f"""context:{before_response.text}"""
            + """\nTODO:find all items in this liste à puces, and return a list containing a bounding box for each result: 
            formatting like : [
  {"box_2d": [741, 321, 810, 404], "label": "a tree"},
  {"box_2d": [733, 888, 788, 932], "label": "a car"},
  {"box_2d": [752, 682, 818, 767], "label": "a girl"},
  ]
             if there is only one box returned, write the output like this:
                [
                {"box_2d": [733, 888, 788, 932], "label": "object"},
                ]
                """,
        ],
    )
    print(f"\n{before_response.text}\n\n" + "*" * 50)
    vr.plot_bounding_boxes(
        target_file=image,
        boxes_coordinates=response.text,
        content=before_response.text+"\n****************\n\n"+response.text,
    )


def load_image_file():
    """
    Opens a file dialog to select an image file and loads the image using PIL.

    Returns:
        PIL.Image.Image: The loaded image file.
    """
    image_file = PIL.Image.open(filedialog.askopenfilename())
    return image_file


if __name__ == "__main__":

    app = tk.Tk()
    button = tk.Button(
        app,
        text="Cliquer ICI pour choisir\n une image\n à me faire étudier",
        bg="black",
        fg="green",
        padx=10,pady=10,
        font=ZEFONT[0],
        command=lambda: vr.create_asyncio_task(surveillance(load_image_file())),
    )

    button.pack(fill="both")
    app.mainloop()
