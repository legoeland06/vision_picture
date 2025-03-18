"""Module providing a function analysing picture
and call visa_reco with bounding-boxes coordinates parameters"""

import tkinter as tk
from tkinter import filedialog
import pyttsx3 as lecteur
import PIL.Image
import PIL.ImageFile
from google import genai as gn
from Constants import ZEFONT
from Classes import Recipe,ImageLoad
import visa_reco as vr
from secret import GEMINI_API_KEY



class HelloApi:

    image_load:ImageLoad

    def lire(self,texte: str):
        """
        Convert the given text to speech using the lecteur.speak method.

        Args:
            texte (str): The text to be spoken.
        """
        lecteur.speak(texte)


    def get_text_from_widget(self,widget: tk.Text) -> str:
        """
        Retrieve text content from a Tkinter Text widget starting from the second line.

        Args:
            widget (tk.Text): The Tkinter Text widget to retrieve text from.

        Returns:
            str: The text content of the widget, or an empty string if the content is only whitespace.
        """
        content = widget.get("2.0", tk.END).strip()
        return content if content else ""


    def surveillance(self,image: PIL.Image, prompt_wdgt: tk.Text):
        """
        Analyze the given image and generate a detailed description and bounding boxes.

        Args:
            image (PIL.Image): The image to be analyzed.
            prompt_wdgt (tk.Text): The Tkinter Text widget containing the prompt.

        Returns:
            Recipe: The generated description and bounding boxes.
        """
        if not image:
            return
        client = gn.Client(api_key=GEMINI_API_KEY)

        def ask_it():
            """
            Generate content using the Gemini API and parse the response.

            Returns:
                Recipe: The parsed response containing the description and bounding boxes.
            """
            while True:
                result = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[
                        image,
                        (
                            """
                            Contexte : 
                                Tu es un modèle d’intelligence artificielle multimodal français conçu pour analyser et décrire des images avec un niveau de détail élevé.

                            Objectif : 
                                Analyser très attentivement l'image ci-dessus et fournir une description complète, précise et nuancée du contenu visuel et en tenant compte des éléments suivants :

                            Consignes :
                                **Exemple d’application** :
                                    * exemple 1 : Si l’image représente une scène urbaine avec des passants sous la pluie, mentionne l’ambiance (mélancolique, dynamique), les effets visuels (gouttes de pluie sur le sol, lumières floues des néons), ainsi que les émotions potentielles des personnages.
                                    * exemple 2 : Si l’image montre du texte, même en langue étrangère, essaie de le traduire ou de proposer une interprétation contextuelle (panneau indicateur, enseigne de magasin, etc.).
                                    * exemple 3 : Si l’image est abstraite ou conceptuelle, essaie de décrire les formes, les couleurs et les motifs de manière poétique ou métaphorique.
                                    * exemple 4 : Si l’image est une œuvre d’art, essaie de reconnaître le style, l’époque ou l’artiste, en proposant une analyse esthétique et symbolique.
                                    * exemple 5 : Si l’image est une partition musicale, essaie de décrire les accords, les notes, les rythmes et les nuances de manière imagée et expressive et enfin d'élaborer le fichier midi correspondant.
                                    * exemple 6 : Si l’image contien un monument historique, essaie de décrire l'architecture, l'histoire et l'importance culturelle de manière détaillée et informative.
                                    * exemple 7 : Si l’image représente un seul objet, fais en le descriptif complet en listant les élements qui le composent.
                                    
                                **Format attendu** : """
                            + (
                                """ ATTENTION : Toutes tes REPONSES seront en FRANCAIS, de la forme d'un texte descriptif fluide et bien structuré, suivi d'une liste. Utilise un vocabulaire varié et précis, en adaptant ton niveau de détail en fonction de la complexité de l’image. Si nécessaire, propose plusieurs interprétations.
                                    La liste à puces avec tous les éléments retenus de l'image, doit être de la forme d'une liste de bounding-box:
                                    [
                                    {"box_2d": [741, 321, 810, 404], "label": "a tree"},
                                    {"box_2d": [733, 888, 788, 932], "label": "a car"},
                                    {"box_2d": [752, 682, 818, 767], "label": "a girl"},
                                    ]
                                    
                                    if there is only one box returned, write the output like this:
                                        [
                                        {"box_2d": [733, 888, 788, 932], "label": "object"},
                                        ]
                                        """
                            )
                            + ("\nQuestion : " + self.get_text_from_widget(prompt_wdgt))
                            if self.get_text_from_widget(prompt_wdgt) != ""
                            else ""
                        ),
                    ],
                    config={
                        "response_mime_type": "application/json",
                        "response_schema": Recipe,
                    },
                )
                _sortie = result.parsed.model_dump()
                _contexte = _sortie["contexte"]
                _liste = [item for item in _sortie["liste_a_puce"]]
                _recipe = Recipe(contexte=_contexte, liste_a_puce=_liste)
                if (
                    len(_recipe.liste_a_puce) > 0
                    and len(_recipe.liste_a_puce[0].box_2d) == 4
                ):
                    return _recipe

        response = ask_it()

        print("Description\n" + "*" * 50 + f"\n{response.contexte}\n\n" + "*" * 50)
        print("\nliste à puce\n" + "*" * 50)
        for puce in response.liste_a_puce:
            print(f"{puce}")
        print("*" * 50)
        print(len(response.liste_a_puce))

        vr.plot_bounding_boxes(
            target_file=image,
            boxes_coordinates=response.liste_a_puce,
            content=response.contexte + "\n" + str(response.liste_a_puce),
        )


    def load_image_file(self):
        """
        Opens a file dialog to select an image file and loads it using PIL.

        Returns:
            PIL.Image.Image: The loaded image file.
        """

        namefile = filedialog.askopenfilename()
        suzy:ImageLoad=ImageLoad()
        suzy.image=PIL.Image.open(namefile)
        self.image_load=suzy
        return self.image_load


if __name__ == "__main__":

    app = tk.Tk()
    helloApi=HelloApi()

    image_load=helloApi.load_image_file()
    prompt_widget = tk.Text(master=app, height=5, fg="green")
    prompt_widget.insert(
        "1.0", "Question importante à répondre sous forme de liste à puces:"
    )
    prompt_widget.pack(fill="x")
    button = tk.Button(
        app,
        text="Cliquer ICI pour choisir\n une image",
        bg="black",
        fg="green",
        padx=10,
        pady=10,
        font=ZEFONT[0],
        command=helloApi.load_image_file,
    )
    lancer = tk.Button(
        app,
        text="Décrir l'image",
        bg="orange",
        fg="white",
        padx=10,
        pady=10,
        font=ZEFONT[0],
        command=lambda: vr.create_asyncio_task(
            helloApi.surveillance(image=helloApi.image_load.image, prompt_wdgt=prompt_widget)
        ),
    )

    button.pack(fill="both")
    lancer.pack(fill="both")
    app.mainloop()
