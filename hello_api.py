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


images_paths = [
    "IMG_20250226_164649.jpg",
    "IMG_20250306_090458.jpg",
    "IMG_20241218_124305.jpg",
    "20171115_165635.jpg",
]


def lire(texte: str):
    """
    Convert the given text to speech using the lecteur.speak method.

    Args:
        texte (str): The text to be spoken.
    """
    lecteur.speak(texte)


def get_text_from_widget(widget: tk.Text):
    """
    Retrieves text content from a Tkinter Text widget starting from the second line.

    Args:
        widget (tk.Text): The Tkinter Text widget from which to retrieve the content.

    Returns:
        str: The content of the widget with an additional instruction if the content is not empty.
             If the content is empty, returns an empty string.
    """
    content=widget.get("2.0", tk.END)
    print(content)
    if len(content.strip())>0:
        return content+"\nConsigne finale : ajoute une liste à puces avec tous les éléments de ta réponse, un élément par ligne"
    return str()


def surveillance(image: PIL.Image, prompt_wdgt: tk.Text):
    """
    Analyzes an image and provides a detailed description along with bounding boxes for identified objects.
    Args:
        image (PIL.Image): The image to be analyzed. If not provided, a file dialog will prompt the user to select an image.
        prompt_wdgt (tk.Text): A Tkinter Text widget containing additional instructions or context for the analysis.
    Returns:
        None
    The function performs the following steps:
        1. Opens the image if not provided.
        2. Initializes a client for the Gemini API using a predefined API key.
        3. Retrieves the text from the prompt widget.
        4. Sends the image and context to the Gemini API to generate a detailed description.
        5. Sends the image and generated description to the Gemini API to identify objects and their bounding boxes.
        6. Prints the generated description and bounding boxes.
        7. Plots the bounding boxes on the image and displays the result.
    """
    image: PIL.Image = (
        PIL.Image.open(fp=filedialog.askopenfilename()) if not image else image
    )
    client = gn.Client(api_key=GEMINI0_KEY)
    print(prompt_wdgt.get("1.0", tk.END))
    before_response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            image,
            (
                """
            Contexte : 
                Tu es un modèle d’intelligence artificielle multimodal conçu pour analyser et décrire des images avec un niveau de détail élevé.

            Objectif : 
                Analyser très attentivement l'image ci-dessus et de fournir une description complète, précise et nuancée du contenu visuel et en tenant compte des éléments suivants :

            Consignes :
                **Exemple d’application** :
                    * exemple 1 : Si l’image représente une scène urbaine avec des passants sous la pluie, mentionne l’ambiance (mélancolique, dynamique), les effets visuels (gouttes de pluie sur le sol, lumières floues des néons), ainsi que les émotions potentielles des personnages.
                    * exemple 2 : Si l’image montre du texte, même en langue étrangère, essaie de le traduire ou de proposer une interprétation contextuelle (panneau indicateur, enseigne de magasin, etc.).
                    * exemple 3 : Si l’image est abstraite ou conceptuelle, essaie de décrire les formes, les couleurs et les motifs de manière poétique ou métaphorique.
                    * exemple 4 : Si l’image est une œuvre d’art, essaie de reconnaître le style, l’époque ou l’artiste, en proposant une analyse esthétique et symbolique.
                    * exemple 5 : Si l’image est une partition musicale, essaie de décrire les accords, les notes, les rythmes et les nuances de manière imagée et expressive et enfin d'élaborer le fichier midi correspondant.
                    * exemple 6 : Si l’image contien un monument historique, essaie de décrire l'architecture, l'histoire et l'importance culturelle de manière détaillée et informative.
                    
                **Format attendu** : """
                + (
                    """ Répond en français sous la forme d’un texte descriptif fluide et bien structuré, en évitant les listes brutes. Ta réponse doit être exhaustive mais concise. Utilise un vocabulaire varié et précis, en adaptant ton niveau de détail en fonction de la complexité de l’image. Si nécessaire, propose plusieurs interprétations.
                        Consigne finale : ajoute en fin de document une liste à puces avec tous les éléments retenus de l'image, une ligne par objet
            """
                )
                if get_text_from_widget(prompt_wdgt)==str()
                else get_text_from_widget(prompt_wdgt)
            ),
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
        content=before_response.text + "\n****************\n\n" + response.text,
    )


def load_image_file():
    """
    Opens a file dialog to select an image file and loads it using PIL.

    Returns:
        PIL.Image.Image: The loaded image file.
    """
    image_file = PIL.Image.open(filedialog.askopenfilename())
    return image_file


if __name__ == "__main__":

    app = tk.Tk()
    prompt_widget = tk.Text(master=app, height=5)
    prompt_widget.insert(
        "1.0", "Question importante à répondre sous forme de liste à puces:\n"
    )
    prompt_widget.pack(fill="x")
    button = tk.Button(
        app,
        text="Cliquer ICI pour choisir\n une image\n à me faire étudier",
        bg="black",
        fg="green",
        padx=10,
        pady=10,
        font=ZEFONT[0],
        command=lambda: vr.create_asyncio_task(
            surveillance(load_image_file(), prompt_wdgt=prompt_widget)
        ),
    )

    button.pack(fill="both")
    app.mainloop()
