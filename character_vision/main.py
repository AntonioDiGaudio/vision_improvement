import tkinter as tk
import random
import string
import json
from datetime import datetime

class LetterMemoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Letter Memory Test") # Imposta la finestra a schermo intero, ma ridimensionabile
        root.geometry("1080x720")
        root.resizable(True, True)  # La finestra può essere ridimensionata sia in larghezza che in altezza
        root.attributes('-fullscreen', True)

        self.time_var = tk.DoubleVar()

        self.num_letters_initial_var = tk.IntVar()
        self.num_letters_final_var = tk.IntVar()

        self.setup_initial_screen()
    
    def setup_initial_screen(self):
        # Cambia il font delle Label e delle Entry
        font_style = ("Arial", 16)  # Puoi cambiare il font e la dimensione qui

        tk.Label(self.root, text="Tempo in secondi:", font=font_style).pack(pady=10)
        tk.Entry(self.root, textvariable=self.time_var, font=font_style).pack(pady=10)

        tk.Label(self.root, text="Numero di lettere iniziali:", font=font_style).pack(pady=10)
        tk.Entry(self.root, textvariable=self.num_letters_initial_var, font=font_style).pack(pady=10)

        tk.Label(self.root, text="Numero di lettere finali:", font=font_style).pack(pady=10)
        tk.Entry(self.root, textvariable=self.num_letters_final_var, font=font_style).pack(pady=10)

        self.error_label = tk.Label(self.root, text="", fg="red", font=font_style)
        self.error_label.pack(pady=10)

        tk.Button(self.root, text="Inizia", command=self.start_test, font=font_style).pack(pady=10)
        tk.Button(self.root, text="Progress", command=self.show_progress, font=font_style).pack(pady=10)

    def start_test(self):
        self.time = float(self.time_var.get())
        self.num_letters_initial = self.num_letters_initial_var.get()
        self.num_letters_final = self.num_letters_final_var.get()

        if not self.validate_inputs():
            return

        self.letters_initial = random.sample(string.ascii_uppercase, self.num_letters_initial)

        for widget in self.root.winfo_children():
            widget.destroy()

        self.display_initial_letters()

        # Dopo che è trascorso il tempo, chiama il metodo per mostrare le lettere finali
        self.root.after(int(self.time * 1000), self.display_final_letters)


    def validate_inputs(self):
        if self.time <= 0:
            self.error_label.config(text="Il tempo deve essere un numero positivo.")
            return False
        if not (1 <= self.num_letters_initial <= 26):
            self.error_label.config(text="Il numero di lettere iniziali deve essere compreso tra 1 e 26.")
            return False
        if not (self.num_letters_initial <= self.num_letters_final <= 26):
            self.error_label.config(text="Il numero di lettere finali deve essere un numero positivo e compreso tra il numero di lettere iniziali e 26.")
            return False
        return True

    def display_initial_letters(self):
        self.canvas = tk.Canvas(self.root, width=self.root.winfo_screenwidth(), height=self.root.winfo_screenheight())
        self.canvas.pack()

        positions = []
        for letter in self.letters_initial:
            attempts = 0
            while attempts < 5000:  # Aumenta ulteriormente il limite di tentativi
                x = random.randint(100, self.root.winfo_screenwidth() - 100)
                y = random.randint(100, self.root.winfo_screenheight() - 100)
                if all(abs(x - px) > 50 and abs(y - py) > 50 for px, py in positions):
                    positions.append((x, y))
                    break
                attempts += 1
            else:
                print(f"Could not place letter {letter} without overlap.")

            if attempts < 5000:  # Aggiungi la lettera solo se è stata trovata una posizione valida
                self.canvas.create_text(x, y, text=letter, font=("Helvetica", 48))


    def display_final_letters(self):
        remaining_alphabet = list(set(string.ascii_uppercase) - set(self.letters_initial))
        remaining_letters = random.sample(remaining_alphabet, self.num_letters_final - self.num_letters_initial)
        self.final_letters = self.letters_initial + remaining_letters
        random.shuffle(self.final_letters)  # Mescola le lettere finali per evitare che le lettere iniziali siano sempre nelle stesse posizioni

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
        for i, letter in enumerate(self.final_letters):
            row, column = divmod(i, 5)  # 5 colonne per riga
            btn = tk.Button(self.scrollable_frame, text=letter, width=5, height=2, font=("Helvetica", 24),
                            command=lambda l=letter: self.toggle_button(l))
            btn.grid(row=row, column=column, padx=10, pady=10)
            self.buttons[letter] = btn

        tk.Button(self.root, text="Invia", command=self.check_results, font=("Helvetica", 16)).pack(pady=20)

    def toggle_button(self, letter):
        button = self.buttons[letter]
        if button["bg"] == "blue":
            button["bg"] = "SystemButtonFace" if self.root.tk.call("tk", "windowingsystem") == "win32" else "lightgrey"
        else:
            button["bg"] = "blue"

    def check_results(self):
        selected_letters = [letter for letter, button in self.buttons.items() if button["bg"] == "blue"]
        correct_letters = [letter for letter in selected_letters if letter in self.letters_initial]
        score = len(correct_letters)

        # Salvataggio dei progressi
        self.save_progress(score)

        result_message = f"Lettere selezionate: {', '.join(selected_letters)}\n" \
                         f"Lettere corrette: {', '.join(correct_letters)}"
        initial_letters_message = f"Lettere iniziali: {', '.join(self.letters_initial)}"
        score_message = f"Score: {score}/{self.num_letters_initial}"

        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text=result_message, font=("Helvetica", 16)).pack(pady=10)
        tk.Label(self.root, text=initial_letters_message, font=("Helvetica", 16)).pack(pady=10)
        tk.Label(self.root, text=score_message, font=("Helvetica", 16)).pack(pady=10)
        tk.Button(self.root, text="Progress", command=self.show_progress, font=("Helvetica", 16)).pack(pady=10)

    def save_progress(self, score):
        # Carica progressi esistenti se presenti
        try:
            with open("progress.json", "r") as file:
                progress_data = json.load(file)
        except FileNotFoundError:
            progress_data = {"progressi": []}

        # Aggiungi nuovo progresso
        now = datetime.now().strftime("%d/%m/%y %H:%M")
        new_progress = {"time-stamp": now, "score": f"{score}/{self.num_letters_initial}"}
        progress_data["progressi"].append(new_progress)

        # Salva progressi aggiornati
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
    app = LetterMemoryApp(root)

    # Imposta la finestra a schermo intero, ma ridimensionabile
    root.attributes('-fullscreen', True)
    root.bind('<Escape>', lambda event: root.attributes('-fullscreen', False))

    root.mainloop()

