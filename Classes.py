"""
Classes:
    ListCoords(BaseModel): A data model representing a labeled bounding box in 2D space.

    Recipe(BaseModel): A class used to represent a Recipe.
            contexte (str): A string representing the context of the recipe.
            liste_a_puce (list[ListCoords]): A list of ListCoords objects representing bullet points in the recipe.

    ImageLoad: A class used to represent an Image Loader.
            get_image(): Returns the image associated with the instance.
            set_image(image): Sets the image attribute for the instance."""



import PIL.Image
import PIL.ImageFile
from pydantic import BaseModel


class ListCoords(BaseModel):
    """
    ListCoords is a data model representing a labeled bounding box in 2D space.

    Attributes:
        box_2d (list[int]): A list of four integers representing the coordinates of the bounding box
                            in the format [x_min, y_min, x_max, y_max].
        label (str): A string label describing the object within the bounding box.
    """

    box_2d: list[int]
    label: str


class Recipe(BaseModel):
    """
    A class used to represent a Recipe.

    Attributes
    ----------
    contexte : str
        A string representing the context of the recipe.
    liste_a_puce : list[ListCoords]
        A list of ListCoords objects representing bullet points in the recipe.
    """

    contexte: str
    liste_a_puce: list[ListCoords]


class ImageLoad:
    """
    A class used to represent an Image Loader.

    Attributes:
        image (PIL.Image): The image associated with the instance.

    Methods:
        get_image():
    """

    image: PIL.Image

    def get_image(self):
        """
        Returns the image associated with the instance.

        Returns:
            object: The image associated with the instance.
        """
        return self.image

    def set_image(self,image):
        """
        Sets the image attribute for the instance.
        Args:
            image: The image to be set.
        """
        self.image=image