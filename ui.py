from __future__ import annotations

import tkinter as tk
from tkinter import simpledialog
from typing import Callable, TypeVar

T = TypeVar("T", str, int, float)


def get_input_from_alert(
    body: str,
    return_type: type[T] = str,
    validate_func: Callable[[T], bool] | None = None,
) -> T:
    """
    Displays an alert dialog with a title and body, and returns the user's input cast to the specified type.

    :param body: The body message of the alert dialog.
    :param return_type: The type to which the user's input should be cast.
    :param validate_func: A function to validate the user's input.
    :return: The user's input cast to the specified type.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    while True:
        if return_type is str:
            user_input = simpledialog.askstring("", body)
        elif return_type is int:
            user_input = simpledialog.askinteger("", body)
        elif return_type is float:
            user_input = simpledialog.askfloat("", body)
        else:
            msg = "Unsupported return type. Please use str, int, or float."
            raise ValueError(msg)

        if user_input is None:
            continue  # If user cancels, ask again

        if validate_func is None or validate_func(return_type(user_input)):
            break  # Exit loop if input is valid

    root.destroy()  # Destroy the root window after getting input
    return return_type(user_input)


def get_button_choice(button_texts: list[str]) -> int:
    """
    Displays a dialog with buttons and returns the index of the clicked button.

    :param button_texts: A list of texts for the buttons.
    :return: The index of the clicked button.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    choice = tk.IntVar()

    def on_button_click(index: int):
        choice.set(index)
        dialog.destroy()

    dialog = tk.Toplevel(root)
    dialog.title("Choose an option")

    for index, text in enumerate(button_texts):
        button = tk.Button(
            dialog, text=text, command=lambda idx=index: on_button_click(idx)
        )
        button.pack(pady=5)

    dialog.wait_window(dialog)
    root.destroy()
    return choice.get()


# Example usage:
def validate_positive(value: int) -> bool:
    return value > 0


user_input_str = get_input_from_alert("Please enter your input:", str)
print(f"User input as str: {user_input_str}")

user_input_int = get_input_from_alert(
    "Please enter a positive number:", int, validate_positive
)
print(f"User input as int: {user_input_int}")

button_texts = ["Option 1", "Option 2", "Option 3"]
button_choice = get_button_choice(button_texts)
print(f"User selected button index: {button_choice}")
