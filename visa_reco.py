"""
Module providing a function displayng picture with colored bounding-boxes
boxes_coordinates and target_file will be received by the caller method
"""

import asyncio
import threading
import tkinter as tk
from PIL import ImageColor, ImageFile, ImageDraw, Image, ImageTk, ImageFont
import pyttsx3 as lecteur
from classes import ListCoords


additional_colors = [
    colorname for (colorname, colorcode) in ImageColor.colormap.items()
]

def create_asyncio_task(async_function):
    """
    Create and run an asyncio task using a new event loop.

    Args:
        async_function (coroutine): The asynchronous function to be run as a task.

    Returns:
        None
    """
    asyncio.run(async_function)


async def lire(texte):
    """
    Asynchronously reads the given text using a text-to-speech engine.

    Args:
        texte (str): The text to be read aloud.

    Returns:
        None
    """
    lecteur.speak(texte)


def alire(self: tk.Text, content):
    """
    Starts a new thread to execute an asynchronous task.

    This function creates a new thread that runs a lambda function. The lambda function
    creates an asyncio task to execute the `lire` function with `contenu_text` as its argument.
    The new thread is then started.

    Note:
        The `threading` module must be imported, and the `create_asyncio_task` and `lire`
        functions, as well as the `contenu_text` variable, must be defined elsewhere in the code.

    Returns:
        None
    """
    try:
        content = self.selection_get()
    except tk.TclError:
        pass

    thread_2 = threading.Thread(
        group=None, target=lambda: create_asyncio_task(lire(content))
    )
    thread_2.start()


def display_result(image, imag_title, content,good_boxes:list[ListCoords]
):
    """
    Display an image in a Tkinter window with a title and additional widgets.

    Args:
        image (PIL.Image.Image): The image to be displayed.
        imag_title (str): The title to be displayed on the image.

    Description:
        This function creates a Tkinter window to display the provided image.
        The image is resized to fit the screen while maintaining its aspect ratio.
        The resized image is then displayed in a Tkinter label widget.
        Additionally, a button labeled "Lire" and a text widget are added to the window.
        The button is associated with the `alire` command, and the text widget is populated
        with the content of `contenu_text`.

    Note:
        The function assumes that `alire` and `contenu_text` are defined elsewhere in the code.
    """
    # Create a Tkinter window
    root = tk.Toplevel()
    root.title("Image Display")

    # Resize the image to fit the screen
    screen_width = root.winfo_screenwidth()/2
    screen_height = root.winfo_screenheight()/2
    image_width, image_height = image.size

    # Calculate the scaling factor to fit the image within the screen
    scale = min(screen_width / image_width, screen_height / image_height)
    new_width = int(image_width * scale)
    new_height = int(image_height * scale)

    # Resize the image
    image = image.resize((new_width, new_height), Image.Resampling.NEAREST)

    # Convert the PIL image to a format Tkinter can use
    tk_image = ImageTk.PhotoImage(image)

    # Create a label widget to display the image
    label = tk.Label(root, image=tk_image, text=imag_title,)

    button = tk.Button(root, text="Lire", command=lambda: alire(button, content))

    text = tk.Text(root, height=10,padx=10,pady=10,bg="maroon",fg="white",wrap="word")

    text.insert(index="1.0", chars=content+"\n\nBounding boxes\n********************************\n")
    
    for element in good_boxes:
        text.insert(index=tk.END, chars=f"{element.label} :: {element.box_2d}\n")

    # text.bind("<Button-1>", alire)
    button.pack(fill="x")
    text.pack(fill="x")

    label.pack()

    # Start the Tkinter event loop
    root.mainloop()


def parse_json(json_output):
    """
    Parses a list of strings to extract JSON content enclosed within markdown fencing.

    Args:
        json_output (list of str): A list of strings representing lines of text,
                                   which may contain JSON content enclosed within
                                   markdown fencing (```json ... ```).

    Returns:
        str: A string containing the JSON content extracted from the input list of strings.
    """
    # Parsing out the markdown fencing
    lines = json_output
    for i, line in enumerate(lines):
        if line == "```json":
            json_output = "\n".join(
                lines[i + 1 :]
            )  # Remove everything before "```json"
            json_output = json_output.split("```", maxsplit=1)[
                0
            ]  # Remove everything after the closing "```"
            break  # Exit the loop once "```json" is found
    return json_output


def plot_bounding_boxes(target_file: ImageFile, boxes_coordinates: list[ListCoords], content: str):
    """
    Plots bounding boxes on the given image and displays the result.
    Args:
        target_file (ImageFile): The image file on which to plot the bounding boxes.
        boxes_coordinates (list[ListCoords]): A list of bounding box coordinates and labels.
        content (str): Additional content to be displayed with the image.
    Raises:
        ValueError: If there is an issue with the bounding box coordinates.
        SyntaxError: If there is an issue with the JSON format of the bounding box coordinates.
    """

    # Load the image
    imag = target_file
    width, height = imag.size
    print(f"Taille de l'image : {imag.size}")
    # Create a drawing object
    draw = ImageDraw.Draw(imag)

    # Define a list of colors
    colors = [
        "red",
        "green",
        "blue",
        "yellow",
        "orange",
        "pink",
        "purple",
        "brown",
        "gray",
        "beige",
        "turquoise",
        "cyan",
        "magenta",
        "lime",
        "navy",
        "maroon",
        "teal",
        "olive",
        "coral",
        "lavender",
        "violet",
        "gold",
        "silver",
    ]

    colors.append(additional_colors)

    good_boxes=[element for element in boxes_coordinates if len(element.box_2d)==4]
    if len(good_boxes)==0:
        return

    for j, boxe in enumerate(good_boxes):
        print(f"BOITE_{j}:: {boxe.box_2d} | {boxe.label}")
        # Iterate over the bounding boxes
        # Select a color from the list
        color = colors[j % len(colors)]
        for box2d in boxe:
            if not boxe.box_2d or len(boxe.box_2d) != 4:
                continue
            # Convert normalized coordinates to absolute coordinates
            abs_y1 = int(boxe.box_2d[0] / 1000 * height)
            abs_x1 = int(boxe.box_2d[1] / 1000 * width)
            abs_y2 = int(boxe.box_2d[2] / 1000 * height)
            abs_x2 = int(boxe.box_2d[3] / 1000 * width)

            if abs_x1 > abs_x2:
                abs_x1, abs_x2 = abs_x2, abs_x1

            if abs_y1 > abs_y2:
                abs_y1, abs_y2 = abs_y2, abs_y1

            # Draw the bounding box
            draw.rectangle(
                ((abs_x1, abs_y1), (abs_x2, abs_y2)),
                outline=color,
                width=int(width / 400),
            )

            # Draw the text
            if "label" in box2d:
                font = ImageFont.truetype("arial.ttf", size=width / 75)
                draw.text(
                    (abs_x1, abs_y1 + 6),
                    boxe.label,
                    fill=color,
                    font=font,
                )

    # Display the image

    thread_1 = threading.Thread(
        group=None, target=display_result(imag, "title", content,good_boxes)
    )
    thread_1.start()
