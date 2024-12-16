import tkinter as tk
import random
from tkinter import filedialog, messagebox, Scrollbar, Canvas, Frame, Toplevel
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from PIL import Image, ImageTk
from pdf2image import convert_from_bytes

class AdditionGenerator:
    def __init__(self, main_root):
        self.main_root = main_root
        self.main_root.title("Générateur d'Additions")

        # Initialiser l'attribut additions
        self.additions = []
        self.preview_window = None  # Ajouter un attribut pour suivre la fenêtre de prévisualisation

        # Entrée pour le nombre maximum
        self.max_label = tk.Label(main_root, text="Nombre maximum :", font=("Helvetica", 12))
        self.max_label.pack(pady=5)
        self.max_entry = tk.Entry(main_root)
        self.max_entry.pack(pady=5)

        # Entrée pour le nombre d'additions
        self.num_additions_label = tk.Label(main_root, text="Nombre d'additions :", font=("Helvetica", 12))
        self.num_additions_label.pack(pady=5)
        self.num_additions_entry = tk.Entry(main_root)
        self.num_additions_entry.pack(pady=5)

        # Case à cocher pour afficher le cercle rouge
        self.show_circle_var = tk.BooleanVar(value=True)
        self.show_circle_checkbox = tk.Checkbutton(main_root, text="Afficher le cercle rouge", variable=self.show_circle_var)
        self.show_circle_checkbox.pack(pady=5)

        # Case à cocher pour autoriser les doublons d'opérations
        self.allow_duplicates_var = tk.BooleanVar(value=True)
        self.allow_duplicates_checkbox = tk.Checkbutton(main_root, text="Autoriser les doublons d'opérations", variable=self.allow_duplicates_var)
        self.allow_duplicates_checkbox.pack(pady=5)

        # Case à cocher pour autoriser le résultat nul
        self.allow_zero_result_var = tk.BooleanVar(value=True)
        self.allow_zero_result_checkbox = tk.Checkbutton(main_root, text="Autoriser le résultat nul", variable=self.allow_zero_result_var)
        self.allow_zero_result_checkbox.pack(pady=5)

        # Case à cocher pour autoriser les membres égaux à zéro
        self.allow_zero_members_var = tk.BooleanVar(value=True)
        self.allow_zero_members_checkbox = tk.Checkbutton(main_root, text="Autoriser un des membres à être égal à 0", variable=self.allow_zero_members_var)
        self.allow_zero_members_checkbox.pack(pady=5)

        # Bouton pour générer les additions
        self.generate_button = tk.Button(main_root, text="Générer des additions", command=self.generate_additions)
        self.generate_button.pack(pady=20)

        # Bouton pour enregistrer en tant que PDF
        self.save_pdf_button = tk.Button(main_root, text="Enregistrer comme PDF", command=self.save_as_pdf)
        self.save_pdf_button.pack(pady=5)

    def validate_entries(self):
        try:
            max_num = int(self.max_entry.get() or "0")
            num_additions = int(self.num_additions_entry.get() or "0")

            if max_num <= 0:
                raise ValueError("Le nombre maximum doit être supérieur à zéro.")
            if num_additions <= 0:
                raise ValueError("Le nombre d'additions doit être positif.")

            return max_num, num_additions
        except ValueError as e:
            messagebox.showerror("Erreur", str(e))
            return None

    def generate_additions(self):
        validation_result = self.validate_entries()
        if validation_result is None:
            return

        # Stocke max_num comme attribut de classe pour l'utiliser plus tard
        self.max_num, num_additions = validation_result

        self.additions = []
        used_operations = set()

        while len(self.additions) < num_additions:
            a = random.randint(0, self.max_num)  # Premier membre aléatoire dans la plage [0, max_num]
            b = random.randint(0, self.max_num - a)  # Deuxième membre tel que a + b <= max_num

            if not self.allow_zero_result_var.get() and a + b == 0:
                continue
            if not self.allow_duplicates_var.get() and (a, b) in used_operations:
                continue

            # Vérifie si l'un des membres peut être égal à zéro
            if not self.allow_zero_members_var.get() and (a == 0 or b == 0):
                continue

            # Ajoute l'addition à la liste et aux opérations utilisées
            self.additions.append((a, b))
            used_operations.add((a, b))

        # Générer et afficher le PDF
        self.display_pdf()

    def create_pdf_in_memory(self):
        pdf_buffer = BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=letter)
        width, height = letter
        margin = 20  # Marges de 20 points
        y_position = height - margin

        for a, b in self.additions:
            if y_position < margin + 100:  # Si la position y est trop basse, ajouter une nouvelle page
                c.showPage()
                y_position = height - margin

            # Dessiner le fond grisé et l'addition
            c.setFillColorRGB(0.9, 0.9, 0.9)
            c.rect(margin, y_position - 30, width - 2 * margin, 30, fill=1)
            c.setFillColorRGB(0, 0, 0)
            c.drawString(margin + 10, y_position - 15, f"{a} + {b} =")
            y_position -= 40

            # Dessiner la bande numérique avec une longueur correspondant à la largeur de la page
            c.drawString(margin, y_position - 10, "Bande numérique (max: {}):".format(self.max_num))
            y_position -= 20

            # Ligne de graduation correspondant à la largeur de la page
            c.line(margin, y_position, width - margin, y_position)

            for i in range(0, self.max_num + 1):
                x = margin + (i / self.max_num) * (width - 2 * margin)
                if i % 5 == 0:
                    c.line(x, y_position - 10, x, y_position + 8)
                else:
                    c.line(x, y_position - 5, x, y_position + 4)

                if i % 5 == 0:
                    c.drawCentredString(x, y_position - 20, str(i))

                if self.show_circle_var.get() and i == a:
                    c.setStrokeColorRGB(1, 0, 0)
                    c.circle(x, y_position, 5)
                    c.setStrokeColorRGB(0, 0, 0)

            y_position -= 50

        c.save()
        pdf_buffer.seek(0)
        return pdf_buffer

    def display_pdf(self):
        # Fermer la fenêtre de prévisualisation existante si elle est ouverte
        if self.preview_window is not None:
            self.preview_window.destroy()

        pdf_buffer = self.create_pdf_in_memory()

        # Convertir le PDF en images
        images = convert_from_bytes(pdf_buffer.getvalue())

        # Afficher les images dans une nouvelle fenêtre Tkinter
        self.preview_window = Toplevel(self.main_root)
        self.preview_window.title("Prévisualisation du PDF")

        # Définir la taille initiale de la fenêtre à 400 pixels de large en format A4 portrait
        initial_width = 400
        initial_height = int(initial_width * (297 / 210))  # Ratio A4 portrait
        self.preview_window.geometry(f"{initial_width}x{initial_height}")

        # Créer un Canvas pour afficher l'image
        canvas = Canvas(self.preview_window, bg="white")
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Ajouter une barre de défilement
        scrollbar_y = Scrollbar(self.preview_window, orient="vertical", command=canvas.yview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x = Scrollbar(self.preview_window, orient="horizontal", command=canvas.xview)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        # Créer un Frame dans le Canvas pour contenir l'image
        frame = Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        # Redimensionner les images pour qu'elles s'adaptent à la taille de la fenêtre
        self.img_labels = []
        self.images = images
        self.canvas = canvas
        self.frame = frame

        # Planifier le redimensionnement des images après un court délai
        self.preview_window.after(100, self.resize_images)

        # Ajuster la taille du Canvas pour afficher l'image à l'échelle de la fenêtre
        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        canvas.bind("<Configure>", on_configure)

        self.preview_window.mainloop()

    def resize_images(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

        for img in self.images:
            # Redimensionner l'image pour qu'elle s'adapte à la taille de la fenêtre
            img_width, img_height = img.size
            window_width = self.canvas.winfo_width()
            window_height = self.canvas.winfo_height()
            if window_width > 0 and window_height > 0:
                ratio = min(window_width / img_width, window_height / img_height)
                new_width = int(img_width * ratio)
                new_height = int(img_height * ratio)
                img = img.resize((new_width, new_height), Image.LANCZOS)

            img_tk = ImageTk.PhotoImage(img)
            img_label = tk.Label(self.frame, image=img_tk)
            img_label.image = img_tk  # Keep a reference to avoid garbage collection
            img_label.pack()
            self.img_labels.append(img_label)

        # Planifier le redimensionnement des images après un court délai
        self.canvas.after(100, self.resize_images)

    def save_as_pdf(self):
        if not self.additions:
            messagebox.showerror("Erreur", "Veuillez d'abord générer les additions avant d'enregistrer le PDF.")
            return

        pdf_file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])

        if not pdf_file_path:
            return

        pdf_buffer = self.create_pdf_in_memory()

        with open(pdf_file_path, 'wb') as f:
            f.write(pdf_buffer.getvalue())

        messagebox.showinfo("Succès", "PDF enregistré avec succès.")

if __name__ == "__main__":
    main_root = tk.Tk()
    app = AdditionGenerator(main_root)
    main_root.mainloop()
