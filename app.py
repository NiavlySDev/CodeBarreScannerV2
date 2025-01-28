import tkinter as tk
import api
import json

root = tk.Tk()
root.title("CodeBarreScanner")
root.geometry("600x400")
root.configure(bg="#f0f8ff")

input_value, modifmode, copymode, source_barcode = "", False, False, None

header = tk.Label(root, text="Scanner de Code-Barre", font=("Helvetica", 18, "bold"), fg="#2c3e50", bg="#f0f8ff")
header.pack(pady=10)

instructions = tk.Label(root, text="Entrez un code-barre et appuyez sur Entrée ou cliquez sur 'Submit'.\n"
                                   "Utilisez 'm' pour basculer entre les modes.\n"
                                   "Utilisez 'c' pour activer/désactiver le mode copie.", font=("Helvetica", 10),
                        fg="#34495e", bg="#f0f8ff")
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
                            f"Quantité: {data[input_value].get('quantite', 'Inconnu')}")
    else:
        data[input_value]["nombre"] += 1
        update_label_output(f"Produit mis à jour : {input_value}\nNom: {data[input_value].get('nom', 'Inconnu')}, "
                            f"Marque: {data[input_value].get('marque', 'Inconnu')}, "
                            f"Quantité: {data[input_value].get('quantite', 'Inconnu')}")
    save_data(data)


def process_input(event=None):
    global input_value, source_barcode
    input_value = entry.get()
    data = load_existing_data()

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

    if modifmode:
        if input_value in data:
            update_label_output(f"Produit trouvé: {input_value}")
            ok_button.config(text="Modifier")
            ok_button.pack(pady=5)
        else:
            update_label_output(f"Code Barre non trouvé: {input_value}")
        return

    fetched_data = api.get_data(input_value)
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
    manual_window.configure(bg="#fefbd8")

    def save(event=None):
        data = load_existing_data()
        entry_data = {field: entries[field].get() for field in entries}
        entry_data["quantite"] = f'{entries["quantite"].get()} {entries["unit"].get()}'
        entry_data["nombre"] = 1
        data[input_value] = entry_data
        save_data(data)
        description = f"Nom: {entry_data.get('nom', 'Inconnu')}, Marque: {entry_data.get('marque', 'Inconnu')}, " \
                      f"Quantité: {entry_data.get('quantite', 'Inconnu')}"
        update_label_output(f"Produit {'Modifié' if modifmode else 'Ajouté'} : {input_value}\n{description}")
        manual_window.destroy()
        reset_input()

    fields = ['marque', 'nom', 'type', 'quantite', 'unit', 'image']
    entries = {field: tk.Entry(manual_window) for field in fields}

    tk.Label(manual_window, text="Entrez les informations du produit", font=("Helvetica", 12, "bold"),
             bg="#fefbd8").pack(pady=10)
    for field in fields:
        tk.Label(manual_window, text=field.capitalize(), bg="#fefbd8").pack()
        entries[field].pack(pady=5)

    if modifmode:
        existing_data = load_existing_data().get(input_value, {})
        for k, v in existing_data.items():
            if k in entries:
                entries[k].insert(0, v)

    tk.Button(manual_window, text="Save", command=save, bg="#4caf50", fg="white", font=("Helvetica", 10, "bold")).pack(
        pady=10)
    manual_window.bind("<Return>", save)


def enter_modification_mode(event=None):
    global modifmode
    modifmode = not modifmode
    update_label_output(f"Mode {'Modification' if modifmode else 'Normal'} activé")
    reset_input()


def toggle_copy_mode(event=None):
    global copymode, source_barcode
    copymode = not copymode
    source_barcode = None
    update_label_output(f"Mode {'Copie' if copymode else 'Normal'} activé")
    reset_input()


validate_command = root.register(validate_input)
entry = tk.Entry(root, validate="key", validatecommand=(validate_command, "%P"), font=("Helvetica", 12), bg="#ecf0f1",
                 fg="#2c3e50")
entry.pack(pady=10, ipadx=5, ipady=2)
entry.focus()

submit_button = tk.Button(root, text="Submit", command=process_input, font=("Helvetica", 10, "bold"), bg="#3498db",
                          fg="white")
submit_button.pack(pady=5)

ok_button = tk.Button(root, text="Entrée Manuelle", command=open_manual_entry_window, font=("Helvetica", 10),
                      bg="#e67e22", fg="white")
ok_button.pack_forget()

root.bind("<Return>", process_input)
root.bind("m", enter_modification_mode)
root.bind("c", toggle_copy_mode)
root.bind("<Delete>", lambda event: reset_input())

label_output = tk.Label(root, text="", font=("Helvetica", 10), bg="#f0f8ff")
label_output.pack(pady=10, fill="x", padx=20, ipadx=10, ipady=10)

footer = tk.Label(root, text="© 2025 Sylvain Crocquevieille - Tous droits réservés", font=("Helvetica", 8),
                  fg="#95a5a6",
                  bg="#f0f8ff")
footer.pack(side="bottom", pady=10)

root.mainloop()
