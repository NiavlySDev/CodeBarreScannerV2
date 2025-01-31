import os
import tkinter as tk
import requests
import subprocess
import sys
from PIL import Image, ImageTk
from bdd import *

required_packages = ["requests","tkinter","mysql.connector","mysql", "pillow"]
for package in required_packages:
    try:
        __import__(package)  # Tente d'importer le module
    except ImportError:  # Si le package n'est pas installé
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])


root = tk.Tk()
root.title("Scanner de Code-Barres")
root.geometry("600x600")
root.configure(bg="#2c3e50")

input_value, modifmode, copymode, retirermode, resetmode, displayinfomode, source_barcode = "", False, False, False, False, False, None

header = tk.Label(root, text="Scanner de Code-Barre", font=("Helvetica", 18, "bold"), fg="#ecf0f1", bg="#2c3e50")
header.pack(pady=10)


def open_all_articles_window():
    data = load_existing_data()

    articles_window = tk.Toplevel(root)
    articles_window.title("Tous les Articles")

    # Define actions for the buttons
    def delete_article(code):
        data = load_existing_data()
        if code in data:
            if data[code]["nombre"] > 0:
                data[code]["nombre"] -= 1
            save_data(data)
            articles_window.destroy()
            open_all_articles_window()

    def increment_count(code):
        data = load_existing_data()
        if code in data:
            data[code]["nombre"] += 1
            save_data(data)
            articles_window.destroy()
            open_all_articles_window()

    def reset_article(code):
        data = load_existing_data()
        if code in data:
            data[code]["nombre"] = 0
            save_data(data)
            articles_window.destroy()
            open_all_articles_window()

    articles_window.geometry("950x600")
    articles_window.configure(bg="#34495e")

    tk.Label(articles_window, text="Liste des Articles", font=("Helvetica", 16, "bold"), bg="#34495e",
             fg="#ecf0f1").pack(pady=10)

    canvas = tk.Canvas(articles_window, bg="#34495e", highlightbackground="#2c3e50")
    scrollbar = tk.Scrollbar(articles_window, orient="vertical", command=canvas.yview, bg="#34495e",
                             troughcolor="#2c3e50")
    scrollable_frame = tk.Frame(canvas, bg="#34495e")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    # Make the scrollbar functional for the entire page with mousewheel
    articles_window.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * int(e.delta / 120), "units"))

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    column = 0
    row = 0
    for code, product in data.items():
        frame = tk.Frame(scrollable_frame, bg="#2c3e50", highlightbackground="#ecf0f1", highlightthickness=1)
        frame.grid(row=row, column=column, padx=10, pady=5, sticky="nsew")

        column += 1
        if column >= 3:
            column = 0
            row += 1

        name = product.get("nom", "Inconnu")
        brand = product.get("marque", "Inconnu")
        quantity = product.get("quantite", "Inconnu")
        product_type = product.get("type", "Inconnu")
        count = product.get("nombre", 0)
        image_url = product.get("image", "")

        tk.Label(frame, text=f"Nom: {name}", font=("Helvetica", 12, "bold"), bg="#2c3e50", fg="#ecf0f1").pack(
            anchor="w", padx=10)
        tk.Label(frame, text=f"Marque: {brand}", font=("Helvetica", 10), bg="#2c3e50", fg="#ecf0f1").pack(
            anchor="w", padx=10)
        tk.Label(frame, text=f"Quantité: {quantity}", font=("Helvetica", 10), bg="#2c3e50", fg="#ecf0f1").pack(
            anchor="w", padx=10)
        tk.Label(frame, text=f"Type: {product_type}", font=("Helvetica", 10), bg="#2c3e50", fg="#ecf0f1").pack(
            anchor="w", padx=10)
        tk.Label(frame, text=f"Nombre: {count}", font=("Helvetica", 10), bg="#2c3e50", fg="#ecf0f1").pack(
            anchor="w", padx=10)
        tk.Label(frame, text=f"Code-barre: {code}", font=("Helvetica", 8, "italic"), bg="#2c3e50", fg="#bdc3c7").pack(
            anchor="w", padx=10)

        # Add Delete button
        tk.Button(frame, text="Supprimer", font=("Helvetica", 8), bg="#e74c3c", fg="#ecf0f1",
                  command=lambda c=code: delete_article(c)).pack(side="left", padx=5, pady=5)

        # Add Increment button
        tk.Button(frame, text="Ajouter", font=("Helvetica", 8), bg="#27ae60", fg="#ecf0f1",
                  command=lambda c=code: increment_count(c)).pack(side="left", padx=5, pady=5)

        # Add Reset button
        tk.Button(frame, text="Réinitialiser", font=("Helvetica", 8), bg="#f1c40f", fg="#2c3e50",
                  command=lambda c=code: reset_article(c)).pack(side="left", padx=5, pady=5)

        if image_url:
            try:
                temp_image_path = f"images/{code}.png"
                if not os.path.exists(temp_image_path):
                    response = requests.get(image_url, stream=True)
                    response.raise_for_status()
                    img_data = response.content
                    os.makedirs("images", exist_ok=True)
                    with open(temp_image_path, "wb") as temp_file:
                        temp_file.write(img_data)
                pil_image = Image.open(temp_image_path)
                max_size = (200, 200)
                pil_image.thumbnail(max_size, Image.Resampling.LANCZOS)
                img = ImageTk.PhotoImage(pil_image)
                label = tk.Label(frame, image=img, bg="#2c3e50")
                label.image = img
                label.pack(anchor="w", padx=10)

                def cleanup_and_close():
                    articles_window.destroy()

                articles_window.protocol("WM_DELETE_WINDOW", cleanup_and_close)
            except (requests.RequestException, tk.TclError, IOError, ImportError) as e:
                print(f"Erreur : {e}")
                tk.Label(frame, text="Image non disponible", font=("Helvetica", 8), bg="#2c3e50", fg="#e74c3c").pack(
                    anchor="w", padx=10)
                


tk.Button(root, text="Voir les Articles", command=open_all_articles_window, font=("Helvetica", 10, "bold"),
          bg="#2c3e50", fg="#ecf0f1").pack(pady=5)

instructions = tk.Label(root, text="Entrez un code-barre et appuyez sur Entrée ou cliquez sur 'Submit'.\n",
                        font=("Helvetica", 10), fg="#bdc3c7", bg="#2c3e50")
instructions.pack(pady=5)

def load_existing_data():
    try:
        with open("output.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_data(data):
    with open("output.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    if BDD:
        start()
        savetobdd()  # Save changes to the database after modifying the JSON file
        stop()

def reset_all_data():
    data = load_existing_data()
    for key in data:
        data[key]["nombre"] = 0
    save_data(data)
    update_label_output("Tous les produits ont été réinitialisés à 0")

def open_statistics_window(event=None):
    data = load_existing_data()
    total_count = sum(product.get("nombre", 0) for product in data.values())
    unique_codes = len(data)
    average_count = total_count / unique_codes if unique_codes > 0 else 0
    top_n = sorted(data.items(), key=lambda x: x[1].get("nombre", 0), reverse=True)[:5]

    stats_window = tk.Toplevel(root)
    stats_window.title("Statistics")
    stats_window.geometry("600x600")
    stats_window.configure(bg="#34495e")

    tk.Label(stats_window, text="Statistiques des Produits", font=("Helvetica", 14, "bold"), bg="#34495e",
             fg="#ecf0f1").pack(pady=10)
    tk.Label(stats_window, text=f"Nombre Total de Produits : {total_count}", font=("Helvetica", 12), bg="#34495e",
             fg="#ecf0f1").pack(
        pady=5)
    tk.Label(stats_window, text=f"Codes-Barres Uniques : {unique_codes}", font=("Helvetica", 12), bg="#34495e",
             fg="#ecf0f1").pack(
        pady=5)
    tk.Label(stats_window, text=f"Nombre Moyen par Produit : {average_count:.2f}", font=("Helvetica", 12),
             bg="#34495e", fg="#ecf0f1").pack(
        pady=5)

    # Calculate percentage contribution of top 5 products
    top_5_total = sum(x[1].get("nombre", 0) for x in top_n)
    top_5_percentage = (top_5_total / total_count * 100) if total_count > 0 else 0
    tk.Label(stats_window, text=f"Contribution du Top 5 aux Scans Totaux : {top_5_percentage:.2f}%",
             font=("Helvetica", 12),
             bg="#34495e", fg="#ecf0f1").pack(pady=5)

    # Identify product with the lowest count
    if data:
        least_scanned_product = min(data.items(), key=lambda x: x[1].get("nombre", float('inf')))
        least_scanned_details = f"{least_scanned_product[0]}: {least_scanned_product[1].get('nom', 'Inconnu')} - {least_scanned_product[1].get('nombre', 0)} fois"
    else:
        least_scanned_details = "Aucun produit"
    tk.Label(stats_window, text=f"Produit le Moins Scanné : {least_scanned_details}", font=("Helvetica", 12),
             bg="#fefbd8").pack(pady=5)

    tk.Label(stats_window, text="Top 5 des Produits les Plus Scannés :", font=("Helvetica", 12, "bold"),
             bg="#fefbd8").pack(
        pady=10)
    for code, product in top_n:
        tk.Label(stats_window, text=f"{code}: {product.get('nom', 'Inconnu')} - {product.get('nombre', 0)} fois",
                 font=("Helvetica", 10), bg="#fefbd8").pack(anchor="w", padx=20)

    tk.Button(stats_window, text="Fermer", command=stats_window.destroy, font=("Helvetica", 10, "bold"),
              bg="#e74c3c", fg="white").pack(pady=20)

def update_label_output(message):
    label_output.config(text=message, fg="#2c3e50", bg="#d4edda", wraplength=500, justify="left")

def reset_input():
    entry.delete(0, tk.END)
    ok_button.pack_forget()

def modify_data(data, fetched_data=None):
    if fetched_data:
        product = fetched_data.get("product", {})
        data[input_value] = {
            "marque": product.get("brands", "Unknown"),
            "nom": product.get("product_name_fr", "Unknown"),
            "type": product.get("product_type", "Unknown"),
            "quantite": f'{product.get("product_quantity", 0)} {product.get("product_quantity_unit", "unit")}',
            "image": product.get("image_front_url", "No Image"),
            "nombre": data.get(input_value, {}).get("nombre", 0) + 1
        }
        update_label_output(f"Produit ajouté : {input_value}\nNom: {data[input_value].get('nom', 'Inconnu')}, "
                            f"Marque: {data[input_value].get('marque', 'Inconnu')}, "
                            f"Quantité: {data[input_value].get('quantite', 'Inconnu')}, "
                            f"Nombre: {data[input_value].get('nombre', 0)}")
    else:
        data[input_value]["nombre"] += 1
        update_label_output(f"Produit mis à jour : {input_value}\nNom: {data[input_value].get('nom', 'Inconnu')}, "
                            f"Marque: {data[input_value].get('marque', 'Inconnu')}, "
                            f"Quantité: {data[input_value].get('quantite', 'Inconnu')}, "
                            f"Nombre: {data[input_value].get('nombre', 0)}")
    save_data(data)

def process_input(event=None):
    global input_value, source_barcode, modifmode, retirermode, resetmode, copymode, displayinfomode
    if BDD:
        start()
        loadfrombdd()
        stop()
    input_value = entry.get()

    if input_value == "28061":
        retirermode, modifmode, copymode, resetmode, displayinfomode = False, False, False, False, False
        update_label_output("Mode Ajout activé")
        reset_input()
        return
    elif input_value == "28062":
        retirermode, modifmode, copymode, resetmode, displayinfomode = True, False, False, False, False
        update_label_output("Mode Retirer activé")
        reset_input()
        return
    elif input_value == "28063":
        retirermode, modifmode, copymode, resetmode, displayinfomode = False, True, False, False, False
        update_label_output("Mode Modification activé")
        reset_input()
        return
    elif input_value == "28064":
        retirermode, modifmode, copymode, resetmode, displayinfomode = False, False, True, False, False
        update_label_output("Mode Copie activé")
        reset_input()
        return
    elif input_value == "28065":
        retirermode, modifmode, copymode, resetmode, displayinfomode = False, False, False, True, False
        update_label_output("Mode Reset activé")
        reset_input()
        return
    elif input_value == "28066":
        retirermode, modifmode, copymode, resetmode, displayinfomode = False, False, False, False, True
        update_label_output("Mode Afficher Informations activé")
        reset_input()
        return

    data = load_existing_data()

    if retirermode:
        if input_value in data:
            if data[input_value]["nombre"] >= 1:
                data[input_value]["nombre"] -= 1
                update_label_output(
                    f"Produit retiré : {input_value}\nNombre après retrait : {data[input_value]['nombre']}")
            else:
                update_label_output(f"Produit non retirable: {input_value} (nombre tombé à 0)")
            save_data(data)
        else:
            update_label_output(f"Code-Barre introuvable : {input_value}")
        reset_input()
        return

    if copymode:
        if not source_barcode:
            if input_value in data:
                source_barcode = input_value
                update_label_output(f"Code source sélectionné pour la copie : {source_barcode}")
            else:
                update_label_output(f"Code source introuvable : {input_value}")
        else:
            if source_barcode in data:
                data[input_value] = data[source_barcode].copy()
                save_data(data)
                update_label_output(f"Les informations du code {source_barcode} ont été copiées vers : {input_value}")
                source_barcode = None
            else:
                update_label_output(f"Code source introuvable dans les données : {source_barcode}")
        reset_input()
        return

    if displayinfomode:
        if input_value in data:
            display_product_info(data, input_value)
        else:
            update_label_output(f"Code-Barres introuvable : {input_value}")
        reset_input()
        return

    if resetmode:
        if input_value in data:
            data[input_value]["nombre"] = 0
            save_data(data)
            update_label_output(f"Produit réinitialisé : {input_value}\nNombre: 0")
        else:
            update_label_output(f"Code source introuvable dans les données : {source_barcode}")
        reset_input()
        return

    if modifmode:
        if input_value in data:
            update_label_output(f"Produit trouvé: {input_value}")
            ok_button.config(text="Modifier")
            ok_button.pack(pady=5)
        else:
            update_label_output(f"Code-Barres non trouvé: {input_value}")
        return

    fetched_data = get_data(input_value)
    if not fetched_data and input_value not in data:
        update_label_output(f"Code Barre non trouvé: {input_value}")
        ok_button.pack(pady=5)
        return
    modify_data(data, fetched_data)
    reset_input()

def validate_input(new_value):
    return new_value.isdigit() or new_value == ""

def open_manual_entry_window():
    global input_value
    manual_window = tk.Toplevel(root)
    manual_window.title("Entrée Manuelle")
    manual_window.geometry("400x400")
    manual_window.configure(bg="#34495e")

    def save(event=None):
        data = load_existing_data()
        entry_data = {field: entries[field].get() for field in entries}
        entry_data["quantite"] = f'{entries["quantite"].get()} {entries["unit"].get()}'
        entry_data["nombre"] = 1
        data[input_value] = entry_data
        save_data(data)
        description = f"Nom: {entry_data.get('nom', 'Inconnu')}, Marque: {entry_data.get('marque', 'Inconnu')}, " \
                      f"Quantité: {entry_data.get('quantite', 'Inconnu')}, Nombre: {entry_data.get('nombre', 1)}"
        update_label_output(f"Produit {'Modifié' if modifmode else 'Ajouté'} : {input_value}\n{description}")
        manual_window.destroy()
        reset_input()

    fields = ['marque', 'nom', 'type', 'quantite', 'unit', 'image']
    entries = {field: tk.Entry(manual_window) for field in fields}

    tk.Label(manual_window, text="Entrez les informations du produit", font=("Helvetica", 12, "bold"),
             bg="#34495e", fg="#ecf0f1").pack(pady=10)
    for field in fields:
        tk.Label(manual_window, text=field.capitalize(), bg="#34495e", fg="#ecf0f1").pack()
        entries[field].pack(pady=5)

    if modifmode:
        existing_data = load_existing_data().get(input_value, {})
        for k, v in existing_data.items():
            if k in entries:
                entries[k].insert(0, v)

    tk.Button(manual_window, text="Save", command=save, bg="#2980b9", fg="#ecf0f1",
              font=("Helvetica", 10, "bold")).pack(
        pady=10)
    manual_window.bind("<Return>", save)

def enter_modification_mode(event=None):
    global modifmode, retirermode
    modifmode = not modifmode
    retirermode = False  # Disable retirer mode when entering modification mode
    update_label_output(f"Mode {'Modification' if modifmode else 'Ajout'} activé")
    reset_input()

def enter_removal_mode(event=None):
    global retirermode, modifmode
    retirermode = not retirermode
    modifmode = False  # Disable modification mode when entering retirer mode
    update_label_output(f"Mode {'Retirer' if retirermode else 'Ajout'} activé")
    reset_input()

def toggle_copy_mode(event=None):
    global copymode, source_barcode
    copymode = not copymode
    source_barcode = None
    update_label_output(f"Mode {'Copie' if copymode else 'Ajout'} activé")
    reset_input()

def display_product_info(data, input_value):
    product = data.get(input_value, {})
    if not product:
        update_label_output(f"Produit introuvable pour le Code-Barres : {input_value}")
        return

    info = (f"Code-Barre : {input_value}\n"
            f"Nom : {product.get('nom', 'Inconnu')}\n"
            f"Marque : {product.get('marque', 'Inconnu')}\n"
            f"Type : {product.get('type', 'Inconnu')}\n"
            f"Quantité : {product.get('quantite', 'Inconnu')}\n"
            f"Nombre : {product.get('nombre', 'Inconnu')}\n"
            f"Image : {product.get('image', 'Inconnu')}")
    update_label_output(info)

def enter_reset_mode(event=None):
    global resetmode
    resetmode = not resetmode
    update_label_output(f"Mode {'Réinitialiser' if resetmode else 'Ajout'} activé")
    reset_input()

def open_help_window():
    help_window = tk.Toplevel(root)
    help_window.title("Aide")
    help_window.geometry("600x600")
    help_window.configure(bg="#34495e")

    tk.Label(help_window, text="Aide - Modes et Raccourcis", font=("Helvetica", 14, "bold"), bg="#34495e",
             fg="#ecf0f1").pack(pady=10)

    help_text = (
        "Modes disponibles et leurs activations :\n"
        "1. Mode Ajout (Défaut) - Ajoute un produit :\n"
        "   - Code-barres 28061\n\n"
        "2. Mode Retirer - Réduit la quantité d’un produit :\n"
        "   - Code-barres 28062 ou appuyez sur R\n\n"
        "3. Mode Modification - Modifie les données d'un produit :\n"
        "   - Code-barres 28063 ou appuyez sur M\n\n"
        "4. Mode Copie - Copie les données d’un produit pour un autre :\n"
        "   - Code-barres 28064 ou appuyez sur C\n\n"
        "5. Mode Reset - Réinitialise les quantités d’un produit à 0 :\n"
        "   - Code-barres 28065 ou appuyez sur X\n\n"
        "6. Mode Afficher Informations - Montre les détails d’un produit :\n"
        "   - Code-barres 28066 ou appuyez sur I\n\n"
        "Raccourcis supplémentaires :\n"
        "- Réinitialiser tous les produits : Appuyez sur Fin\n"
        "- Effacer le champ d'entrée : Appuyez sur Supprimer\n"
        "- Accéder aux statistiques : Appuyez sur S\n"
        "- Accéder à cette aide : Appuyez sur H\n"
    )

    tk.Label(help_window, text=help_text, font=("Helvetica", 10), justify="left", bg="#dff9fb", wraplength=450).pack(
        pady=10)

    tk.Button(help_window, text="Fermer", command=help_window.destroy, font=("Helvetica", 10, "bold"), bg="#e74c3c",
              fg="white").pack(pady=20)

def toggle_display_info_mode():
    global displayinfomode
    displayinfomode = not displayinfomode
    update_label_output(f"Mode {'Afficher Informations' if displayinfomode else 'Ajout'} activé")
    reset_input()

def get_data(number):
    url = f"https://world.openfoodfacts.org/api/v2/product/{number}.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except:
        return None

validate_command = root.register(validate_input)
entry = tk.Entry(root, validate="key", validatecommand=(validate_command, "%P"), font=("Helvetica", 12), bg="#2c3e50",
                 fg="#ecf0f1", insertbackground="#ecf0f1")
entry.pack(pady=10, ipadx=5, ipady=2)
entry.focus()

submit_button = tk.Button(root, text="Soumettre", command=process_input, font=("Helvetica", 10, "bold"), bg="#2980b9",
                          fg="#ecf0f1")
submit_button.pack(pady=5)

reset_all_button = tk.Button(root, text="Réinitialiser Tout", command=reset_all_data, font=("Helvetica", 10, "bold"),
                             bg="#c0392b",
                             fg="#ecf0f1")
reset_all_button.pack(pady=5)

stats_button = tk.Button(root, text="Voir les Statistiques", command=open_statistics_window,
                         font=("Helvetica", 10, "bold"),
                         bg="#6c3483", fg="#ecf0f1")
stats_button.pack(pady=5)

help_button = tk.Button(root, text="Aide", command=open_help_window, font=("Helvetica", 10, "bold"), bg="#16a085",
                        fg="#ecf0f1")
help_button.pack(pady=5)

ok_button = tk.Button(root, text="Entrée Manuelle", command=open_manual_entry_window, font=("Helvetica", 10),
                      bg="#d35400", fg="#ecf0f1")
ok_button.pack_forget()

root.bind("<Return>", process_input)
root.bind("m", enter_modification_mode)
root.bind("c", toggle_copy_mode)
root.bind("r", enter_removal_mode)
root.bind("x", enter_reset_mode)
root.bind("s", open_statistics_window)
root.bind("i", lambda event: toggle_display_info_mode())
root.bind("<End>", lambda event: reset_all_data())
root.bind("<Delete>", lambda event: reset_input())
root.bind("h", lambda event: open_help_window())

label_output = tk.Label(root, text="", font=("Helvetica", 10), bg="#2c3e50", fg="#ecf0f1")
label_output.pack(pady=10, fill="x", padx=20, ipadx=10, ipady=10)

footer = tk.Label(root, text="© 2025 Sylvain Crocquevieille - Tous droits réservés", font=("Helvetica", 8),
                  fg="#7f8c8d",
                  bg="#2c3e50")
footer.pack(side="bottom", pady=10)

if BDD:
    start()
    savetobdd()
    stop()

root.mainloop()

