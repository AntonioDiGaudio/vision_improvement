import tkinter as tk
from PIL import Image, ImageTk
import os
import random
from datetime import datetime
import json

class ImageMemoryApp:
    def __init__(self, root):
        self.root = root
        self.correct_images = []
        self.root.title("Image Memory Test")
        root.geometry("1080x720")
        root.resizable(True, True)
        root.attributes('-fullscreen', True)

        self.time_var = tk.DoubleVar()
        self.num_images_initial_var = tk.IntVar()
        self.num_images_final_var = tk.IntVar()

        self.setup_initial_screen()

    def setup_initial_screen(self):
        font_style = ("Arial", 16)

        tk.Label(self.root, text="Tempo in secondi:", font=font_style).pack(pady=10)
        tk.Entry(self.root, textvariable=self.time_var, font=font_style).pack(pady=10)

        tk.Label(self.root, text="Numero di immagini iniziali:", font=font_style).pack(pady=10)
        tk.Entry(self.root, textvariable=self.num_images_initial_var, font=font_style).pack(pady=10)

        tk.Label(self.root, text="Numero di immagini finali:", font=font_style).pack(pady=10)
        tk.Entry(self.root, textvariable=self.num_images_final_var, font=font_style).pack(pady=10)

        self.error_label = tk.Label(self.root, text="", fg="red", font=font_style)
        self.error_label.pack(pady=10)

        tk.Button(self.root, text="Inizia", command=self.start_test, font=font_style).pack(pady=10)
        tk.Button(self.root, text="Progress", command=self.show_progress, font=font_style).pack(pady=10)

    def start_test(self):
        self.time = float(self.time_var.get())
        self.num_images_initial = self.num_images_initial_var.get()
        self.num_images_final = self.num_images_final_var.get()

        if not self.validate_inputs():
            return

        self.images_initial = self.get_random_images(self.num_images_initial)

        for widget in self.root.winfo_children():
            widget.destroy()

        self.display_initial_images()
        self.root.after(int(self.time * 1000), self.display_final_images)

    def get_random_images(self, num_images):
        image_filenames = os.listdir("images")
        return random.sample(image_filenames, num_images)

    def validate_inputs(self):
        if self.time <= 0:
            self.error_label.config(text="Il tempo deve essere un numero positivo.")
            return False
        if not (1 <= self.num_images_initial <= 100):
            self.error_label.config(text="Il numero di immagini iniziali deve essere compreso tra 1 e 100.")
            return False
        if not (self.num_images_initial <= self.num_images_final <= 100):
            self.error_label.config(text="Il numero di immagini finali deve essere un numero positivo e compreso tra il numero di immagini iniziali e 100.")
            return False
        return True

    def display_initial_images(self):
        canvas_width = self.root.winfo_screenwidth()
        canvas_height = self.root.winfo_screenheight()

        positions = []  # Lista delle posizioni già occupate
        for image_filename in self.images_initial:
            attempts = 0
            while attempts < 5000:
                x = random.randint(100, canvas_width - 100)
                y = random.randint(100, canvas_height - 100)
                # Verifichiamo che la posizione sia accettabile e non sovrapposta ad altre immagini
                if all(abs(x - px) > 150 and abs(y - py) > 150 for px, py in positions):
                    positions.append((x, y))
                    break
                attempts += 1
            else:
                print(f"Could not place image {image_filename} without overlap.")

            if attempts < 5000:
                image_path = os.path.join("images", image_filename)
                image = Image.open(image_path)
                image = image.resize((100, 100), Image.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                label = tk.Label(self.root, image=photo)
                label.photo = photo  # Conserva un riferimento per evitare che l'immagine venga distrutta
                label.place(x=x, y=y)

    def display_final_images(self):
        remaining_images = [img for img in self.get_random_images(self.num_images_final) if
                            img not in self.images_initial]
        num_remaining = self.num_images_final - len(self.images_initial)
        if num_remaining > 0:
            self.images_final = self.images_initial + remaining_images[:num_remaining]
        else:
            self.images_final = self.images_initial[:self.num_images_final]

        random.shuffle(self.images_final)

        for widget in self.root.winfo_children():
            widget.destroy()

        self.canvas = tk.Canvas(self.root)
        self.scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.buttons = {}
        for i, image_filename in enumerate(self.images_final):
            row, column = divmod(i, 5)
            image_path = os.path.join("images", image_filename)
            image = Image.open(image_path)
            image = image.resize((100, 100), Image.LANCZOS)  # Regola le dimensioni dell'immagine con LANCZOS
            photo = ImageTk.PhotoImage(image)
            btn = tk.Button(self.scrollable_frame, image=photo, width=100, height=100,
                            command=lambda img=image_filename: self.toggle_button(img))
            btn.image = photo
            btn.grid(row=row, column=column, padx=10, pady=10)
            self.buttons[image_filename] = btn

        tk.Button(self.root, text="Invia", command=self.check_results, font=("Arial", 16)).pack(pady=20)

    def toggle_button(self, image_filename):
        button = self.buttons[image_filename]
        if button["bg"] == "blue":
            button["bg"] = "SystemButtonFace" if self.root.tk.call("tk", "windowingsystem") == "win32" else "lightgrey"
        else:
            button["bg"] = "blue"

    def check_results(self):
        selected_images = [image_filename for image_filename, button in self.buttons.items() if button["bg"] == "blue"]
        correct_images = [image_filename for image_filename in selected_images if image_filename in self.images_initial]
        score = len(correct_images)

        self.save_progress(score)

        result_message = f"Immagini selezionate: {', '.join(selected_images)}\n" \
                         f"Immagini corrette: {', '.join(correct_images)}"
        initial_images_message = f"Immagini iniziali: {', '.join(self.images_initial)}"
        score_message = f"Score: {score}/{self.num_images_initial}"

        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text=result_message, font=("Arial", 16)).pack(pady=10)
        tk.Label(self.root, text=initial_images_message, font=("Arial", 16)).pack(pady=10)
        tk.Label(self.root, text=score_message, font=("Arial", 16)).pack(pady=10)
        tk.Button(self.root, text="Progress", command=self.show_progress, font=("Arial", 16)).pack(pady=10)

    def save_progress(self, score):
        try:
            with open("progress.json", "r") as file:
                progress_data = json.load(file)
        except FileNotFoundError:
            progress_data = {"progressi": []}

        now = datetime.now().strftime("%d/%m/%y %H:%M")
        new_progress = {"time-stamp": now, "score": f"{score}/{self.num_images_initial}"}
        progress_data["progressi"].append(new_progress)

        with open("progress.json", "w") as file:
            json.dump(progress_data, file)

    def show_progress(self):
        try:
            with open("progress.json", "r") as file:
                progress_data = json.load(file)
                progress_list = progress_data["progressi"]
        except FileNotFoundError:
            progress_list = []

        progress_window = tk.Toplevel(self.root)
        progress_window.title("Progressi")

        canvas = tk.Canvas(progress_window)
        scrollbar = tk.Scrollbar(progress_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        if progress_list:
            # Ordina la lista dei progressi in base al timestamp più recente
            progress_list.sort(key=lambda x: datetime.strptime(x["time-stamp"], "%d/%m/%y %H:%M"), reverse=True)

            for progress in progress_list:
                progress_info = f"Giorno: {progress['time-stamp']}, Score: {progress['score']}"
                tk.Label(scrollable_frame, text=progress_info, font=("Helvetica", 16)).pack(pady=5)
        else:
            tk.Label(scrollable_frame, text="Nessun progresso disponibile.", font=("Helvetica", 16)).pack(pady=5)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageMemoryApp(root)


    root.attributes('-fullscreen', True)
    root.bind('<Escape>', lambda event: root.attributes('-fullscreen', False))

    root.mainloop()

