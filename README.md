# 📚 Gestion Librairie & Papeterie 📝

Un système de gestion intuitif et complet pour les librairies et papeteries, conçu pour simplifier la gestion quotidienne des stocks, des ventes, des clients et des fournisseurs. Développé avec une interface utilisateur moderne et réactive grâce à **PySide** et **PyQt5**.

---

## ✨ Fonctionnalités

* **Gestion des Stocks :** Ajout, modification, suppression et recherche de livres et d'articles de papeterie. Suivi des quantités, des prix et des emplacements.
* **Transactions de Vente :** Enregistrement rapide des ventes, calcul automatique des totaux, gestion des retours et des remboursements.
* **Gestion des Clients :** Suivi détaillé des informations clients, de leur historique d'achats et de leurs préférences.
* **Gestion des Fournisseurs :** Enregistrement des détails des fournisseurs, suivi des commandes d'approvisionnement et des livraisons.
* **Rapports et Statistiques :** Génération de rapports sur les ventes, l'inventaire, les clients et les performances générales de l'entreprise.
* **Interface Utilisateur Graphique (GUI) :** Basée sur **PySide/PyQt5** pour une expérience utilisateur fluide, ergonomique et visuellement agréable.
* **Support QR Code :** Potentielle intégration pour la gestion des articles via **QR codes** (génération et/ou lecture).

---

## 🛠 Technologies Utilisées

* **Python 3.x**
* **PySide6 / PyQt5** (pour l'interface graphique)
* **SQLAlchemy** (ou autre ORM/bibliothèque de base de données pour l'interaction avec la base de données, par exemple SQLite pour le développement, ou PostgreSQL/MySQL pour la production).
* **Qt Designer** (pour la conception de l'interface utilisateur).
* **qrcode** (pour la génération de codes QR).
* **Pillow** (nécessaire pour la manipulation d'images, souvent une dépendance de `qrcode`).
* *(Optionnel) **opencv-python** : Si vous prévoyez d'intégrer une fonctionnalité de scan de QR codes via webcam.*

---

## 🚀 Installation et Lancement

Pour faire fonctionner l'application, suivez ces étapes :

1.  **Cloner le dépôt :**
    ```bash
    git clone [https://github.com/votre_utilisateur/librairie_papeterie.git](https://github.com/votre_utilisateur/librairie_papeterie.git)
    cd librairie_papeterie
    ```

2.  **Créer un environnement virtuel (fortement recommandé) :**
    Cela isole les dépendances de votre projet du reste de votre système Python, évitant ainsi les conflits.
    ```bash
    python -m venv venv
    # Sur Windows
    .\venv\Scripts\activate
    # Sur macOS/Linux
    source venv/bin/activate
    ```

3.  **Installer les dépendances :**
    Toutes les bibliothèques nécessaires au projet sont listées dans le fichier `requirements.txt`. Assurez-vous que ce fichier existe à la racine de votre projet et qu'il contient toutes les dépendances (ex: `PySide6`, `SQLAlchemy`, `qrcode`, `Pillow`, etc.). Installez-les en une seule commande :
    ```bash
    pip install -r requirements.txt
    ```

4.  **Lancer l'application :**
    ```bash
    python main.py # Ou le nom de votre fichier de démarrage principal (par exemple, app.py)
    ```

---

## 💻 Configuration de l'Environnement de Développement (PyCharm)

Pour garantir un développement fluide et éviter les conflits de dépendances, il est recommandé d'ouvrir le projet dans PyCharm et de le configurer pour utiliser l'environnement virtuel (venv) créé précédemment.

1.  **Ouvrir le projet dans PyCharm :**
    Lancez PyCharm, cliquez sur "**Open**", puis sélectionnez le dossier racine du projet (`librairie_papeterie`).

2.  **Configurer l'interpréteur Python sur l'environnement virtuel :**
    * Accédez à : `File > Settings > Project: librairie_papeterie > Python Interpreter` (ou `PyCharm > Preferences > Project: librairie_papeterie > Python Interpreter` sur macOS).
    * Cliquez sur l'icône de la **roue dentée ⚙️** (en haut à droite de la section interpréteur) > "**Add...**"
    * Choisissez "**Existing environment**".
    * Indiquez le **chemin** vers votre environnement virtuel. Ce chemin pointe vers l'exécutable Python dans votre `venv` :
        * **Windows** : `.\venv\Scripts\python.exe`
        * **macOS/Linux** : `./venv/bin/python`
    * Cliquez sur **OK** pour valider.

3.  **Installer les dépendances automatiquement (si nécessaire) :**
    PyCharm devrait détecter automatiquement le fichier `requirements.txt` et vous proposer d'installer les dépendances manquantes. Si ce n'est pas le cas, ouvrez le terminal intégré de PyCharm (en bas de l'écran) et exécutez la commande suivante :
    ```bash
    pip install -r requirements.txt
    ```

4.  **Lancer l'application depuis PyCharm :**
    Dans la fenêtre de PyCharm, naviguez dans la structure du projet, faites un clic droit sur `main.py` (ou le fichier Python principal de démarrage de votre application), puis sélectionnez "**Run 'main'**".

✅ **Votre environnement est maintenant configuré proprement pour contribuer efficacement au projet !**

---

## 💡 Comment Contribuer

Nous accueillons avec plaisir les contributions ! Si vous souhaitez améliorer ce projet, veuillez suivre ces étapes :

1.  Faites un "fork" de ce dépôt sur votre compte GitHub.
2.  Créez une nouvelle branche pour votre fonctionnalité ou correction de bug :
    ```bash
    git checkout -b feature/nom-de-votre-fonctionnalite
    # ou
    git checkout -b bugfix/description-du-bug
    ```
3.  Commitez vos changements en écrivant des messages clairs et concis :
    ```bash
    git commit -m 'feat: Ajout de la fonctionnalité X'
    # ou
    git commit -m 'fix: Correction du bug Y'
    ```
4.  Poussez vos modifications vers votre dépôt forké :
    ```bash
    git push origin feature/nom-de-votre-fonctionnalite
    ```
5.  Ouvrez une "Pull Request" depuis votre dépôt forké vers le dépôt principal, décrivant en détail vos modifications et pourquoi elles sont utiles.

---


## Documentation et ressources

Vous trouverez ci-dessous des documents et captures d’écran illustrant les différentes versions de l’interface utilisateur ainsi que la documentation PDF associée.

### Documentation PDF

- [Documentation version 1 (PDF)](docs/docs_pdf/Librairie_Papetierie-V1.pdf)

### Captures d’écran de l’interface

#### Interface version 1  
![Accueil v1](docs/images/v1/ui_accueil.png)

---

## 📄 Licence

Ce projet est distribué sous la licence [**MIT License**]. Veuillez consulter le fichier `LICENSE` à la racine du dépôt pour plus de détails sur les conditions d'utilisation.

---