"""Module providing a function analysing picture
and call visa_reco with bounding-boxes coordinates parameters"""

import os
from pathlib import Path
import time
import tkinter as tk
from tkinter import filedialog
import PIL.Image
import PIL.ImageFile
import PIL.ImageTk
from colorama import Fore
import cv2
import lire_text as lire
from skimage.metrics import structural_similarity as ssim
from cv2 import VideoCapture
from google import genai as gn
from classes import Recipe, ImageLoad
import visa_reco as vr
from secret import GEMINI_API_KEY


class HelloApi:
    """HelloApi is a class that provides a graphical user interface (GUI) for loading images,
    displaying them, and interacting with an AI model to analyze the images and generate detailed descriptions.
    ### Attributes:
        image_name (str): The name of the image file.
        image_load (ImageLoad): An object that holds the loaded image.
        tk_image (PIL.ImageTk.PhotoImage): The Tkinter-compatible image object.
        lancer (tk.Button): A button widget to trigger the image analysis.
        illustration (tk.Label): A label widget to display the loaded image.
    ### Methods:
        get_image_name() -> str: Retrieves the name of the image.
        set_image_name(name: str): Sets the image name and updates the configuration of the 'lancer' button.
        set_image_tk(imagetk: PIL.ImageTk.PhotoImage): Sets the Tkinter image object.
        get_image_tk() -> PIL.ImageTk.PhotoImage: Returns the Tkinter image object.
        set_image_load(loaded: ImageLoad): Sets the image load and updates the illustration with the resized image.
        get_image_load() -> ImageLoad: Returns the current image load.
        lire(texte: str): Converts the given text to speech using the lecteur.speak method.
        get_text_from_widget(widget: tk.Text) -> str: Retrieves text content from a Tkinter Text widget starting from the second line.
        surveillance(image: PIL.Image, prompt_wdgt: tk.Text): Analyzes the given image and generates a detailed description and bounding boxes.
        load_image_file() -> PIL.Image.Image: Opens a file dialog to select an image file and loads it using PIL.
    """

    def __init__(self, display: bool = True):

        if display:
            self.image_name: str = str()
            self.image_load: ImageLoad = None
            self.tk_image: PIL.ImageTk = None

            app = tk.Tk()
            frame = tk.Frame(app)
            prompt_widget = tk.Text(master=frame, height=5, fg="white", bg="orange")
            prompt_widget.insert(
                "1.0", "Question importante à répondre sous forme de liste à puces:"
            )
            prompt_widget.pack(fill="x")
            canvas = tk.Canvas(frame, bg="black", relief="flat")
            canvas_images = tk.Canvas(frame)
            button = tk.Button(
                canvas,
                text="L\nO\nA\nD",
                bg="black",
                fg="green",
                padx=10,
                pady=10,
                font="Trebuchet",
                command=self.load_image_file,
            )
            self.lancer = tk.Button(
                canvas_images,
                text="ENVOYER",
                width=10,
                bg="orange",
                fg="white",
                padx=10,
                pady=10,
                font="Trebuchet",
                command=lambda: self.surveillance(
                    image=self.image_load.image, prompt_wdgt=prompt_widget
                ),
            )
            self.illustration = tk.Label(
                canvas,
                text="NO IMAGE LOADED",
                image=self.tk_image if self.tk_image else None,
                bg="black",
                fg="white",
                font="Trebuchet",
            )

            frame.pack(fill="both")
            canvas.pack(fill="both")
            canvas_images.pack(fill="both")
            button.pack(side="left", fill="both")
            self.illustration.pack(fill="both")
            self.lancer.pack(fill="both")
            app.mainloop()

    def get_image_name(self):
        """
        Retrieve the name of the image.

        Returns:
            str: The name of the image.
        """
        return self.image_name

    def set_image_name(self, name):
        """
        Sets the image name and updates the configuration of the 'lancer' attribute.

        Args:
            name (str): The name to set for the image.

        Returns:
            None
        """
        self.image_name = name
        self.lancer.config(fg="red")

    def set_image_tk(self, imagetk):
        """
        Sets the Tkinter image object.

        Args:
            imagetk (PhotoImage): The Tkinter PhotoImage object to be set.
        """
        self.tk_image = imagetk

    def get_image_tk(self):
        """
        Returns the Tkinter image object.

        Returns:
            tk.PhotoImage: The Tkinter image object stored in the instance.
        """
        return self.tk_image

    def set_image_load(self, loaded: ImageLoad):
        """
        Sets the image load and updates the illustration with the resized image.
        Args:
            loaded: An object that provides a method `get_image` which returns a PIL.Image.
        The method performs the following steps:
        1. Sets the `image_load` attribute to the provided `loaded` object.
        2. Retrieves the image from the `loaded` object.
        3. Resizes the image to 600x600 pixels using the nearest neighbor resampling method.
        4. Converts the resized image to a format that Tkinter can use.
        5. Updates the `illustration` widget with the new image and sets its configuration.
        """
        self.image_load = loaded
        self.set_image_tk(
            PIL.ImageTk.PhotoImage(
                loaded.get_image().resize((600, 600), PIL.Image.Resampling.NEAREST)
            )
        )
        self.illustration.config(
            image=self.get_image_tk(), height=200, justify="center", padx=10, pady=10
        )

    def get_image_load(self):
        """
        Returns the current image load.

        Returns:
            object: The current image load.
        """
        return self.image_load

    def get_text_from_widget(self, widget: tk.Text) -> str:
        """
        Retrieve text content from a Tkinter Text widget starting from the second line.

        Args:
            widget (tk.Text): The Tkinter Text widget to retrieve text from.

        Returns:
            str: The text content of the widget, or an empty string if the content is only whitespace.
        """
        content = widget.get("2.0", tk.END).strip()
        return content if content else ""

    def surveillance(
        self, image: PIL.Image, prompt_wdgt: tk.Text = None, texte: str = str()
    ):
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
                            (
                                """
                            Objectif : 
                                Analyser très attentivement l'image ci-dessus et répond à la Question en fin de ce prompt en tenant compte des consignes suivantes :

                            Consignes :
                                **Exemple d’application** :
                                    * exemple 1 : Si l’image représente une scène urbaine avec des passants sous la pluie, mentionne l’ambiance (mélancolique, dynamique), les effets visuels (gouttes de pluie sur le sol, lumières floues des néons), ainsi que les émotions potentielles des personnages.
                                    * exemple 2 : Si l’image montre du texte, même en langue étrangère, essaie de le traduire ou de proposer une interprétation contextuelle (panneau indicateur, enseigne de magasin, etc.).
                                    * exemple 3 : Si l’image est abstraite ou conceptuelle, essaie de décrire les formes, les couleurs et les motifs de manière poétique ou métaphorique.
                                    * exemple 4 : Si l’image est une œuvre d’art, essaie de reconnaître le style, l’époque ou l’artiste, en proposant une analyse esthétique et symbolique.
                                    * exemple 5 : Si l’image est une partition musicale, essaie de décrire les accords, les notes, les rythmes et les nuances de manière imagée et expressive et enfin d'élaborer le fichier midi correspondant.
                                    * exemple 6 : Si l’image contien un monument historique, essaie de décrire l'architecture, l'histoire et l'importance culturelle de manière détaillée et informative.
                                    * exemple 7 : Si l’image représente un seul objet, fais en le descriptif complet en listant les élements qui le composent.
                                    
                                **Format attendu** : Sous la forme d'un texte descriptif fluide et bien structuré, suivi d'une liste à puces.
                                            Concernant le texte descriptif : Utilise un vocabulaire varié et précis, en adaptant ton niveau de détail en fonction de la complexité de l’image. Si nécessaire, propose plusieurs interprétations.
                                            Concernant la liste à puces : elle doit être de la forme d'une liste de bounding-box encadrant les éléments retenus de l'image ou la mise en évidence des éléments de ta réponse soigneusement encradrés, avec leur label associé.

                                        Exemple :
                                    <le texte de la réponse> par exemple: "Une scène urbaine nocturne avec des passants sous la pluie, éclairée par des néons et des phares de voitures. L'ambiance est mélancolique et dynamique, avec des reflets flous et des gouttes de pluie sur le sol."
                                    <la liste à puce> par exemple:
                                    [
                                    {"box_2d": [741, 321, 810, 404], "label": "a tree"},
                                    {"box_2d": [733, 888, 788, 932], "label": "a car"},
                                    {"box_2d": [752, 682, 818, 767], "label": "a girl"},
                                    ]
                                    
                                    if there is only one bounding-box returned, write the output like this:
                                        [
                                        {"box_2d": [733, 888, 788, 932], "label": "object"},
                                        ]
                                        """
                            )
                            + ("\nQuestion : " + self.get_text_from_widget(prompt_wdgt))
                            if self.get_text_from_widget(prompt_wdgt) != ""
                            else (
                                "\nQuestion : "
                                + "Quelle est la description de l'image ?\n"
                            )
                            + "\n\nRéponse en français(FR) exclusivement"
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
                    len(_recipe.liste_a_puce) != 0
                    and len(_recipe.liste_a_puce[0].box_2d) == 4
                ):
                    return _recipe
                else:
                    print(
                        "Veuillez répondre en français et respecter le format demandé"
                    )
                    _recipe.liste_a_puce.clear()
                    return _recipe

        response = ask_it()
        print_to_console([response])
        vr.plot_bounding_boxes(
            target_file=image,
            boxes_coordinates=response.liste_a_puce,
            content=response.contexte,
        )

    def load_image_file(self):
        """
        Opens a file dialog to select an image file and loads it using PIL.

        Returns:
            PIL.Image.Image: The loaded image file.
        """

        namefile = filedialog.askopenfilename()
        self.set_image_name(Path(namefile).name)
        suzy: ImageLoad = ImageLoad()
        suzy.image = PIL.Image.open(namefile)
        self.set_image_load(suzy)

        return self.image_load


def mode_console(images: list[str], question: str = str()):
    """
    Analyzes a list of images using a multimodal language model and prints the analysis results to the console.
    Args:
        images (list[str]): A list of file paths to the images to be analyzed. Defaults to ["./peripherique.jpg"].
    Returns:
        list[Recipe]: A list of Recipe objects containing the analysis results for each image.
    The function performs the following steps:
    1. Loads each image from the provided file paths.
    2. Sends the image to a multimodal language model (Gemini 2.0 Flash) for analysis.
    3. Parses the response from the model to extract the context and bullet points.
    4. Prints the context and bullet points to the console.
    5. Prints the number of bullet points (bounding boxes) to the console.
    6. Appends the analysis results to a list of Recipe objects and returns it.
    """
    recipes: list[Recipe] = []
    # récupération de la list d'images à analyser
    for image in images:
        # chargement de l'image
        image = PIL.Image.open(image)
        # création du prompt vers le llm multimodal
        client = gn.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                image,
                (
                    """
                Objectif : 
                    Analyser très attentivement l'image ci-dessus et répond à la Question en fin de ce prompt en tenant compte des consignes suivantes :

                Consignes :
                    **Exemple d’application** :
                        * exemple 1 : Si l’image représente une scène urbaine avec des passants sous la pluie, mentionne l’ambiance (mélancolique, dynamique), les effets visuels (gouttes de pluie sur le sol, lumières floues des néons), ainsi que les émotions potentielles des personnages.
                        * exemple 2 : Si l’image montre du texte, même en langue étrangère, essaie de le traduire ou de proposer une interprétation contextuelle (panneau indicateur, enseigne de magasin, etc.)."
                        """
                )
                + f"\nQuestion : {question}",
            ],
            config={
                "response_mime_type": "application/json",
                "response_schema": Recipe,
            },
        )
        # récupération de la réponse

        _result = response.parsed.model_dump()
        contexte = _result["contexte"]
        liste_a_puce = _result["liste_a_puce"]
        recipe = Recipe(contexte=contexte, liste_a_puce=liste_a_puce)
        recipes.append(recipe)
    return recipes


def print_to_console(content: list[Recipe]):
    """
    Prints the details of each Recipe object in the content list to the console.

    Args:
        content (list[Recipe]): A list of Recipe objects to be printed.

    The function prints the following details for each Recipe object:
        - A separator line of asterisks based on the terminal width.
        - The description of the recipe in green text.
        - A separator line of dashes, one-third the width of the terminal.
        - A bullet list of items in the recipe, if any, in green text.
        - The number of items in the bullet list.

    If the bullet list is empty, it prints "Pas de liste à puce" (No bullet list).
    """
    max_largueur = os.get_terminal_size().columns
    for element in content:
        print()
        print(
            "*" * max_largueur
            + f"\nDescription : \n{Fore.GREEN+element.contexte+Fore.RESET}\n"
            + "-" * int(max_largueur / 3)
        )
        print("Liste à puce :" + Fore.GREEN)
        if len(element.liste_a_puce) == 0:
            print("Pas de liste à puce" + Fore.RESET)
        else:
            for puce in element.liste_a_puce:
                print(f"{puce}")
            print(
                f"{Fore.RESET}\nNombre de bounding boxes : {len(element.liste_a_puce)}"
            )


def compare_images(imageA, imageB):
    """
    Compare two images using the Structural Similarity Index (SSIM).

    Args:
        imageA (numpy.ndarray): The first image.
        imageB (numpy.ndarray): The second image.

    Returns:
        bool: True if the images are similar, False otherwise.
    """
    grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)
    score, _ = ssim(grayA, grayB, full=True)
    return score


def mode_survey():
    """
    Captures images from a USB-connected phone camera and processes them.
    This function continuously captures images from a camera connected via USB.
    It compares the similarity of each captured image with the initial image using SSIM.
    If the similarity score is below a threshold, it saves the new image and processes it using the `mode_console` function.
    The result is then read aloud using the `lire.lancer` function.
    If the similarity score is above the threshold, it logs a message indicating no change.
    """

    # utilise le téléphone en usb comme caméra
    n = 0
    m = 0
    seuil = 0.90
    # récupération des images de la caméra
    # caméra du téléphone cv2.VideoCapture(1)
    # caméra web cv2.VideoCapture(0)

    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("Error: Could not open video device.")
        return

    # récupération d'une image de la caméra
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame from camera.")
        return

    initial_frame = frame.copy()
    cv2.imwrite("captures/image_cam.jpg", frame)  # ignore
    print("Initial frame captured")

    while True:
        n += 1
        # récupération d'une image de la caméra
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image from camera")
            return

        print(f"Captured frame {n}")

        similarity_score = compare_images(initial_frame, frame)
        print(f"Similarity score: {similarity_score}, seuil:{seuil}")

        if similarity_score < seuil:  # Threshold for similarity
            # enregistrement de l'image dans un fichier
            cv2.imwrite(f"captures/image_cam_{n}.jpg", frame)  # ignore
            print(
                f"Image saved as captures/image_cam_{n} with similarity score: {similarity_score}"
            )
            resultat = mode_console(
                images=[f"captures/image_cam_{n}.jpg"],
                question="étudie attentivement et en détails cette photo et donne moi le nombre de personne que tu aperçois ?",
            )

            seul_element = resultat.pop()
            lire.lancer("coucou éric !")
            # lire.lancer(seul_element.contexte, langue="français(FR)")
            # vr.display_result(
            #     content=seul_element.contexte,
            #     image=PIL.ImageFile(,
            #     good_boxes=[],
            #     imag_title="ok",
            # )

            initial_frame = frame.copy()
            m += 1
        else:
            print(f"Test numéro {n} : pas de changement")
            cv2.imwrite(f"captures/image_cam_Nochanges_{m}.jpg", frame)  # ignore
            # lire.lancer(f"Test numéro {n} : pas de changement")

        time.sleep(2)


if __name__ == "__main__":
    # gestion des options de la ligne de commande pour lancer l'API en mode console
    # ou en mode GUI (Graphical User Interface) avec Tkinter
    import argparse

    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--console", action="store_true", help="Run the API in console mode"
    )
    argparser.add_argument("--files", nargs="+", help="lit les fichiers à traiter")
    argparser.add_argument(
        "--directory",
        help="lit les fichiers d'un répertoire donné",
    )
    argparser.add_argument(
        "--cam", action="store_true", help="Run the API in cam survey mode"
    )
    args = argparser.parse_args()
    if args.console:
        if args.files:
            resultats = mode_console(
                images=args.files, question="Quelle est la description de l'image ?"
            )
            print_to_console(resultats)
        elif args.directory:
            print("Traitement des fichiers d'un répertoire")
            # traitement des fichiers d'un répertoire
            # récupération des fichiers du répertoire
            directory: list[str] = os.listdir(args.directory)
            # création de la liste des chemins des fichiers
            files = [f"{args.directory}/" + str(f) for f in directory]
            print(files)
            resultats = mode_console(images=files)
            print_to_console(resultats)
    elif args.cam:
        print("Traitement des images de la caméra")
        # traitement des images de la cam
        mode_survey()
    else:
        helloApi = HelloApi()
