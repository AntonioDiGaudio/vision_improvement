import tkinter as tk
import random
import json
from datetime import datetime

class WordMemoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Word Memory Test")
        root.geometry("1080x720")
        root.resizable(True, True)
        root.attributes('-fullscreen', True)

        self.time_var = tk.DoubleVar()
        self.num_words_initial_var = tk.IntVar()
        self.num_words_final_var = tk.IntVar()

        self.setup_initial_screen()

    def setup_initial_screen(self):
        font_style = ("Arial", 16)

        tk.Label(self.root, text="Tempo in secondi:", font=font_style).pack(pady=10)
        tk.Entry(self.root, textvariable=self.time_var, font=font_style).pack(pady=10)

        tk.Label(self.root, text="Numero di parole iniziali:", font=font_style).pack(pady=10)
        tk.Entry(self.root, textvariable=self.num_words_initial_var, font=font_style).pack(pady=10)

        tk.Label(self.root, text="Numero di parole finali:", font=font_style).pack(pady=10)
        tk.Entry(self.root, textvariable=self.num_words_final_var, font=font_style).pack(pady=10)

        self.error_label = tk.Label(self.root, text="", fg="red", font=font_style)
        self.error_label.pack(pady=10)

        tk.Button(self.root, text="Inizia", command=self.start_test, font=font_style).pack(pady=10)
        tk.Button(self.root, text="Progress", command=self.show_progress, font=font_style).pack(pady=10)

    def start_test(self):
        self.time = float(self.time_var.get())
        self.num_words_initial = self.num_words_initial_var.get()
        self.num_words_final = self.num_words_final_var.get()

        if not self.validate_inputs():
            return

        self.words_initial = self.get_random_words(self.num_words_initial)

        for widget in self.root.winfo_children():
            widget.destroy()

        self.display_initial_words()

        self.root.after(int(self.time * 1000), self.display_final_words)

    def get_random_words(self, num_words):
        with open("parole.txt", "r", encoding="utf-8") as file:
            words = [line.strip() for line in file.readlines()]
            return random.sample(words, num_words)

    def validate_inputs(self):
        if self.time <= 0:
            self.error_label.config(text="Il tempo deve essere un numero positivo.")
            return False
        if not (1 <= self.num_words_initial <= 100):
            self.error_label.config(text="Il numero di parole iniziali deve essere compreso tra 1 e 100.")
            return False
        if not (self.num_words_initial <= self.num_words_final <= 100):
            self.error_label.config(text="Il numero di parole finali deve essere un numero positivo e compreso tra il numero di parole iniziali e 100.")
            return False
        return True

    def display_initial_words(self):
        self.canvas = tk.Canvas(self.root, width=self.root.winfo_screenwidth(), height=self.root.winfo_screenheight())
        self.canvas.pack()

        positions = []
        for word in self.words_initial:
            attempts = 0
            while attempts < 5000:
                x = random.randint(100, self.root.winfo_screenwidth() - 100)
                y = random.randint(100, self.root.winfo_screenheight() - 100)
                if all(abs(x - px) > 50 and abs(y - py) > 50 for px, py in positions):
                    positions.append((x, y))
                    break
                attempts += 1
            else:
                print(f"Could not place word {word} without overlap.")

            if attempts < 5000:
                self.canvas.create_text(x, y, text=word, font=("Arial", 24))

    def display_final_words(self):
        remaining_words = self.get_random_words(self.num_words_final - self.num_words_initial)
        self.words_final = self.words_initial + remaining_words
        random.shuffle(self.words_final)

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
        for i, word in enumerate(self.words_final):
            row, column = divmod(i, 5)
            btn = tk.Button(self.scrollable_frame, text=word, width=15, height=2, font=("Arial", 12),
                            command=lambda w=word: self.toggle_button(w))
            btn.grid(row=row, column=column, padx=10, pady=10)
            self.buttons[word] = btn

        tk.Button(self.root, text="Invia", command=self.check_results, font=("Arial", 16)).pack(pady=20)

    def toggle_button(self, word):
        button = self.buttons[word]
        if button["bg"] == "blue":
            button["bg"] = "SystemButtonFace" if self.root.tk.call("tk", "windowingsystem") == "win32" else "lightgrey"
        else:
            button["bg"] = "blue"

    def check_results(self):
        selected_words = [word for word, button in self.buttons.items() if button["bg"] == "blue"]
        correct_words = [word for word in selected_words if word in self.words_initial]
        score = len(correct_words)

        self.save_progress(score)

        result_message = f"Parole selezionate: {', '.join(selected_words)}\n" \
                         f"Parole corrette: {', '.join(correct_words)}"
        initial_words_message = f"Parole iniziali: {', '.join(self.words_initial)}"
        score_message = f"Score: {score}/{self.num_words_initial}"

        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text=result_message, font=("Arial", 16)).pack(pady=10)
        tk.Label(self.root, text=initial_words_message, font=("Arial", 16)).pack(pady=10)
        tk.Label(self.root, text=score_message, font=("Arial", 16)).pack(pady=10)
        tk.Button(self.root, text="Progress", command=self.show_progress, font=("Arial", 16)).pack(pady=10)

    def save_progress(self, score):
        try:
            with open("progress.json", "r") as file:
                progress_data = json.load(file)
        except FileNotFoundError:
            progress_data = {"progressi": []}

        now = datetime.now().strftime("%d/%m/%y %H:%M")
        new_progress = {"time-stamp": now, "score": f"{score}/{self.num_words_initial}"}
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
    app = WordMemoryApp(root)

    root.attributes('-fullscreen', True)
    root.bind('<Escape>', lambda event: root.attributes('-fullscreen', False))

    root.mainloop()


