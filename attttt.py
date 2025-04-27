import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import pandas as pd
import uuid
try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError as e:
    print(f"Erreur d'importation des bibliothèques matplotlib ou numpy : {e}")
    messagebox.showerror("Erreur", "Veuillez installer matplotlib et numpy pour utiliser Flexilog.")
    exit()

class FlexilogApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Flexilog - Solution logistique pour PME/TPE")
        self.root.geometry("1200x700")
        self.root.configure(bg="#F5F7FA")
        self.articles = []
        self.mouvements = []
        self.clients = []
        self.fournisseurs = []
        self.commandes = []
        self.depots = [
            {"nom": "Entrepôt Casablanca", "id": str(uuid.uuid4())},
            {"nom": "Stock Tanger", "id": str(uuid.uuid4())},
            {"nom": "Dépôt Marrakech", "id": str(uuid.uuid4())},
            {"nom": "Entrepôt Fès", "id": str(uuid.uuid4())},
            {"nom": "Dépôt Agadir", "id": str(uuid.uuid4())},
            {"nom": "Stock Rabat", "id": str(uuid.uuid4())},
            {"nom": "Entrepôt Meknès", "id": str(uuid.uuid4())},
            {"nom": "Dépôt Oujda", "id": str(uuid.uuid4())}
        ]
        self.categories = ["Électronique", "Textile", "Alimentaire"]
        self.create_menu()

    def create_menu(self):
        menu_frame = tk.Frame(self.root, bg="#1A3C5A", width=250)
        menu_frame.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(menu_frame, text="Flexilog", font=("Arial", 18, "bold"), fg="white", bg="#1A3C5A", pady=20).pack(fill=tk.X)
        buttons = [
            ("📊 Tableau de bord", self.show_dashboard),
            ("📦 Gestion des articles", self.gestion_articles),
            ("📋 Suivi de stock", self.suivi_stock),
            ("🔄 Entrées et sorties", self.entrees_sorties),
            ("👥 Fournisseurs et clients", self.gestion_contacts),
            ("🏬 Gestion des dépôts", self.gestion_depots),
            ("❌ Quitter", self.root.quit)
        ]
        style = ttk.Style()
        style.configure("Menu.TButton", font=("Arial", 12, "bold"), foreground="white", background="#4A90E2", padding=10, borderwidth=0)
        style.map("Menu.TButton", background=[("active", "#3267D6"), ("!disabled", "#4A90E2")], foreground=[("active", "white")])
        for txt, cmd in buttons:
            button = ttk.Button(menu_frame, text=txt, command=cmd, style="Menu.TButton")
            button.pack(fill=tk.X, padx=10, pady=5)
        self.main_frame = tk.Frame(self.root, bg="#F5F7FA")
        self.main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.show_dashboard()

    def clear_main(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def gestion_depots(self):
        self.clear_main()
        header_frame = tk.Frame(self.main_frame, bg="#F5F7FA")
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(header_frame, text="🏬 Gestion des dépôts", font=("Arial", 16, "bold"), bg="#F5F7FA", fg="#1A3C5A").pack(anchor="w")
        
        # Form Frame
        form_frame = tk.Frame(self.main_frame, bg="white", bd=1, relief=tk.GROOVE)
        form_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Nom du dépôt
        tk.Label(form_frame, text="Nom du dépôt", bg="white", font=("Arial", 12, "bold"), fg="#1A3C5A").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        entry_nom = tk.Entry(form_frame, font=("Arial", 12), width=30)
        entry_nom.grid(row=0, column=1, padx=10, pady=10)
        
        # Catégorie
        tk.Label(form_frame, text="Catégorie", bg="white", font=("Arial", 12, "bold"), fg="#1A3C5A").grid(row=0, column=2, padx=10, pady=10, sticky="w")
        categorie_var = tk.StringVar(value=self.categories[0] if self.categories else "")
        categorie_combobox = ttk.Combobox(form_frame, textvariable=categorie_var, values=self.categories, width=18, font=("Arial", 12))
        categorie_combobox.grid(row=0, column=3, padx=10, pady=10)
        
        # Seuil critique
        tk.Label(form_frame, text="Seuil critique", bg="white", font=("Arial", 12, "bold"), fg="#1A3C5A").grid(row=0, column=4, padx=10, pady=10, sticky="w")
        entry_seuil = tk.Entry(form_frame, font=("Arial", 12), width=10)
        entry_seuil.grid(row=0, column=5, padx=10, pady=10)
        
        # Buttons
        form_button_frame = tk.Frame(form_frame, bg="white")
        form_button_frame.grid(row=1, column=0, columnspan=6, pady=10)
        style = ttk.Style()
        style.configure("Action.TButton", font=("Arial", 10, "bold"), padding=8)
        style.map("Action.TButton", background=[("active", "#3267D6")], foreground=[("active", "white")])
        ttk.Button(form_button_frame, text="➕ Ajouter Dépôt", command=lambda: ajouter_depot(), style="Action.TButton").pack(side=tk.LEFT, padx=5)
        btn_modifier = ttk.Button(form_button_frame, text="✏️ Modifier Dépôt", command=lambda: modifier_depot(), style="Action.TButton", state='disabled')
        btn_modifier.pack(side=tk.LEFT, padx=5)
        btn_seuil = ttk.Button(form_button_frame, text="⚙️ Définir Seuil", command=lambda: definir_seuil(), style="Action.TButton", state='disabled')
        btn_seuil.pack(side=tk.LEFT, padx=5)
        
        # Table Frame
        tree_frame = tk.Frame(self.main_frame, bg="white", bd=1, relief=tk.GROOVE)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(tree_frame, text="Stock par dépôt et catégorie", font=("Arial", 12, "bold"), bg="white", fg="#1A3C5A").pack(anchor="w", padx=10, pady=5)
        
        canvas = tk.Canvas(tree_frame, bg="white")
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=canvas.xview)
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Table Headers
        headers = ["Dépôt"]
        for category in self.categories:
            headers.extend([f"Stock {category}", f"Seuil {category}"])
        
        header_frame = tk.Frame(scrollable_frame, bg="#1A3C5A")
        header_frame.pack(fill=tk.X, pady=2)
        for col, header in enumerate(headers):
            tk.Label(header_frame, text=header, font=("Arial", 12, "bold"), fg="white", bg="#1A3C5A", width=15).grid(row=0, column=col, padx=2, pady=2)
        
        # Table Rows
        rows_frame = tk.Frame(scrollable_frame, bg="white")
        rows_frame.pack(fill=tk.BOTH, expand=True)
        
        selected_depot = [None]
        
        def display_depots():
            for widget in rows_frame.winfo_children():
                widget.destroy()
            for row, depot in enumerate(self.depots, start=1):
                bg_color = "#ffffff" if row % 2 == 0 else "#f9f9f9"
                row_frame = tk.Frame(rows_frame, bg=bg_color, bd=1, relief=tk.SOLID)
                row_frame.pack(fill=tk.X, pady=2)
                
                tk.Label(row_frame, text=depot["nom"], bg=bg_color, font=("Arial", 12), width=15).grid(row=0, column=0, padx=2, pady=2)
                
                # Calculate stock and display seuil for each category
                col = 1
                for category in self.categories:
                    # Stock calculation
                    stock = sum(m['qte'] for m in self.mouvements if m['depot'] == depot["nom"] and any(a['categorie'] == category and a['ref'] == m['article'] for a in self.articles) and m['type'] in ["Entrée", "Retour client"]) - \
                            sum(m['qte'] for m in self.mouvements if m['depot'] == depot["nom"] and any(a['categorie'] == category and a['ref'] == m['article'] for a in self.articles) and m['type'] in ["Sortie", "Retour fournisseur"])
                    stock = max(0, stock)
                    tk.Label(row_frame, text=str(stock), bg=bg_color, font=("Arial", 12), width=15).grid(row=0, column=col, padx=2, pady=2)
                    col += 1
                    
                    # Seuil (default to 10 if not set)
                    seuil = depot.get(f"seuil_{category}", 10)
                    tk.Label(row_frame, text=str(seuil), bg=bg_color, font=("Arial", 12), width=15).grid(row=0, column=col, padx=2, pady=2)
                    col += 1
                
                def select_depot(d=depot):
                    selected_depot[0] = d
                    entry_nom.delete(0, tk.END)
                    entry_nom.insert(0, d["nom"])
                    btn_modifier.state(['!disabled'])
                    btn_seuil.state(['!disabled'])
                    btn_supprimer.state(['!disabled'])
                
                ttk.Button(row_frame, text="✅ Sélectionner", command=lambda d=depot: select_depot(d), style="Action.TButton").grid(row=0, column=col, padx=2, pady=2)
        
        def ajouter_depot():
            nom = entry_nom.get().strip()
            if not nom:
                messagebox.showerror("Erreur", "Veuillez entrer un nom pour le dépôt.")
                return
            if any(depot["nom"] == nom for depot in self.depots):
                messagebox.showerror("Erreur", "Ce nom de dépôt existe déjà.")
                return
            new_depot = {"nom": nom, "id": str(uuid.uuid4())}
            for category in self.categories:
                new_depot[f"seuil_{category}"] = 10  # Default seuil
            self.depots.append(new_depot)
            messagebox.showinfo("Ajout", f"Dépôt '{nom}' ajouté avec succès.")
            clear_form()
            display_depots()
        
        def modifier_depot():
            if not selected_depot[0]:
                messagebox.showwarning("Avertissement", "Veuillez sélectionner un dépôt à modifier.")
                return
            nouveau_nom = entry_nom.get().strip()
            if not nouveau_nom:
                messagebox.showerror("Erreur", "Veuillez entrer un nouveau nom pour le dépôt.")
                return
            if any(depot["nom"] == nouveau_nom and depot["id"] != selected_depot[0]["id"] for depot in self.depots):
                messagebox.showerror("Erreur", "Ce nom de dépôt existe déjà.")
                return
            ancien_nom = selected_depot[0]["nom"]
            for depot in self.depots:
                if depot["id"] == selected_depot[0]["id"]:
                    depot["nom"] = nouveau_nom
                    break
            for mouvement in self.mouvements:
                if mouvement["depot"] == ancien_nom:
                    mouvement["depot"] = nouveau_nom
            messagebox.showinfo("Modification", f"Dépôt modifié avec succès en '{nouveau_nom}'.")
            clear_form()
            display_depots()
        
        def definir_seuil():
            if not selected_depot[0]:
                messagebox.showwarning("Avertissement", "Veuillez sélectionner un dépôt pour définir le seuil.")
                return
            try:
                seuil = int(entry_seuil.get().strip())
                if seuil < 0:
                    messagebox.showerror("Erreur", "Le seuil doit être un nombre positif.")
                    return
                categorie = categorie_var.get()
                if not categorie:
                    messagebox.showerror("Erreur", "Veuillez sélectionner une catégorie.")
                    return
                for depot in self.depots:
                    if depot["id"] == selected_depot[0]["id"]:
                        depot[f"seuil_{categorie}"] = seuil
                        break
                messagebox.showinfo("Seuil", f"Seuil pour {categorie} défini à {seuil}.")
                clear_form()
                display_depots()
            except ValueError:
                messagebox.showerror("Erreur", "Le seuil doit être un nombre valide.")
        
        def supprimer_depot():
            if not selected_depot[0]:
                messagebox.showwarning("Avertissement", "Veuillez sélectionner un dépôt à supprimer.")
                return
            if any(m["depot"] == selected_depot[0]["nom"] for m in self.mouvements):
                messagebox.showerror("Erreur", "Impossible de supprimer un dépôt avec des mouvements associés.")
                return
            self.depots = [d for d in self.depots if d["id"] != selected_depot[0]["id"]]
            messagebox.showinfo("Suppression", "Dépôt supprimé avec succès.")
            clear_form()
            display_depots()
        
        def clear_form():
            entry_nom.delete(0, tk.END)
            entry_seuil.delete(0, tk.END)
            categorie_var.set(self.categories[0] if self.categories else "")
            selected_depot[0] = None
            btn_modifier.state(['disabled'])
            btn_seuil.state(['disabled'])
            btn_supprimer.state(['disabled'])
        
        btn_supprimer = ttk.Button(form_button_frame, text="🗑️ Supprimer Dépôt", command=supprimer_depot, style="Action.TButton", state='disabled')
        btn_supprimer.pack(side=tk.LEFT, padx=5)
        
        display_depots()

    def show_dashboard(self):
        self.clear_main()
        header_frame = tk.Frame(self.main_frame, bg="#F5F7FA")
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(header_frame, text="📊 Tableau de bord", font=("Arial", 16, "bold"), bg="#F5F7FA", fg="#1A3C5A").pack(anchor="w")
        notebook = ttk.Notebook(self.main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        overview_frame = tk.Frame(notebook, bg="white")
        notebook.add(overview_frame, text="Vue synthétique")
        self.setup_dashboard_tab(overview_frame)

    def setup_dashboard_tab(self, frame):
        total_articles = len(self.articles)
        stock_alerte = sum(1 for a in self.articles if a['stock'] < a['seuil'])
        commandes_actives = len([c for c in self.commandes if c['statut'] == 'En attente'])
        valeur_stock = sum(a['stock'] * a['prix'] for a in self.articles)
        retards_fournisseurs = len([c for c in self.commandes if c['type'] == 'Fournisseur' and c['statut'] == 'Retard'])
        kpi_data = [
            ("Articles", str(total_articles)),
            ("Alertes stock", str(stock_alerte)),
            ("Valeur stock", f"{valeur_stock:.2f} €"),
            ("Commandes à traiter", str(commandes_actives)),
            ("Retards fournisseurs", str(retards_fournisseurs)),
            ("Taux de rotation", f"{self.calculate_rotation_rate():.2f}%")
        ]
        kpi_frame = tk.Frame(frame, bg="white", bd=1, relief=tk.GROOVE)
        kpi_frame.pack(fill=tk.X, padx=10, pady=10)
        for col, (metric, value) in enumerate(kpi_data):
            tk.Label(kpi_frame, text=f"{metric}:", font=("Arial", 12, "bold"), bg="white", fg="#1A3C5A").grid(row=0, column=col*2, padx=10, pady=5, sticky="e")
            tk.Label(kpi_frame, text=value, font=("Arial", 12), bg="white").grid(row=0, column=col*2+1, padx=10, pady=5, sticky="w")
        graph_frame = tk.Frame(frame, bg="white")
        graph_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Graph 1: Stock over time (Line Plot)
        fig1, ax1 = plt.subplots(figsize=(4, 3))
        if self.mouvements:
            sorted_mouvements = sorted(self.mouvements, key=lambda x: x['date'])
            dates = []
            stock_levels = []
            stock_dict = {a['ref']: a['stock'] for a in self.articles}
            earliest_date = datetime.date.fromisoformat(sorted_mouvements[0]['date'])
            dates.append(earliest_date)
            total_stock = sum(stock_dict.values())
            stock_levels.append(total_stock)
            current_date = earliest_date
            for m in sorted_mouvements:
                mvmt_date = datetime.date.fromisoformat(m['date'])
                while current_date < mvmt_date:
                    current_date += datetime.timedelta(days=1)
                    dates.append(current_date)
                    stock_levels.append(total_stock)
                article_ref = m['article']
                qte = m['qte']
                if m['type'] in ["Entrée", "Retour client"]:
                    stock_dict[article_ref] = stock_dict.get(article_ref, 0) + qte
                elif m['type'] in ["Sortie", "Retour fournisseur"]:
                    stock_dict[article_ref] = stock_dict.get(article_ref, 0) - qte
                total_stock = sum(stock_dict.values())
                dates.append(mvmt_date)
                stock_levels.append(total_stock)
                current_date = mvmt_date
            ax1.plot(dates, stock_levels, marker='o', color='#4A90E2', label='Stock total')
        else:
            # Default empty plot
            today = datetime.date.today()
            dates = [today - datetime.timedelta(days=x) for x in range(5)][::-1]
            stock_levels = [0] * 5
            ax1.plot(dates, stock_levels, marker='o', color='#4A90E2', label='Stock total')
        ax1.set_title("Quantité de stock au fil du temps", fontweight="bold", color="#1A3C5A")
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Quantité")
        ax1.grid(True)
        ax1.tick_params(axis='x', rotation=45)
        ax1.legend()
        fig1.tight_layout()
        canvas1 = FigureCanvasTkAgg(fig1, master=graph_frame)
        canvas1.draw()
        canvas1.get_tk_widget().pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)

        # Graph 2: Stock by category (Bar Plot)
        fig2, ax2 = plt.subplots(figsize=(4, 3))
        categories = list(set(a['categorie'] for a in self.articles)) if self.articles else self.categories
        stocks = [sum(a['stock'] for a in self.articles if a['categorie'] == c) for c in categories] if self.articles else [0] * len(categories)
        ax2.bar(categories, stocks, color='#4A90E2')
        ax2.set_title("Stock par catégorie", fontweight="bold", color="#1A3C5A")
        ax2.set_ylabel("Quantité")
        ax2.tick_params(axis='x', rotation=45)
        fig2.tight_layout()
        canvas2 = FigureCanvasTkAgg(fig2, master=graph_frame)
        canvas2.draw()
        canvas2.get_tk_widget().pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)

        # Graph 3: Stock distribution by depot (Bar Plot)
        fig3, ax3 = plt.subplots(figsize=(4, 3))
        depot_names = [d['nom'] for d in self.depots]
        depot_stocks = []
        for depot in depot_names:
            depot_stock = sum(m['qte'] for m in self.mouvements if m['depot'] == depot and m['type'] in ["Entrée", "Retour client"]) - \
                          sum(m['qte'] for m in self.mouvements if m['depot'] == depot and m['type'] in ["Sortie", "Retour fournisseur"])
            depot_stocks.append(max(0, depot_stock))
        if not depot_stocks:
            depot_stocks = [0] * len(depot_names)
        ax3.bar(depot_names, depot_stocks, color='#4A90E2')
        ax3.set_title("Stock par dépôt", fontweight="bold", color="#1A3C5A")
        ax3.set_ylabel("Quantité")
        ax3.tick_params(axis='x', rotation=45)
        fig3.tight_layout()
        canvas3 = FigureCanvasTkAgg(fig3, master=graph_frame)
        canvas3.draw()
        canvas3.get_tk_widget().pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)

    def calculate_rotation_rate(self):
        if not self.mouvements or not self.articles:
            return 0
        total_sorties = sum(m['qte'] for m in self.mouvements if m['type'] == 'Sortie')
        avg_stock = sum(a['stock'] for a in self.articles) / len(self.articles)
        return (total_sorties / avg_stock * 100) if avg_stock > 0 else 0

    def gestion_articles(self):
        self.clear_main()
        header_frame = tk.Frame(self.main_frame, bg="#F5F7FA")
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(header_frame, text="📦 Gestion des articles", font=("Arial", 16, "bold"), bg="#F5F7FA", fg="#1A3C5A").pack(anchor="w")
        form_frame = tk.Frame(self.main_frame, bg="white", bd=1, relief=tk.GROOVE)
        form_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(form_frame, text="Référence", bg="white", font=("Arial", 12, "bold"), fg="#1A3C5A").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        entry_ref = tk.Entry(form_frame, font=("Arial", 12), width=20)
        entry_ref.grid(row=0, column=1, padx=10, pady=5)
        tk.Label(form_frame, text="Nom", bg="white", font=("Arial", 12, "bold"), fg="#1A3C5A").grid(row=0, column=2, padx=10, pady=5, sticky="w")
        entry_nom = tk.Entry(form_frame, font=("Arial", 12), width=20)
        entry_nom.grid(row=0, column=3, padx=10, pady=5)
        tk.Label(form_frame, text="Description", bg="white", font=("Arial", 12, "bold"), fg="#1A3C5A").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        entry_desc = tk.Entry(form_frame, font=("Arial", 12), width=20)
        entry_desc.grid(row=1, column=1, padx=10, pady=5)
        tk.Label(form_frame, text="Catégorie", bg="white", font=("Arial", 12, "bold"), fg="#1A3C5A").grid(row=1, column=2, padx=10, pady=5, sticky="w")
        categorie_var = tk.StringVar(value=self.categories[0] if self.categories else "")
        categorie_combobox = ttk.Combobox(form_frame, textvariable=categorie_var, values=self.categories, width=18, font=("Arial", 12))
        categorie_combobox.grid(row=1, column=3, padx=10, pady=5)
        tk.Label(form_frame, text="Nouvelle catégorie", bg="white", font=("Arial", 12, "bold"), fg="#1A3C5A").grid(row=2, column=2, padx=10, pady=5, sticky="w")
        entry_new_categorie = tk.Entry(form_frame, font=("Arial", 12), width=20)
        entry_new_categorie.grid(row=2, column=3, padx=10, pady=5)
        ttk.Button(form_frame, text="➕ Ajouter Catégorie", command=lambda: ajouter_categorie(), style="Action.TButton").grid(row=3, column=3, padx=10, pady=5, sticky="w")
        tk.Label(form_frame, text="Prix (€)", bg="white", font=("Arial", 12, "bold"), fg="#1A3C5A").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        entry_prix = tk.Entry(form_frame, font=("Arial", 12), width=20)
        entry_prix.grid(row=4, column=1, padx=10, pady=5)
        tk.Label(form_frame, text="Stock", bg="white", font=("Arial", 12, "bold"), fg="#1A3C5A").grid(row=4, column=2, padx=10, pady=5, sticky="w")
        entry_stock = tk.Entry(form_frame, font=("Arial", 12), width=20)
        entry_stock.grid(row=4, column=3, padx=10, pady=5)
        tk.Label(form_frame, text="Seuil", bg="white", font=("Arial", 12, "bold"), fg="#1A3C5A").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        entry_seuil = tk.Entry(form_frame, font=("Arial", 12), width=20)
        entry_seuil.grid(row=5, column=1, padx=10, pady=5)
        form_button_frame = tk.Frame(form_frame, bg="white")
        form_button_frame.grid(row=6, column=0, columnspan=4, pady=10)
        style = ttk.Style()
        style.configure("Action.TButton", font=("Arial", 10, "bold"), padding=8)
        style.map("Action.TButton", background=[("active", "#3267D6")], foreground=[("active", "white")])
        ttk.Button(form_button_frame, text="➕ Ajouter", command=lambda: ajouter_article(), style="Action.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(form_button_frame, text="✏️ Modifier", command=lambda: modifier_article(), style="Action.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(form_button_frame, text="🧹 Vider", command=lambda: clear_form(), style="Action.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(form_button_frame, text="📋 Dupliquer", command=lambda: duplicate_article(), style="Action.TButton").pack(side=tk.LEFT, padx=5)
        selected_article = [None]
        filter_frame = tk.Frame(self.main_frame, bg="#F5F7FA")
        filter_frame.pack(fill=tk.X, padx=20, pady=5)
        filter_search_frame = tk.Frame(filter_frame, bg="#F5F7FA")
        filter_search_frame.pack(side=tk.LEFT)
        tk.Label(filter_search_frame, text="Filtrer par :", bg="#F5F7FA", font=("Arial", 12, "bold"), fg="#1A3C5A").pack(side=tk.LEFT, padx=5)
        filter_var = tk.StringVar(value="Tous")
        filter_menu = ttk.Combobox(filter_search_frame, textvariable=filter_var, values=["Tous", "Sous seuil", "Stock > 0"] + self.categories, width=15, font=("Arial", 12))
        filter_menu.pack(side=tk.LEFT, padx=5)
        tk.Label(filter_search_frame, text="Rechercher :", bg="#F5F7FA", font=("Arial", 12, "bold"), fg="#1A3C5A").pack(side=tk.LEFT, padx=5)
        search_var = tk.StringVar()
        search_entry = tk.Entry(filter_search_frame, textvariable=search_var, font=("Arial", 12), width=20)
        search_entry.pack(side=tk.LEFT, padx=5)
        action_button_frame = tk.Frame(filter_frame, bg="#F5F7FA")
        action_button_frame.pack(side=tk.RIGHT)
        ttk.Button(action_button_frame, text="🗑️ Supprimer", command=lambda: supprimer_article(), style="Action.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(action_button_frame, text="📥 Importer Excel", command=lambda: importer_excel(), style="Action.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(action_button_frame, text="📤 Exporter Excel", command=lambda: exporter_excel(), style="Action.TButton").pack(side=tk.LEFT, padx=5)
        tree_frame = tk.Frame(self.main_frame, bg="white", bd=1, relief=tk.GROOVE)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        canvas = tk.Canvas(tree_frame, bg="white")
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        sort_column = tk.StringVar(value="Référence")
        sort_reverse = tk.BooleanVar(value=False)

        def get_sort_key(article, column):
            value = article.get(column.lower(), "")
            try:
                return float(value)
            except (ValueError, TypeError):
                return str(value).lower()

        def sort_articles():
            try:
                column = sort_column.get()
                reverse = sort_reverse.get()
                self.articles.sort(key=lambda a: get_sort_key(a, column), reverse=reverse)
                sort_reverse.set(not reverse)
                display_articles(filter_var.get(), search_var.get())
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors du tri: {str(e)}")

        def ajouter_categorie():
            new_categorie = entry_new_categorie.get().strip()
            if not new_categorie:
                messagebox.showerror("Erreur", "Veuillez entrer un nom pour la catégorie.")
                return
            if new_categorie in self.categories:
                messagebox.showerror("Erreur", "Cette catégorie existe déjà.")
                return
            self.categories.append(new_categorie)
            categorie_combobox['values'] = self.categories
            filter_menu['values'] = ["Tous", "Sous seuil", "Stock > 0"] + self.categories
            categorie_var.set(new_categorie)
            entry_new_categorie.delete(0, tk.END)
            messagebox.showinfo("Ajout", f"Catégorie '{new_categorie}' ajoutée avec succès.")

        def display_articles(filter_type, search_query=""):
            for widget in scrollable_frame.winfo_children():
                widget.destroy()
            header_frame = tk.Frame(scrollable_frame, bg="#1A3C5A")
            header_frame.pack(fill=tk.X, pady=2)
            headers = ["Référence", "Nom", "Description", "Catégorie", "Prix (€)", "Stock", "Seuil", "Action"]
            for col, header in enumerate(headers):
                frame = tk.Frame(header_frame, bg="#1A3C5A")
                frame.grid(row=0, column=col, padx=2, pady=2)
                nick_name = header
                if nick_name == "Nom":
                    nick_name = "Nom_article"
                tk.Label(frame, text=header, font=("Arial", 12, "bold"), fg="white", bg="#1A3C5A", width=15).pack(side=tk.LEFT)
                if col < len(headers) - 1:
                    sort_btn = tk.Button(frame, text="⬆⬇", font=("Arial", 8), bg="#4A90E2", fg="white", bd=1,
                                         command=lambda h=nick_name: (sort_column.set(h), sort_articles()))
                    sort_btn.pack(side=tk.LEFT)
            filtered_articles = []
            search_query = search_query.lower()
            for a in self.articles:
                if not isinstance(a, dict) or "ref" not in a:
                    continue
                if filter_type == "Sous seuil" and a["stock"] >= a["seuil"]:
                    continue
                if filter_type == "Stock > 0" and a["stock"] <= 0:
                    continue
                if filter_type in self.categories and a["categorie"] != filter_type:
                    continue
                if search_query and not (search_query in a["ref"].lower() or search_query in a["nom"].lower()):
                    continue
                filtered_articles.append(a)
            for row, a in enumerate(filtered_articles, start=1):
                bg_color = "#ffffff" if row % 2 == 0 else "#f9f9f9"
                article_frame = tk.Frame(scrollable_frame, bg=bg_color, bd=1, relief=tk.SOLID)
                article_frame.pack(fill=tk.X, pady=2)
                tk.Label(article_frame, text=a["ref"], bg=bg_color, font=("Arial", 12), width=15).grid(row=0, column=0, padx=2, pady=2)
                tk.Label(article_frame, text=a["nom"], bg=bg_color, font=("Arial", 12), width=15).grid(row=0, column=1, padx=2, pady=2)
                tk.Label(article_frame, text=a["description"], bg=bg_color, font=("Arial", 12), width=15).grid(row=0, column=2, padx=2, pady=2)
                tk.Label(article_frame, text=a["categorie"], bg=bg_color, font=("Arial", 12), width=15).grid(row=0, column=3, padx=2, pady=2)
                tk.Label(article_frame, text=f"{a['prix']:.2f}", bg=bg_color, font=("Arial", 12), width=15).grid(row=0, column=4, padx=2, pady=2)
                tk.Label(article_frame, text=a["stock"], bg=bg_color, font=("Arial", 12), width=15).grid(row=0, column=5, padx=2, pady=2)
                tk.Label(article_frame, text=a["seuil"], bg=bg_color, font=("Arial", 12), width=15).grid(row=0, column=6, padx=2, pady=2)

                def select_article(article=a):
                    selected_article[0] = article
                    entry_ref.delete(0, tk.END)
                    entry_ref.insert(0, article["ref"])
                    entry_nom.delete(0, tk.END)
                    entry_nom.insert(0, article["nom"])
                    entry_desc.delete(0, tk.END)
                    entry_desc.insert(0, article["description"])
                    categorie_var.set(article["categorie"])
                    entry_prix.delete(0, tk.END)
                    entry_prix.insert(0, str(article["prix"]))
                    entry_stock.delete(0, tk.END)
                    entry_stock.insert(0, str(article["stock"]))
                    entry_seuil.delete(0, tk.END)
                    entry_seuil.insert(0, str(article["seuil"]))

                ttk.Button(article_frame, text="✅ Sélectionner", command=select_article, style="Action.TButton").grid(row=0, column=7, padx=2, pady=2)

        def ajouter_article():
            try:
                ref = entry_ref.get().strip()
                nom = entry_nom.get().strip()
                desc = entry_desc.get().strip()
                categorie = categorie_var.get()
                prix = float(entry_prix.get())
                stock = int(entry_stock.get())
                seuil = int(entry_seuil.get())
                if ref and nom and categorie and prix >= 0 and stock >= 0 and seuil >= 0:
                    article = {
                        "ref": ref, "nom": nom, "description": desc, "categorie": categorie,
                        "prix": prix, "stock": stock, "seuil": seuil
                    }
                    self.articles.append(article)
                    if categorie not in self.categories:
                        self.categories.append(categorie)
                        categorie_combobox['values'] = self.categories
                        filter_menu['values'] = ["Tous", "Sous seuil", "Stock > 0"] + self.categories
                    messagebox.showinfo("Ajout", "Article ajouté avec succès.")
                    self.gestion_articles()
                else:
                    messagebox.showerror("Erreur", "Veuillez remplir tous les champs correctement.")
            except ValueError:
                messagebox.showerror("Erreur", "Prix, stock et seuil doivent être des nombres valides.")

        def modifier_article():
            if not selected_article[0]:
                messagebox.showwarning("Avertissement", "Veuillez sélectionner un article à modifier.")
                return
            try:
                ref = entry_ref.get().strip()
                nom = entry_nom.get().strip()
                desc = entry_desc.get().strip()
                categorie = categorie_var.get()
                prix = float(entry_prix.get())
                stock = int(entry_stock.get())
                seuil = int(entry_seuil.get())
                if ref and nom and categorie and prix >= 0 and stock >= 0 and seuil >= 0:
                    for a in self.articles:
                        if a["ref"] == selected_article[0]["ref"]:
                            a.update({
                                "ref": ref, "nom": nom, "description": desc, "categorie": categorie,
                                "prix": prix, "stock": stock, "seuil": seuil
                            })
                            break
                    if categorie not in self.categories:
                        self.categories.append(categorie)
                        categorie_combobox['values'] = self.categories
                        filter_menu['values'] = ["Tous", "Sous seuil", "Stock > 0"] + self.categories
                    messagebox.showinfo("Modification", "Article modifié avec succès.")
                    self.gestion_articles()
                else:
                    messagebox.showerror("Erreur", "Veuillez remplir tous les champs correctement.")
            except ValueError:
                messagebox.showerror("Erreur", "Prix, stock et seuil doivent être des nombres valides.")

        def importer_excel():
            try:
                file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
                if not file_path:
                    return
                df = pd.read_excel(file_path)
                expected_columns = ["ref", "nom", "description", "categorie", "prix", "stock", "seuil"]
                if not all(col in df.columns for col in expected_columns):
                    messagebox.showerror("Erreur", "Le fichier Excel doit contenir les colonnes: ref, nom, description, categorie, prix, stock, seuil")
                    return
                imported_count = 0
                for _, row in df.iterrows():
                    try:
                        ref = str(row["ref"]).strip()
                        nom = str(row["nom"]).strip()
                        desc = str(row["description"]).strip() if pd.notna(row["description"]) else ""
                        categorie = str(row["categorie"]).strip()
                        prix = float(row["prix"])
                        stock = int(row["stock"])
                        seuil = int(row["seuil"])
                        if ref and nom and categorie and prix >= 0 and stock >= 0 and seuil >= 0:
                            if categorie not in self.categories:
                                self.categories.append(categorie)
                                categorie_combobox['values'] = self.categories
                                filter_menu['values'] = ["Tous", "Sous seuil", "Stock > 0"] + self.categories
                            self.articles.append({
                                "ref": ref, "nom": nom, "description": desc, "categorie": categorie,
                                "prix": prix, "stock": stock, "seuil": seuil
                            })
                            imported_count += 1
                    except (ValueError, TypeError):
                        continue
                self.gestion_articles()
                messagebox.showinfo("Importation", f"{imported_count} articles importés avec succès.")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'importation: {str(e)}")

        def exporter_excel():
            if not self.articles:
                messagebox.showwarning("Avertissement", "Aucun article à exporter.")
                return
            try:
                file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
                if not file_path:
                    return
                df = pd.DataFrame(self.articles)
                df.to_excel(file_path, index=False)
                messagebox.showinfo("Exportation", "Articles exportés avec succès.")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'exportation: {str(e)}")

        def clear_form():
            entry_ref.delete(0, tk.END)
            entry_nom.delete(0, tk.END)
            entry_desc.delete(0, tk.END)
            categorie_var.set(self.categories[0] if self.categories else "")
            entry_new_categorie.delete(0, tk.END)
            entry_prix.delete(0, tk.END)
            entry_stock.delete(0, tk.END)
            entry_seuil.delete(0, tk.END)
            selected_article[0] = None

        def duplicate_article():
            if not selected_article[0]:
                messagebox.showwarning("Avertissement", "Veuillez sélectionner un article à dupliquer.")
                return
            new_article = selected_article[0].copy()
            new_ref = f"{selected_article[0]['ref']}_COPY_{len(self.articles) + 1}"
            new_article["ref"] = new_ref
            self.articles.append(new_article)
            messagebox.showinfo("Duplication", "Article dupliqué avec succès.")
            self.gestion_articles()

        def supprimer_article():
            if not selected_article[0]:
                messagebox.showwarning("Avertissement", "Veuillez sélectionner un article à supprimer.")
                return
            self.articles = [a for a in self.articles if a["ref"] != selected_article[0]["ref"]]
            display_articles(filter_var.get(), search_var.get())
            messagebox.showinfo("Suppression", "Article supprimé.")
            clear_form()

        def on_filter_or_search_change(*args):
            display_articles(filter_var.get(), search_var.get())

        filter_var.trace("w", on_filter_or_search_change)
        search_var.trace("w", on_filter_or_search_change)
        display_articles("Tous", "")

    def suivi_stock(self):
        self.clear_main()
        header_frame = tk.Frame(self.main_frame, bg="#F5F7FA")
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(header_frame, text="📋 Suivi de stock", font=("Arial", 16, "bold"), bg="#F5F7FA", fg="#1A3C5A").pack(anchor="w")
        filter_frame = tk.Frame(self.main_frame, bg="#F5F7FA")
        filter_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(filter_frame, text="Filtrer par :", bg="#F5F7FA", font=("Arial", 12, "bold"), fg="#1A3C5A").pack(side=tk.LEFT, padx=5)
        filter_var = tk.StringVar(value="Tous")
        filter_menu = ttk.Combobox(filter_frame, textvariable=filter_var, values=["Tous", "Sous seuil", "Stock > 0"], font=("Arial", 12))
        filter_menu.pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="📜 Voir Historique", command=lambda: voir_historique(), style="Action.TButton").pack(side=tk.LEFT, padx=5)
        tree_frame = tk.Frame(self.main_frame, bg="white", bd=1, relief=tk.GROOVE)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        tree = ttk.Treeview(tree_frame, columns=("Ref", "Nom", "Stock", "Seuil", "Statut"), show="headings")
        tree.heading("Ref", text="Référence", command=lambda: self.sort_column(tree, "Ref", False))
        tree.heading("Nom", text="Nom", command=lambda: self.sort_column(tree, "Nom", False))
        tree.heading("Stock", text="Stock", command=lambda: self.sort_column(tree, "Stock", False))
        tree.heading("Seuil", text="Seuil", command=lambda: self.sort_column(tree, "Seuil", False))
        tree.heading("Statut", text="Statut", command=lambda: self.sort_column(tree, "Statut", False))
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        def voir_historique():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Avertissement", "Veuillez sélectionner un article pour voir l'historique.")
                return
            ref = tree.item(selected[0], "values")[0]
            self.show_historique_mouvements(ref)

        filter_menu.bind("<<ComboboxSelected>>", lambda e: self.update_stock_table(tree, filter_var.get()))
        self.update_stock_table(tree, "Tous")

    def show_historique_mouvements(self, ref):
        self.clear_main()
        header_frame = tk.Frame(self.main_frame, bg="#F5F7FA")
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(header_frame, text=f"📜 Historique des mouvements - {ref}", font=("Arial", 16, "bold"), bg="#F5F7FA", fg="#1A3C5A").pack(anchor="w")
        tree_frame = tk.Frame(self.main_frame, bg="white", bd=1, relief=tk.GROOVE)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        tree = ttk.Treeview(tree_frame, columns=("Article", "Type", "Quantité", "Dépôt", "Date"), show="headings")
        tree.heading("Article", text="Article", command=lambda: self.sort_column(tree, "Article", False))
        tree.heading("Type", text="Type", command=lambda: self.sort_column(tree, "Type", False))
        tree.heading("Quantité", text="Quantité", command=lambda: self.sort_column(tree, "Quantité", False))
        tree.heading("Dépôt", text="Dépôt", command=lambda: self.sort_column(tree, "Dépôt", False))
        tree.heading("Date", text="Date", command=lambda: self.sort_column(tree, "Date", False))
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        for m in self.mouvements:
            if m["article"] == ref:
                tree.insert("", tk.END, values=(m["article"], m["type"], m["qte"], m["depot"], m["date"]))
        ttk.Button(self.main_frame, text="⬅ Retour", command=self.suivi_stock, style="Action.TButton").pack(pady=10)

    def entrees_sorties(self):
        self.clear_main()
        header_frame = tk.Frame(self.main_frame, bg="#F5F7FA")
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(header_frame, text="🔄 Entrées et sorties", font=("Arial", 16, "bold"), bg="#F5F7FA", fg="#1A3C5A").pack(anchor="w")
        form_frame = tk.Frame(self.main_frame, bg="white", bd=1, relief=tk.GROOVE)
        form_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(form_frame, text="Article (Référence)", bg="white", font=("Arial", 12, "bold"), fg="#1A3C5A").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        entry_article = tk.Entry(form_frame, font=("Arial", 12), width=20)
        entry_article.grid(row=0, column=1, padx=10, pady=5)
        tk.Label(form_frame, text="Type", bg="white", font=("Arial", 12, "bold"), fg="#1A3C5A").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        mouvement_type = ttk.Combobox(form_frame, values=["Entrée", "Sortie", "Retour client", "Retour fournisseur"], font=("Arial", 12), width=18)
        mouvement_type.grid(row=1, column=1, padx=10, pady=5)
        tk.Label(form_frame, text="Quantité", bg="white", font=("Arial", 12, "bold"), fg="#1A3C5A").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        entry_qte = tk.Entry(form_frame, font=("Arial", 12), width=20)
        entry_qte.grid(row=2, column=1, padx=10, pady=5)
        tk.Label(form_frame, text="Dépôt", bg="white", font=("Arial", 12, "bold"), fg="#1A3C5A").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        depot_var = tk.StringVar(value=self.depots[0]["nom"] if self.depots else "")
        depot_combobox = ttk.Combobox(form_frame, textvariable=depot_var, values=[d["nom"] for d in self.depots], font=("Arial", 12), width=18)
        depot_combobox.grid(row=3, column=1, padx=10, pady=5)
        tk.Label(form_frame, text="Source/Destination", bg="white", font=("Arial", 12, "bold"), fg="#1A3C5A").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        entry_source = tk.Entry(form_frame, font=("Arial", 12), width=20)
        entry_source.grid(row=4, column=1, padx=10, pady=5)
        ttk.Button(form_frame, text="✔ Valider Mouvement", command=lambda: ajouter_mouvement(), style="Action.TButton").grid(row=5, column=0, columnspan=2, pady=10)
        transfer_frame = tk.Frame(self.main_frame, bg="white", bd=1, relief=tk.GROOVE)
        transfer_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(transfer_frame, text="Transférer vers Dépôt", bg="white", font=("Arial", 12, "bold"), fg="#1A3C5A").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        depot_dest_var = tk.StringVar(value=self.depots[0]["nom"] if self.depots else "")
        depot_dest_combobox = ttk.Combobox(transfer_frame, textvariable=depot_dest_var, values=[d["nom"] for d in self.depots], font=("Arial", 12), width=18)
        depot_dest_combobox.grid(row=0, column=1, padx=10, pady=5)
        ttk.Button(transfer_frame, text="🔄 Transférer", command=lambda: transferer_stock(), style="Action.TButton").grid(row=1, column=0, columnspan=2, pady=10)
        tree_frame = tk.Frame(self.main_frame, bg="white", bd=1, relief=tk.GROOVE)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        tree = ttk.Treeview(tree_frame, columns=("Article", "Type", "Quantité", "Dépôt", "Source", "Date"), show="headings")
        tree.heading("Article", text="Article", command=lambda: self.sort_column(tree, "Article", False))
        tree.heading("Type", text="Type", command=lambda: self.sort_column(tree, "Type", False))
        tree.heading("Quantité", text="Quantité", command=lambda: self.sort_column(tree, "Quantité", False))
        tree.heading("Dépôt", text="Dépôt", command=lambda: self.sort_column(tree, "Dépôt", False))
        tree.heading("Source", text="Source", command=lambda: self.sort_column(tree, "Source", False))
        tree.heading("Date", text="Date", command=lambda: self.sort_column(tree, "Date", False))
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        def ajouter_mouvement():
            try:
                article = entry_article.get().strip()
                type_mvmt = mouvement_type.get()
                qte = int(entry_qte.get())
                depot = depot_var.get()
                source = entry_source.get().strip()
                if not article or not type_mvmt or not depot or not source or qte <= 0:
                    messagebox.showerror("Erreur", "Veuillez remplir tous les champs correctement.")
                    return
                # Vérifier si l'article existe
                article_exists = any(a["ref"] == article for a in self.articles)
                if not article_exists:
                    messagebox.showerror("Erreur", "L'article spécifié n'existe pas.")
                    return
                # Vérifier si le stock est suffisant pour une sortie
                if type_mvmt in ["Sortie", "Retour fournisseur"]:
                    for a in self.articles:
                        if a["ref"] == article:
                            current_stock = a["stock"]
                            depot_stock = sum(m['qte'] for m in self.mouvements if m['depot'] == depot and m['article'] == article and m['type'] in ["Entrée", "Retour client"]) - \
                                          sum(m['qte'] for m in self.mouvements if m['depot'] == depot and m['article'] == article and m['type'] in ["Sortie", "Retour fournisseur"])
                            depot_stock = max(0, depot_stock)
                            if depot_stock < qte:
                                messagebox.showerror("Erreur", f"Stock insuffisant dans le dépôt {depot} pour effectuer cette sortie.")
                                return
                            break
                date = datetime.date.today().isoformat()
                mouvement = {
                    "article": article, "type": type_mvmt, "qte": qte, "depot": depot,
                    "source": source, "date": date
                }
                self.mouvements.append(mouvement)
                for a in self.articles:
                    if a["ref"] == article:
                        if type_mvmt in ["Entrée", "Retour client"]:
                            a["stock"] += qte
                        elif type_mvmt in ["Sortie", "Retour fournisseur"]:
                            a["stock"] -= qte
                            if a["stock"] < 0:
                                a["stock"] = 0
                        break
                messagebox.showinfo("Mouvement", "Mouvement enregistré.")
                self.entrees_sorties()
            except ValueError:
                messagebox.showerror("Erreur", "La quantité doit être un nombre valide.")

        def transferer_stock():
            try:
                article = entry_article.get().strip()
                qte = int(entry_qte.get())
                depot_source = depot_var.get()
                depot_dest = depot_dest_var.get()
                if not article or qte <= 0 or depot_source == depot_dest:
                    messagebox.showerror("Erreur", "Veuillez remplir tous les champs correctement et choisir des dépôts différents.")
                    return
                # Vérifier si l'article existe
                article_exists = any(a["ref"] == article for a in self.articles)
                if not article_exists:
                    messagebox.showerror("Erreur", "L'article spécifié n'existe pas.")
                    return
                # Vérifier si le stock est suffisant dans le dépôt source
                depot_stock = sum(m['qte'] for m in self.mouvements if m['depot'] == depot_source and m['article'] == article and m['type'] in ["Entrée", "Retour client"]) - \
                              sum(m['qte'] for m in self.mouvements if m['depot'] == depot_source and m['article'] == article and m['type'] in ["Sortie", "Retour fournisseur"])
                depot_stock = max(0, depot_stock)
                if depot_stock < qte:
                    messagebox.showerror("Erreur", f"Stock insuffisant dans le dépôt {depot_source} pour effectuer ce transfert.")
                    return
                date = datetime.date.today().isoformat()
                self.mouvements.append({
                    "article": article, "type": "Sortie", "qte": qte, "depot": depot_source,
                    "source": f"Transfert vers {depot_dest}", "date": date
                })
                self.mouvements.append({
                    "article": article, "type": "Entrée", "qte": qte, "depot": depot_dest,
                    "source": f"Transfert depuis {depot_source}", "date": date
                })
                messagebox.showinfo("Transfert", "Transfert effectué avec succès.")
                self.entrees_sorties()
            except ValueError:
                messagebox.showerror("Erreur", "La quantité doit être un nombre valide.")

        self.update_mouvements_table(tree)

    def gestion_contacts(self):
        self.clear_main()
        header_frame = tk.Frame(self.main_frame, bg="#F5F7FA")
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(header_frame, text="👥 Fournisseurs et clients", font=("Arial", 16, "bold"), bg="#F5F7FA", fg="#1A3C5A").pack(anchor="w")
        form_frame = tk.Frame(self.main_frame, bg="white", bd=1, relief=tk.GROOVE)
        form_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(form_frame, text="Nom", bg="white", font=("Arial", 12, "bold"), fg="#1A3C5A").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        entry_nom = tk.Entry(form_frame, font=("Arial", 12), width=20)
        entry_nom.grid(row=0, column=1, padx=10, pady=5)
        tk.Label(form_frame, text="Adresse", bg="white", font=("Arial", 12, "bold"), fg="#1A3C5A").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        entry_adresse = tk.Entry(form_frame, font=("Arial", 12), width=20)
        entry_adresse.grid(row=1, column=1, padx=10, pady=5)
        tk.Label(form_frame, text="Ville", bg="white", font=("Arial", 12, "bold"), fg="#1A3C5A").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        entry_ville = tk.Entry(form_frame, font=("Arial", 12), width=20)
        entry_ville.grid(row=2, column=1, padx=10, pady=5)
        tk.Label(form_frame, text="Code postal", bg="white", font=("Arial", 12, "bold"), fg="#1A3C5A").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        entry_code_postal = tk.Entry(form_frame, font=("Arial", 12), width=20)
        entry_code_postal.grid(row=3, column=1, padx=10, pady=5)
        tk.Label(form_frame, text="Pays", bg="white", font=("Arial", 12, "bold"), fg="#1A3C5A").grid(row=0, column=2, padx=10, pady=5, sticky="w")
        entry_pays = tk.Entry(form_frame, font=("Arial", 12), width=20)
        entry_pays.grid(row=0, column=3, padx=10, pady=5)
        tk.Label(form_frame, text="Email", bg="white", font=("Arial", 12, "bold"), fg="#1A3C5A").grid(row=1, column=2, padx=10, pady=5, sticky="w")
        entry_email = tk.Entry(form_frame, font=("Arial", 12), width=20)
        entry_email.grid(row=1, column=3, padx=10, pady=5)
        tk.Label(form_frame, text="Téléphone", bg="white", font=("Arial", 12, "bold"), fg="#1A3C5A").grid(row=2, column=2, padx=10, pady=5, sticky="w")
        entry_telephone = tk.Entry(form_frame, font=("Arial", 12), width=20)
        entry_telephone.grid(row=2, column=3, padx=10, pady=5)
        tk.Label(form_frame, text="Site web", bg="white", font=("Arial", 12, "bold"), fg="#1A3C5A").grid(row=3, column=2, padx=10, pady=5, sticky="w")
        entry_site_web = tk.Entry(form_frame, font=("Arial", 12), width=20)
        entry_site_web.grid(row=3, column=3, padx=10, pady=5)
        tk.Label(form_frame, text="Type", bg="white", font=("Arial", 12, "bold"), fg="#1A3C5A").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        contact_type = ttk.Combobox(form_frame, values=["Client", "Fournisseur"], font=("Arial", 12), width=18)
        contact_type.grid(row=4, column=1, padx=10, pady=5)
        ttk.Button(form_frame, text="➕ Ajouter", command=lambda: ajouter_contact(), style="Action.TButton").grid(row=5, column=0, columnspan=4, pady=10)
        filter_frame = tk.Frame(self.main_frame, bg="#F5F7FA")
        filter_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(filter_frame, text="Filtrer par :", bg="#F5F7FA", font=("Arial", 12, "bold"), fg="#1A3C5A").pack(side=tk.LEFT, padx=5)
        filter_var = tk.StringVar(value="Tous")
        filter_menu = ttk.Combobox(filter_frame, textvariable=filter_var, values=["Tous", "Client", "Fournisseur"], font=("Arial", 12))
        filter_menu.pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="🗑️ Supprimer", command=lambda: supprimer_contact(), style="Action.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="📜 Historique", command=lambda: voir_historique(), style="Action.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="📤 Exporter Factures", command=lambda: exporter_factures(), style="Action.TButton").pack(side=tk.LEFT, padx=5)
        tree_frame = tk.Frame(self.main_frame, bg="white", bd=1, relief=tk.GROOVE)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        canvas = tk.Canvas(tree_frame, bg="white")
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=canvas.xview)
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        tree = ttk.Treeview(scrollable_frame, columns=("Nom", "Type", "Adresse", "Ville", "Code postal", "Pays", "Email", "Téléphone", "Site web"), show="headings")
        tree.heading("Nom", text="Nom", command=lambda: self.sort_column(tree, "Nom", False))
        tree.heading("Type", text="Type", command=lambda: self.sort_column(tree, "Type", False))
        tree.heading("Adresse", text="Adresse", command=lambda: self.sort_column(tree, "Adresse", False))
        tree.heading("Ville", text="Ville", command=lambda: self.sort_column(tree, "Ville", False))
        tree.heading("Code postal", text="Code postal", command=lambda: self.sort_column(tree, "Code postal", False))
        tree.heading("Pays", text="Pays", command=lambda: self.sort_column(tree, "Pays", False))
        tree.heading("Email", text="Email", command=lambda: self.sort_column(tree, "Email", False))
        tree.heading("Téléphone", text="Téléphone", command=lambda: self.sort_column(tree, "Téléphone", False))
        tree.heading("Site web", text="Site web", command=lambda: self.sort_column(tree, "Site web", False))
        tree.column("Nom", width=150)
        tree.column("Type", width=100)
        tree.column("Adresse", width=200)
        tree.column("Ville", width=120)
        tree.column("Code postal", width=100)
        tree.column("Pays", width=120)
        tree.column("Email", width=200)
        tree.column("Téléphone", width=150)
        tree.column("Site web", width=200)
        tree.pack(fill=tk.BOTH, expand=True)
        selected_contact = [None]

        def on_select(event):
            selected_items = tree.selection()
            if selected_items:
                item = selected_items[0]
                values = tree.item(item, "values")
                selected_contact[0] = {
                    "nom": values[0],
                    "type": values[1],
                    "adresse": values[2],
                    "ville": values[3],
                    "code_postal": values[4],
                    "pays": values[5],
                    "email": values[6],
                    "telephone": values[7],
                    "site_web": values[8]
                }
                entry_nom.delete(0, tk.END)
                entry_nom.insert(0, values[0])
                entry_adresse.delete(0, tk.END)
                entry_adresse.insert(0, values[2])
                entry_ville.delete(0, tk.END)
                entry_ville.insert(0, values[3])
                entry_code_postal.delete(0, tk.END)
                entry_code_postal.insert(0, values[4])
                entry_pays.delete(0, tk.END)
                entry_pays.insert(0, values[5])
                entry_email.delete(0, tk.END)
                entry_email.insert(0, values[6])
                entry_telephone.delete(0, tk.END)
                entry_telephone.insert(0, values[7])
                entry_site_web.delete(0, tk.END)
                entry_site_web.insert(0, values[8])
                contact_type.set(values[1])
            else:
                selected_contact[0] = None
                clear_form()

        tree.bind('<<TreeviewSelect>>', on_select)

        def ajouter_contact():
            nom = entry_nom.get().strip()
            adresse = entry_adresse.get().strip()
            ville = entry_ville.get().strip()
            code_postal = entry_code_postal.get().strip()
            pays = entry_pays.get().strip()
            email = entry_email.get().strip()
            telephone = entry_telephone.get().strip()
            site_web = entry_site_web.get().strip()
            type_contact = contact_type.get()
            if not nom or not type_contact:
                messagebox.showerror("Erreur", "Veuillez entrer un nom et un type pour le contact.")
                return
            if any(c["nom"] == nom for c in self.clients + self.fournisseurs):
                messagebox.showerror("Erreur", "Ce nom de contact existe déjà.")
                return
            contact_data = {
                "nom": nom,
                "adresse": adresse,
                "ville": ville,
                "code_postal": code_postal,
                "pays": pays,
                "email": email,
                "telephone": telephone,
                "site_web": site_web
            }
            if type_contact == "Client":
                self.clients.append(contact_data)
            else:
                self.fournisseurs.append(contact_data)
            messagebox.showinfo("Ajout", f"{type_contact} ajouté avec succès.")
            clear_form()
            self.update_contacts_table(tree, filter_var.get())

        def clear_form():
            entry_nom.delete(0, tk.END)
            entry_adresse.delete(0, tk.END)
            entry_ville.delete(0, tk.END)
            entry_code_postal.delete(0, tk.END)
            entry_pays.delete(0, tk.END)
            entry_email.delete(0, tk.END)
            entry_telephone.delete(0, tk.END)
            entry_site_web.delete(0, tk.END)
            contact_type.set("")
            selected_contact[0] = None

        def voir_historique():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Avertissement", "Veuillez sélectionner un contact pour voir l'historique.")
                return
            nom = tree.item(selected[0], "values")[0]
            type_contact = tree.item(selected[0], "values")[1]
            self.show_historique_commandes(nom, type_contact)

        def supprimer_contact():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Avertissement", "Veuillez sélectionner un contact à supprimer.")
                return
            for item in selected:
                nom = tree.item(item, "values")[0]
                type_contact = tree.item(item, "values")[1]
                if type_contact == "Client":
                    self.clients = [c for c in self.clients if c["nom"] != nom]
                else:
                    self.fournisseurs = [f for f in self.fournisseurs if f["nom"] != nom]
            self.update_contacts_table(tree, filter_var.get())
            messagebox.showinfo("Suppression", "Contact(s) supprimé(s).")
            clear_form()

        def exporter_factures():
            try:
                # Determine which invoices to export
                invoices = []
                if selected_contact[0]:
                    nom = selected_contact[0]["nom"]
                    type_contact = selected_contact[0]["type"]
                    invoices = [c for c in self.commandes if c["contact"] == nom and c["type"] == type_contact]
                else:
                    invoices = self.commandes

                if not invoices:
                    messagebox.showwarning("Avertissement", "Aucune facture à exporter.")
                    return

                # Prepare invoice data with price information
                invoice_data = []
                for c in invoices:
                    article_ref = c["article"]
                    # Find article price
                    article = next((a for a in self.articles if a["ref"] == article_ref), None)
                    prix_unitaire = article["prix"] if article else 0.0
                    prix_total = prix_unitaire * c["qte"]
                    invoice_data.append({
                        "Contact": c["contact"],
                        "Type": c["type"],
                        "Article": c["article"],
                        "Quantité": c["qte"],
                        "Prix Unitaire (€)": prix_unitaire,
                        "Prix Total (€)": prix_total,
                        "Statut": c["statut"],
                        "Date": c["date"]
                    })

                # Save to Excel
                file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
                if not file_path:
                    return
                df = pd.DataFrame(invoice_data)
                df.to_excel(file_path, index=False)
                messagebox.showinfo("Exportation", "Factures exportées avec succès.")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'exportation des factures: {str(e)}")

        filter_menu.bind("<<ComboboxSelected>>", lambda e: self.update_contacts_table(tree, filter_var.get()))
        self.update_contacts_table(tree, "Tous")

    def show_historique_commandes(self, nom, type_contact):
        self.clear_main()
        header_frame = tk.Frame(self.main_frame, bg="#F5F7FA")
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(header_frame, text=f"📜 Historique des commandes - {nom}", font=("Arial", 16, "bold"), bg="#F5F7FA", fg="#1A3C5A").pack(anchor="w")
        tree_frame = tk.Frame(self.main_frame, bg="white", bd=1, relief=tk.GROOVE)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        tree = ttk.Treeview(tree_frame, columns=("Contact", "Type", "Article", "Quantité", "Statut", "Date"), show="headings")
        tree_frame = tk.Frame(self.main_frame, bg="white", bd=1, relief=tk.GROOVE)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        tree = ttk.Treeview(tree_frame, columns=("Contact", "Type", "Article", "Quantité", "Statut", "Date"), show="headings")
        tree.heading("Contact", text="Contact", command=lambda: self.sort_column(tree, "Contact", False))
        tree.heading("Type", text="Type", command=lambda: self.sort_column(tree, "Type", False))
        tree.heading("Article", text="Article", command=lambda: self.sort_column(tree, "Article", False))
        tree.heading("Quantité", text="Quantité", command=lambda: self.sort_column(tree, "Quantité", False))
        tree.heading("Statut", text="Statut", command=lambda: self.sort_column(tree, "Statut", False))
        tree.heading("Date", text="Date", command=lambda: self.sort_column(tree, "Date", False))
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for c in self.commandes:
            if c["contact"] == nom and c["type"] == type_contact:
                tree.insert("", tk.END, values=(c["contact"], c["type"], c["article"], c["qte"], c["statut"], c["date"]))
        
        ttk.Button(self.main_frame, text="⬅ Retour", command=self.gestion_contacts, style="Action.TButton").pack(pady=10)

    def sort_column(self, tree, col, reverse):
        try:
            items = [(tree.set(item, col), item) for item in tree.get_children()]
            # Try to convert values to float for numerical sorting, otherwise sort as strings
            items.sort(key=lambda x: float(x[0]) if x[0].replace('.', '', 1).lstrip('-').isdigit() else x[0].lower(), reverse=reverse)
            for index, (val, item) in enumerate(items):
                tree.move(item, "", index)
            tree.heading(col, command=lambda: self.sort_column(tree, col, not reverse))
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du tri: {str(e)}")

    def update_stock_table(self, tree, filter_type):
        for item in tree.get_children():
            tree.delete(item)
        for a in self.articles:
            if not isinstance(a, dict) or "ref" not in a:
                continue
            if filter_type == "Sous seuil" and a["stock"] >= a["seuil"]:
                continue
            if filter_type == "Stock > 0" and a["stock"] <= 0:
                continue
            statut = "Critique" if a["stock"] < a["seuil"] else "Normal"
            tree.insert("", tk.END, values=(a["ref"], a["nom"], a["stock"], a["seuil"], statut))

    def update_mouvements_table(self, tree):
        for item in tree.get_children():
            tree.delete(item)
        for m in self.mouvements:
            tree.insert("", tk.END, values=(m["article"], m["type"], m["qte"], m["depot"], m["source"], m["date"]))

    def update_contacts_table(self, tree, filter_type):
        for item in tree.get_children():
            tree.delete(item)
        contacts = []
        if filter_type in ["Tous", "Client"]:
            contacts.extend([c | {"type": "Client"} for c in self.clients])
        if filter_type in ["Tous", "Fournisseur"]:
            contacts.extend([f | {"type": "Fournisseur"} for f in self.fournisseurs])
        for c in contacts:
            tree.insert("", tk.END, values=(
                c["nom"], c["type"], c["adresse"], c["ville"], c["code_postal"],
                c["pays"], c["email"], c["telephone"], c["site_web"]
            ))

if __name__ == "__main__":
    root = tk.Tk()
    app = FlexilogApp(root)
    root.mainloop()