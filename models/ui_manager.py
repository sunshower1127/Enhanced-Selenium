import tkinter as tk
from tkinter import simpledialog


def get_input_from_alert(title: str, body: str):
    """
    Displays an alert dialog with a title and body, and returns the user's input.

    :param title: The title of the alert dialog.
    :param body: The body message of the alert dialog.
    :return: The user's input as a string.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    user_input = simpledialog.askstring(title, body)
    root.destroy()  # Destroy the root window after getting input
    return user_input


# Example usage:
user_input = get_input_from_alert("Title", "Please enter your input:")
print(f"User input: {user_input}")
