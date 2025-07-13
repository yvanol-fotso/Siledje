# Dummy version 1

# dummy_stock_data = [
#     # Papeterie
#     [1, "Cahier de liaison 96 pages", "Papeterie", 150, 2.5, "CB1001", "carton", "Fournisseur A", "contact@fournisseura.com", "2024-01-15", "Cahier de 96 pages, grand format.", "Étagère 1A", "", "", ""],
#     [2, "Cahier TP 300 pages A4", "Papeterie", 5, 15.0, "CB1004", "carton", "Fournisseur A", "contact@fournisseura.com", "2024-03-10", "Pack de 5 cartons de cahiers TP A4.", "Réserve Zone B", "", "", ""],
#     [3, "Ramette Format A4 80g", "Papeterie", 100, 4.0, "CB1011", "lot", "Fournisseur G", "contact@fournisseurg.com", "2024-05-01", "Ramette de 500 feuilles A4, 80g.", "Réserve Zone A", "", "", ""],
#     [4, "Manifold 50 Duplicata", "Papeterie", 70, 3.5, "CB1012", "unité", "Fournisseur H", "info@fournisseurh.org", "2024-04-20", "Manifold autocopiant 50 feuillets.", "Comptoir C", "", "", ""],
#     [5, "Registre de présence grand modèle", "Papeterie", 20, 10.0, "CB1013", "pièce", "Fournisseur A", "contact@fournisseura.com", "2024-06-01", "Registre relié pour la présence.", "Bureau Admin", "", "", ""],
#
#     # Fournitures
#     [6, "Stylo bille bleu", "Fournitures", 200, 1.2, "CB1002", "unité", "Fournisseur B", "info@fournisseurb.net", "2024-02-01", "Stylo à bille bleu, pointe moyenne.", "Tiroir 2C", "", "", ""],
#     [7, "Règle 30cm transparente", "Fournitures", 80, 1.8, "CB1003", "unité", "Fournisseur C", "sales@fournisseurc.com", "2024-01-20", "Règle en plastique transparent.", "Boîte 3D", "", "", ""],
#     [8, "Trousse scolaire motifs variés", "Fournitures", 60, 5.0, "CB1005", "pièce", "Fournisseur D", "support@fournisseurd.org", "2024-03-15", "Trousse en tissu, motifs variés.", "Présentoir 4B", "", "", ""],
#     [9, "Biro noir pointe fine", "Fournitures", 120, 1.0, "CB1007", "unité", "Fournisseur B", "info@fournisseurb.net", "2024-02-20", "Stylo à bille noir, pointe fine.", "Tiroir 2C", "", "", ""],
#     [10, "Gomme blanche non abrasive", "Fournitures", 90, 0.5, "CB1008", "pièce", "Fournisseur C", "sales@fournisseurc.com", "2024-03-01", "Gomme douce, non abrasive.", "Boîte 3D", "", "", ""],
#     [11, "Crayon à papier HB avec gomme", "Fournitures", 180, 0.7, "CB1009", "unité", "Fournisseur B", "info@fournisseurb.net", "2024-03-25", "Crayon graphite HB, avec gomme intégrée.", "Tiroir 2C", "", "", ""],
#
#     # Manuels - Maternelle (Française)
#     [12, "Maths Petite Section 1", "Manuels", 30, 25.0, "CB1201", "unité", "Fournisseur E", "livres@fournisseure.fr", "2024-01-05", "Manuel de maths Petite Section 1.", "Section Manuels", "Maternelle", "Française", "Petite Section"],
#     [13, "Français Petite Section 2", "Manuels", 30, 25.0, "CB1202", "unité", "Fournisseur E", "livres@fournisseure.fr", "2024-01-06", "Manuel de français Petite Section 2.", "Section Manuels", "Maternelle", "Française", "Petite Section"],
#     [14, "Sciences Petite Section 3", "Manuels", 30, 25.0, "CB1203", "unité", "Fournisseur E", "livres@fournisseure.fr", "2024-01-07", "Manuel de sciences Petite Section 3.", "Section Manuels", "Maternelle", "Française", "Petite Section"],
#     [15, "Art Petite Section 4", "Manuels", 30, 25.0, "CB1204", "unité", "Fournisseur E", "livres@fournisseure.fr", "2024-01-08", "Manuel d'art Petite Section 4.", "Section Manuels", "Maternelle", "Française", "Petite Section"],
#     [16, "Maths Moyenne Section 1", "Manuels", 28, 26.0, "CB1301", "unité", "Fournisseur E", "livres@fournisseure.fr", "2024-01-09", "Manuel de maths Moyenne Section 1.", "Section Manuels", "Maternelle", "Française", "Moyenne Section"],
#     [17, "Français Moyenne Section 2", "Manuels", 28, 26.0, "CB1302", "unité", "Fournisseur E", "livres@fournisseure.fr", "2024-01-10", "Manuel de français Moyenne Section 2.", "Section Manuels", "Maternelle", "Française", "Moyenne Section"],
#     [18, "Sciences Moyenne Section 3", "Manuels", 28, 26.0, "CB1303", "unité", "Fournisseur E", "livres@fournisseure.fr", "2024-01-11", "Manuel de sciences Moyenne Section 3.", "Section Manuels", "Maternelle", "Française", "Moyenne Section"],
#     [19, "Art Moyenne Section 4", "Manuels", 28, 26.0, "CB1304", "unité", "Fournisseur E", "livres@fournisseure.fr", "2024-01-12", "Manuel d'art Moyenne Section 4.", "Section Manuels", "Maternelle", "Française", "Moyenne Section"],
#     [20, "Maths Grande Section 1", "Manuels", 28, 26.0, "CB1401", "unité", "Fournisseur E", "livres@fournisseure.fr", "2024-01-13", "Manuel de maths Grande Section 1.", "Section Manuels", "Maternelle", "Française", "Grande Section"],
#     [21, "Français Grande Section 2", "Manuels", 28, 26.0, "CB1402", "unité", "Fournisseur E", "livres@fournisseure.fr", "2024-01-14", "Manuel de français Grande Section 2.", "Section Manuels", "Maternelle", "Française", "Grande Section"],
#     [22, "Sciences Grande Section 3", "Manuels", 28, 26.0, "CB1403", "unité", "Fournisseur E", "livres@fournisseure.fr", "2024-01-15", "Manuel de sciences Grande Section 3.", "Section Manuels", "Maternelle", "Française", "Grande Section"],
#     [23, "Art Grande Section 4", "Manuels", 28, 26.0, "CB1404", "unité", "Fournisseur E", "livres@fournisseure.fr", "2024-01-16", "Manuel d'art Grande Section 4.", "Section Manuels", "Maternelle", "Française", "Grande Section"],
#
#     # Manuels - Maternelle (Anglophone)
#     [24, "Maths Nursery 1", "Manuels", 30, 25.0, "CB1501", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-01-17", "Maths textbook Nursery 1.", "Section Manuels", "Maternelle", "Anglophone", "Nursery 1"],
#     [25, "English Nursery 1", "Manuels", 30, 25.0, "CB1502", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-01-18", "English textbook Nursery 1.", "Section Manuels", "Maternelle", "Anglophone", "Nursery 1"],
#     [26, "Science Nursery 1", "Manuels", 30, 25.0, "CB1503", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-01-19", "Science textbook Nursery 1.", "Section Manuels", "Maternelle", "Anglophone", "Nursery 1"],
#     [27, "Art Nursery 1", "Manuels", 30, 25.0, "CB1504", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-01-20", "Art textbook Nursery 1.", "Section Manuels", "Maternelle", "Anglophone", "Nursery 1"],
#     [28, "Maths Nursery 2", "Manuels", 28, 26.0, "CB1601", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-01-21", "Maths textbook Nursery 2.", "Section Manuels", "Maternelle", "Anglophone", "Nursery 2"],
#     [29, "English Nursery 2", "Manuels", 28, 26.0, "CB1602", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-01-22", "English textbook Nursery 2.", "Section Manuels", "Maternelle", "Anglophone", "Nursery 2"],
#     [30, "Science Nursery 2", "Manuels", 28, 26.0, "CB1603", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-01-23", "Science textbook Nursery 2.", "Section Manuels", "Maternelle", "Anglophone", "Nursery 2"],
#     [31, "Art Nursery 2", "Manuels", 28, 26.0, "CB1604", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-01-24", "Art textbook Nursery 2.", "Section Manuels", "Maternelle", "Anglophone", "Nursery 2"],
#
#     # Manuels - Primaire (Française)
#     [32, "Maths CP 1", "Manuels", 50, 21.0, "CB1701", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-01-25", "Maths textbook CP 1.", "Section Manuels", "Primaire", "Française", "CP"],
#     [33, "Français CP 2", "Manuels", 50, 21.0, "CB1702", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-01-26", "Français textbook CP 2.", "Section Manuels", "Primaire", "Française", "CP"],
#     [34, "Sciences CP 3", "Manuels", 50, 21.0, "CB1703", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-01-27", "Sciences textbook CP 3.", "Section Manuels", "Primaire", "Française", "CP"],
#     [35, "Art CP 4", "Manuels", 50, 21.0, "CB1704", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-01-28", "Art textbook CP 4.", "Section Manuels", "Primaire", "Française", "CP"],
#     [36, "Maths CE1 1", "Manuels", 45, 22.0, "CB1801", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-01-29", "Maths textbook CE1 1.", "Section Manuels", "Primaire", "Française", "CE1"],
#     [37, "Français CE1 2", "Manuels", 45, 22.0, "CB1802", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-01-30", "Français textbook CE1 2.", "Section Manuels", "Primaire", "Française", "CE1"],
#     [38, "Sciences CE1 3", "Manuels", 45, 22.0, "CB1803", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-01-31", "Sciences textbook CE1 3.", "Section Manuels", "Primaire", "Française", "CE1"],
#     [39, "Art CE1 4", "Manuels", 45, 22.0, "CB1804", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-02-01", "Art textbook CE1 4.", "Section Manuels", "Primaire", "Française", "CE1"],
#     [40, "Maths CM2 1", "Manuels", 40, 20.0, "CB1901", "unité", "Fournisseur E", "livres@fournisseure.fr", "2024-02-02", "Maths textbook CM2 1.", "Section Manuels", "Primaire", "Française", "CM2"],
#     [41, "Français CM2 2", "Manuels", 40, 20.0, "CB1902", "unité", "Fournisseur E", "livres@fournisseure.fr", "2024-02-03", "Français textbook CM2 2.", "Section Manuels", "Primaire", "Française", "CM2"],
#     [42, "Sciences CM2 3", "Manuels", 40, 20.0, "CB1903", "unité", "Fournisseur E", "livres@fournisseure.fr", "2024-02-04", "Sciences textbook CM2 3.", "Section Manuels", "Primaire", "Française", "CM2"],
#     [43, "Art CM2 4", "Manuels", 40, 20.0, "CB1904", "unité", "Fournisseur E", "livres@fournisseure.fr", "2024-02-05", "Art textbook CM2 4.", "Section Manuels", "Primaire", "Française", "CM2"],
#
#     # Manuels - Primaire (Anglophone)
#     [44, "Maths Grade 1 1", "Manuels", 50, 21.0, "CB2001", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-02-06", "Maths textbook Grade 1 1.", "Section Manuels", "Primaire", "Anglophone", "Grade 1"],
#     [45, "English Grade 1 2", "Manuels", 50, 21.0, "CB2002", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-02-07", "English textbook Grade 1 2.", "Section Manuels", "Primaire", "Anglophone", "Grade 1"],
#     [46, "Science Grade 1 3", "Manuels", 50, 21.0, "CB2003", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-02-08", "Science textbook Grade 1 3.", "Section Manuels", "Primaire", "Anglophone", "Grade 1"],
#     [47, "Art Grade 1 4", "Manuels", 50, 21.0, "CB2004", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-02-09", "Art textbook Grade 1 4.", "Section Manuels", "Primaire", "Anglophone", "Grade 1"],
#     [48, "Maths Grade 2 1", "Manuels", 45, 22.0, "CB2101", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-02-10", "Maths textbook Grade 2 1.", "Section Manuels", "Primaire", "Anglophone", "Grade 2"],
#     [49, "English Grade 2 2", "Manuels", 45, 22.0, "CB2102", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-02-11", "English textbook Grade 2 2.", "Section Manuels", "Primaire", "Anglophone", "Grade 2"],
#     [50, "Science Grade 2 3", "Manuels", 45, 22.0, "CB2103", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-02-12", "Science textbook Grade 2 3.", "Section Manuels", "Primaire", "Anglophone", "Grade 2"],
#     [51, "Art Grade 2 4", "Manuels", 45, 22.0, "CB2104", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-02-13", "Art textbook Grade 2 4.", "Section Manuels", "Primaire", "Anglophone", "Grade 2"],
#     [52, "Maths Grade 3 1", "Manuels", 40, 20.0, "CB2201", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-02-14", "Maths textbook Grade 3 1.", "Section Manuels", "Primaire", "Anglophone", "Grade 3"],
#     [53, "English Grade 3 2", "Manuels", 40, 20.0, "CB2202", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-02-15", "English textbook Grade 3 2.", "Section Manuels", "Primaire", "Anglophone", "Grade 3"],
#     [54, "Science Grade 3 3", "Manuels", 40, 20.0, "CB2203", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-02-16", "Science textbook Grade 3 3.", "Section Manuels", "Primaire", "Anglophone", "Grade 3"],
#     [55, "Art Grade 3 4", "Manuels", 40, 20.0, "CB2204", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-02-17", "Art textbook Grade 3 4.", "Section Manuels", "Primaire", "Anglophone", "Grade 3"],
#
#     # Manuels - Secondaire (Française)
#     [56, "Maths 6ème 1", "Manuels", 25, 28.0, "CB2301", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-02-18", "Maths textbook 6ème 1.", "Section Manuels", "Secondaire", "Française", "6ème"],
#     [57, "Français 6ème 2", "Manuels", 25, 28.0, "CB2302", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-02-19", "Français textbook 6ème 2.", "Section Manuels", "Secondaire", "Française", "6ème"],
#     [58, "Sciences 6ème 3", "Manuels", 25, 28.0, "CB2303", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-02-20", "Sciences textbook 6ème 3.", "Section Manuels", "Secondaire", "Française", "6ème"],
#     [59, "Art 6ème 4", "Manuels", 25, 28.0, "CB2304", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-02-21", "Art textbook 6ème 4.", "Section Manuels", "Secondaire", "Française", "6ème"],
#     [60, "Maths 3ème 1", "Manuels", 18, 30.0, "CB2401", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-02-22", "Maths textbook 3ème 1.", "Section Manuels", "Secondaire", "Française", "3ème"],
#     [61, "Français 3ème 2", "Manuels", 18, 30.0, "CB2402", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-02-23", "Français textbook 3ème 2.", "Section Manuels", "Secondaire", "Française", "3ème"],
#     [62, "Sciences 3ème 3", "Manuels", 18, 30.0, "CB2403", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-02-24", "Sciences textbook 3ème 3.", "Section Manuels", "Secondaire", "Française", "3ème"],
#     [63, "Art 3ème 4", "Manuels", 18, 30.0, "CB2404", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-02-25", "Art textbook 3ème 4.", "Section Manuels", "Secondaire", "Française", "3ème"],
#
#     # Manuels - Secondaire (Anglophone)
#     [64, "Maths Grade 6 1", "Manuels", 25, 28.0, "CB2501", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-02-26", "Maths textbook Grade 6 1.", "Section Manuels", "Secondaire", "Anglophone", "Grade 6"],
#     [65, "English Grade 6 2", "Manuels", 25, 28.0, "CB2502", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-02-27", "English textbook Grade 6 2.", "Section Manuels", "Secondaire", "Anglophone", "Grade 6"],
#     [66, "Science Grade 6 3", "Manuels", 25, 28.0, "CB2503", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-02-28", "Science textbook Grade 6 3.", "Section Manuels", "Secondaire", "Anglophone", "Grade 6"],
#     [67, "Art Grade 6 4", "Manuels", 25, 28.0, "CB2504", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-03-01", "Art textbook Grade 6 4.", "Section Manuels", "Secondaire", "Anglophone", "Grade 6"],
#     [68, "Maths Grade 9 1", "Manuels", 18, 30.0, "CB2601", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-03-02", "Maths textbook Grade 9 1.", "Section Manuels", "Secondaire", "Anglophone", "Grade 9"],
#     [69, "English Grade 9 2", "Manuels", 18, 30.0, "CB2602", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-03-03", "English textbook Grade 9 2.", "Section Manuels", "Secondaire", "Anglophone", "Grade 9"],
#     [70, "Science Grade 9 3", "Manuels", 18, 30.0, "CB2603", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-03-04", "Science textbook Grade 9 3.", "Section Manuels", "Secondaire", "Anglophone", "Grade 9"],
#     [71, "Art Grade 9 4", "Manuels", 18, 30.0, "CB2604", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-03-05", "Art textbook Grade 9 4.", "Section Manuels", "Secondaire", "Anglophone", "Grade 9"],
#
#     # Art & Loisirs
#     [72, "Peinture acrylique (Bleu)", "Art & Loisirs", 20, 8.0, "CB1020", "unité", "Fournisseur F", "art@fournisseurf.com", "2024-04-01", "Tube de peinture acrylique couleur bleu.", "Rayon Art", "", "", ""],
#     [73, "Crayons de couleur (Set de 12)", "Art & Loisirs", 40, 6.5, "CB1021", "pièce", "Fournisseur F", "art@fournisseurf.com", "2024-04-10", "Set de 12 crayons de couleur.", "Rayon Art", "", "", ""],
# ]
#
# stock_headers = [
#     "ID", "Nom", "Catégorie", "Quantité", "Prix", "Code-barres",
#     "Type d'emballage", "Fournisseur", "Contact Fournisseur", "Date d'ajout",
#     "Description", "Emplacement", "Niveau", "Langue", "Classe"
# ]



# Dummy version 2
stock_headers = [
    "ID", "Nom", "Catégorie", "Quantité", "Prix", "Code-barres",
    "Type d'emballage", "Fournisseur", "Contact Fournisseur", "Date d'ajout",
    "Description", "Emplacement", "Niveau", "Langue", "Classe"
]

dummy_stock_data = [
    # Papeterie (inchangé)
    [1, "Cahier de liaison 96 pages", "Papeterie", 150, 2.5, "CB1001", "carton", "Fournisseur A", "contact@fournisseura.com", "2024-01-15", "Cahier de 96 pages, grand format.", "Étagère 1A", "", "", ""],
    [2, "Cahier TP 300 pages A4", "Papeterie", 5, 15.0, "CB1004", "carton", "Fournisseur A", "contact@fournisseura.com", "2024-03-10", "Pack de 5 cartons de cahiers TP A4.", "Réserve Zone B", "", "", ""],
    [3, "Ramette Format A4 80g", "Papeterie", 100, 4.0, "CB1011", "lot", "Fournisseur G", "contact@fournisseurg.com", "2024-05-01", "Ramette de 500 feuilles A4, 80g.", "Réserve Zone A", "", "", ""],
    [4, "Manifold 50 Duplicata", "Papeterie", 70, 3.5, "CB1012", "unité", "Fournisseur H", "info@fournisseurh.org", "2024-04-20", "Manifold autocopiant 50 feuillets.", "Comptoir C", "", "", ""],
    [5, "Registre de présence grand modèle", "Papeterie", 20, 10.0, "CB1013", "pièce", "Fournisseur A", "contact@fournisseura.com", "2024-06-01", "Registre relié pour la présence.", "Bureau Admin", "", "", ""],

    # Fournitures (inchangé)
    [6, "Stylo bille bleu", "Fournitures", 200, 1.2, "CB1002", "unité", "Fournisseur B", "info@fournisseurb.net", "2024-02-01", "Stylo à bille bleu, pointe moyenne.", "Tiroir 2C", "", "", ""],
    [7, "Règle 30cm transparente", "Fournitures", 80, 1.8, "CB1003", "unité", "Fournisseur C", "sales@fournisseurc.com", "2024-01-20", "Règle en plastique transparent.", "Boîte 3D", "", "", ""],
    [8, "Trousse scolaire motifs variés", "Fournitures", 60, 5.0, "CB1005", "pièce", "Fournisseur D", "support@fournisseurd.org", "2024-03-15", "Trousse en tissu, motifs variés.", "Présentoir 4B", "", "", ""],
    [9, "Biro noir pointe fine", "Fournitures", 120, 1.0, "CB1007", "unité", "Fournisseur B", "info@fournisseurb.net", "2024-02-20", "Stylo à bille noir, pointe fine.", "Tiroir 2C", "", "", ""],
    [10, "Gomme blanche non abrasive", "Fournitures", 90, 0.5, "CB1008", "pièce", "Fournisseur C", "sales@fournisseurc.com", "2024-03-01", "Gomme douce, non abrasive.", "Boîte 3D", "", "", ""],
    [11, "Crayon à papier HB avec gomme", "Fournitures", 180, 0.7, "CB1009", "unité", "Fournisseur B", "info@fournisseurb.net", "2024-03-25", "Crayon graphite HB, avec gomme intégrée.", "Tiroir 2C", "", "", ""],

    # Manuels - Maternelle (Française)
    [12, "Maths Petite Section 1", "Manuels", 30, 25.0, "CB1201", "unité", "Fournisseur E", "livres@fournisseure.fr", "2024-01-05", "Manuel de maths Petite Section 1.", "Section Manuels", "Maternelle", "Française", "Petite Section"],
    [13, "Français Petite Section 2", "Manuels", 30, 25.0, "CB1202", "unité", "Fournisseur E", "livres@fournisseure.fr", "2024-01-06", "Manuel de français Petite Section 2.", "Section Manuels", "Maternelle", "Française", "Petite Section"],
    [14, "Sciences Petite Section 3", "Manuels", 30, 25.0, "CB1203", "unité", "Fournisseur E", "livres@fournisseure.fr", "2024-01-07", "Manuel de sciences Petite Section 3.", "Section Manuels", "Maternelle", "Française", "Petite Section"],
    [15, "Art Petite Section 4", "Manuels", 30, 25.0, "CB1204", "unité", "Fournisseur E", "livres@fournisseure.fr", "2024-01-08", "Manuel d'art Petite Section 4.", "Section Manuels", "Maternelle", "Française", "Petite Section"],
    [16, "Maths Moyenne Section 1", "Manuels", 28, 26.0, "CB1301", "unité", "Fournisseur E", "livres@fournisseure.fr", "2024-01-09", "Manuel de maths Moyenne Section 1.", "Section Manuels", "Maternelle", "Française", "Moyenne Section"],
    [17, "Français Moyenne Section 2", "Manuels", 28, 26.0, "CB1302", "unité", "Fournisseur E", "livres@fournisseure.fr", "2024-01-10", "Manuel de français Moyenne Section 2.", "Section Manuels", "Maternelle", "Française", "Moyenne Section"],
    [18, "Sciences Moyenne Section 3", "Manuels", 28, 26.0, "CB1303", "unité", "Fournisseur E", "livres@fournisseure.fr", "2024-01-11", "Manuel de sciences Moyenne Section 3.", "Section Manuels", "Maternelle", "Française", "Moyenne Section"],
    [19, "Art Moyenne Section 4", "Manuels", 28, 26.0, "CB1304", "unité", "Fournisseur E", "livres@fournisseure.fr", "2024-01-12", "Manuel d'art Moyenne Section 4.", "Section Manuels", "Maternelle", "Française", "Moyenne Section"],
    [20, "Maths Grande Section 1", "Manuels", 28, 26.0, "CB1401", "unité", "Fournisseur E", "livres@fournisseure.fr", "2024-01-13", "Manuel de maths Grande Section 1.", "Section Manuels", "Maternelle", "Française", "Grande Section"],
    [21, "Français Grande Section 2", "Manuels", 28, 26.0, "CB1402", "unité", "Fournisseur E", "livres@fournisseure.fr", "2024-01-14", "Manuel de français Grande Section 2.", "Section Manuels", "Maternelle", "Française", "Grande Section"],
    [22, "Sciences Grande Section 3", "Manuels", 28, 26.0, "CB1403", "unité", "Fournisseur E", "livres@fournisseure.fr", "2024-01-15", "Manuel de sciences Grande Section 3.", "Section Manuels", "Maternelle", "Française", "Grande Section"],
    [23, "Art Grande Section 4", "Manuels", 28, 26.0, "CB1404", "unité", "Fournisseur E", "livres@fournisseure.fr", "2024-01-16", "Manuel d'art Grande Section 4.", "Section Manuels", "Maternelle", "Française", "Grande Section"],

    # Manuels - Maternelle (Anglophone)
    [24, "Maths Nursery 1", "Manuels", 30, 25.0, "CB1501", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-01-17", "Maths textbook Nursery 1.", "Section Manuels", "Maternelle", "Anglophone", "Nursery 1"],
    [25, "English Nursery 1", "Manuels", 30, 25.0, "CB1502", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-01-18", "English textbook Nursery 1.", "Section Manuels", "Maternelle", "Anglophone", "Nursery 1"],
    [26, "Science Nursery 1", "Manuels", 30, 25.0, "CB1503", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-01-19", "Science textbook Nursery 1.", "Section Manuels", "Maternelle", "Anglophone", "Nursery 1"],
    [27, "Art Nursery 1", "Manuels", 30, 25.0, "CB1504", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-01-20", "Art textbook Nursery 1.", "Section Manuels", "Maternelle", "Anglophone", "Nursery 1"],
    [28, "Maths Nursery 2", "Manuels", 28, 26.0, "CB1601", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-01-21", "Maths textbook Nursery 2.", "Section Manuels", "Maternelle", "Anglophone", "Nursery 2"],
    [29, "English Nursery 2", "Manuels", 28, 26.0, "CB1602", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-01-22", "English textbook Nursery 2.", "Section Manuels", "Maternelle", "Anglophone", "Nursery 2"],
    [30, "Science Nursery 2", "Manuels", 28, 26.0, "CB1603", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-01-23", "Science textbook Nursery 2.", "Section Manuels", "Maternelle", "Anglophone", "Nursery 2"],
    [31, "Art Nursery 2", "Manuels", 28, 26.0, "CB1604", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-01-24", "Art textbook Nursery 2.", "Section Manuels", "Maternelle", "Anglophone", "Nursery 2"],

    # Manuels - Primaire (Française)
    [32, "Maths CP 1", "Manuels", 50, 21.0, "CB1701", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-01-25", "Maths textbook CP 1.", "Section Manuels", "Primaire", "Française", "CP"],
    [33, "Français CP 2", "Manuels", 50, 21.0, "CB1702", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-01-26", "Français textbook CP 2.", "Section Manuels", "Primaire", "Française", "CP"],
    [34, "Sciences CP 3", "Manuels", 50, 21.0, "CB1703", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-01-27", "Sciences textbook CP 3.", "Section Manuels", "Primaire", "Française", "CP"],
    [35, "Art CP 4", "Manuels", 50, 21.0, "CB1704", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-01-28", "Art textbook CP 4.", "Section Manuels", "Primaire", "Française", "CP"],
    [36, "Maths CE1 1", "Manuels", 45, 22.0, "CB1801", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-01-29", "Maths textbook CE1 1.", "Section Manuels", "Primaire", "Française", "CE1"],
    [37, "Français CE1 2", "Manuels", 45, 22.0, "CB1802", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-01-30", "Français textbook CE1 2.", "Section Manuels", "Primaire", "Française", "CE1"],
    [38, "Sciences CE1 3", "Manuels", 45, 22.0, "CB1803", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-01-31", "Sciences textbook CE1 3.", "Section Manuels", "Primaire", "Française", "CE1"],
    [39, "Art CE1 4", "Manuels", 45, 22.0, "CB1804", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-02-01", "Art textbook CE1 4.", "Section Manuels", "Primaire", "Française", "CE1"],
    [40, "Maths CM2 1", "Manuels", 40, 20.0, "CB1901", "unité", "Fournisseur E", "livres@fournisseure.fr", "2024-02-02", "Maths textbook CM2 1.", "Section Manuels", "Primaire", "Française", "CM2"],
    [41, "Français CM2 2", "Manuels", 40, 20.0, "CB1902", "unité", "Fournisseur E", "livres@fournisseure.fr", "2024-02-03", "Français textbook CM2 2.", "Section Manuels", "Primaire", "Française", "CM2"],
    [42, "Sciences CM2 3", "Manuels", 40, 20.0, "CB1903", "unité", "Fournisseur E", "livres@fournisseure.fr", "2024-02-04", "Sciences textbook CM2 3.", "Section Manuels", "Primaire", "Française", "CM2"],
    [43, "Art CM2 4", "Manuels", 40, 20.0, "CB1904", "unité", "Fournisseur E", "livres@fournisseure.fr", "2024-02-05", "Art textbook CM2 4.", "Section Manuels", "Primaire", "Française", "CM2"],
    # Ajout pour CE2
    [74, "Maths CE2 1", "Manuels", 45, 22.0, "CB2701", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-03-06", "Maths textbook CE2 1.", "Section Manuels", "Primaire", "Française", "CE2"],
    [75, "Français CE2 2", "Manuels", 45, 22.0, "CB2702", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-03-07", "Français textbook CE2 2.", "Section Manuels", "Primaire", "Française", "CE2"],
    [76, "Sciences CE2 3", "Manuels", 45, 22.0, "CB2703", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-03-08", "Sciences textbook CE2 3.", "Section Manuels", "Primaire", "Française", "CE2"],
    [77, "Art CE2 4", "Manuels", 45, 22.0, "CB2704", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-03-09", "Art textbook CE2 4.", "Section Manuels", "Primaire", "Française", "CE2"],
    # Ajout pour CM1
    [78, "Maths CM1 1", "Manuels", 40, 20.0, "CB2801", "unité", "Fournisseur E", "livres@fournisseure.fr", "2024-03-10", "Maths textbook CM1 1.", "Section Manuels", "Primaire", "Française", "CM1"],
    [79, "Français CM1 2", "Manuels", 40, 20.0, "CB2802", "unité", "Fournisseur E", "livres@fournisseure.fr", "2024-03-11", "Français textbook CM1 2.", "Section Manuels", "Primaire", "Française", "CM1"],
    [80, "Sciences CM1 3", "Manuels", 40, 20.0, "CB2803", "unité", "Fournisseur E", "livres@fournisseure.fr", "2024-03-12", "Sciences textbook CM1 3.", "Section Manuels", "Primaire", "Française", "CM1"],
    [81, "Art CM1 4", "Manuels", 40, 20.0, "CB2804", "unité", "Fournisseur E", "livres@fournisseure.fr", "2024-03-13", "Art textbook CM1 4.", "Section Manuels", "Primaire", "Française", "CM1"],

    # Manuels - Primaire (Anglophone, renommé de Grade à Class)
    [44, "Maths Class 1 1", "Manuels", 50, 21.0, "CB2001", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-02-06", "Maths textbook Class 1 1.", "Section Manuels", "Primaire", "Anglophone", "Class 1"],
    [45, "English Class 1 2", "Manuels", 50, 21.0, "CB2002", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-02-07", "English textbook Class 1 2.", "Section Manuels", "Primaire", "Anglophone", "Class 1"],
    [46, "Science Class 1 3", "Manuels", 50, 21.0, "CB2003", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-02-08", "Science textbook Class 1 3.", "Section Manuels", "Primaire", "Anglophone", "Class 1"],
    [47, "Art Class 1 4", "Manuels", 50, 21.0, "CB2004", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-02-09", "Art textbook Class 1 4.", "Section Manuels", "Primaire", "Anglophone", "Class 1"],
    [48, "Maths Class 2 1", "Manuels", 45, 22.0, "CB2101", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-02-10", "Maths textbook Class 2 1.", "Section Manuels", "Primaire", "Anglophone", "Class 2"],
    [49, "English Class 2 2", "Manuels", 45, 22.0, "CB2102", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-02-11", "English textbook Class 2 2.", "Section Manuels", "Primaire", "Anglophone", "Class 2"],
    [50, "Science Class 2 3", "Manuels", 45, 22.0, "CB2103", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-02-12", "Science textbook Class 2 3.", "Section Manuels", "Primaire", "Anglophone", "Class 2"],
    [51, "Art Class 2 4", "Manuels", 45, 22.0, "CB2104", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-02-13", "Art textbook Class 2 4.", "Section Manuels", "Primaire", "Anglophone", "Class 2"],
    [52, "Maths Class 3 1", "Manuels", 40, 20.0, "CB2201", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-02-14", "Maths textbook Class 3 1.", "Section Manuels", "Primaire", "Anglophone", "Class 3"],
    [53, "English Class 3 2", "Manuels", 40, 20.0, "CB2202", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-02-15", "English textbook Class 3 2.", "Section Manuels", "Primaire", "Anglophone", "Class 3"],
    [54, "Science Class 3 3", "Manuels", 40, 20.0, "CB2203", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-02-16", "Science textbook Class 3 3.", "Section Manuels", "Primaire", "Anglophone", "Class 3"],
    [55, "Art Class 3 4", "Manuels", 40, 20.0, "CB2204", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-02-17", "Art textbook Class 3 4.", "Section Manuels", "Primaire", "Anglophone", "Class 3"],
    # Ajout pour Class 4
    [82, "Maths Class 4 1", "Manuels", 40, 20.0, "CB2901", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-03-14", "Maths textbook Class 4 1.", "Section Manuels", "Primaire", "Anglophone", "Class 4"],
    [83, "English Class 4 2", "Manuels", 40, 20.0, "CB2902", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-03-15", "English textbook Class 4 2.", "Section Manuels", "Primaire", "Anglophone", "Class 4"],
    [84, "Science Class 4 3", "Manuels", 40, 20.0, "CB2903", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-03-16", "Science textbook Class 4 3.", "Section Manuels", "Primaire", "Anglophone", "Class 4"],
    [85, "Art Class 4 4", "Manuels", 40, 20.0, "CB2904", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-03-17", "Art textbook Class 4 4.", "Section Manuels", "Primaire", "Anglophone", "Class 4"],
    # Ajout pour Class 5
    [86, "Maths Class 5 1", "Manuels", 40, 20.0, "CB3001", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-03-18", "Maths textbook Class 5 1.", "Section Manuels", "Primaire", "Anglophone", "Class 5"],
    [87, "English Class 5 2", "Manuels", 40, 20.0, "CB3002", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-03-19", "English textbook Class 5 2.", "Section Manuels", "Primaire", "Anglophone", "Class 5"],
    [88, "Science Class 5 3", "Manuels", 40, 20.0, "CB3003", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-03-20", "Science textbook Class 5 3.", "Section Manuels", "Primaire", "Anglophone", "Class 5"],
    [89, "Art Class 5 4", "Manuels", 40, 20.0, "CB3004", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-03-21", "Art textbook Class 5 4.", "Section Manuels", "Primaire", "Anglophone", "Class 5"],
    # Ajout pour Class 6
    [90, "Maths Class 6 1", "Manuels", 40, 20.0, "CB3101", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-03-22", "Maths textbook Class 6 1.", "Section Manuels", "Primaire", "Anglophone", "Class 6"],
    [91, "English Class 6 2", "Manuels", 40, 20.0, "CB3102", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-03-23", "English textbook Class 6 2.", "Section Manuels", "Primaire", "Anglophone", "Class 6"],
    [92, "Science Class 6 3", "Manuels", 40, 20.0, "CB3103", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-03-24", "Science textbook Class 6 3.", "Section Manuels", "Primaire", "Anglophone", "Class 6"],
    [93, "Art Class 6 4", "Manuels", 40, 20.0, "CB3104", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-03-25", "Art textbook Class 6 4.", "Section Manuels", "Primaire", "Anglophone", "Class 6"],

    # Manuels - Secondaire (Française)
    [56, "Maths 6ème 1", "Manuels", 25, 28.0, "CB2301", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-02-18", "Maths textbook 6ème 1.", "Section Manuels", "Secondaire", "Française", "6ème"],
    [57, "Français 6ème 2", "Manuels", 25, 28.0, "CB2302", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-02-19", "Français textbook 6ème 2.", "Section Manuels", "Secondaire", "Française", "6ème"],
    [58, "Sciences 6ème 3", "Manuels", 25, 28.0, "CB2303", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-02-20", "Sciences textbook 6ème 3.", "Section Manuels", "Secondaire", "Française", "6ème"],
    [59, "Art 6ème 4", "Manuels", 25, 28.0, "CB2304", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-02-21", "Art textbook 6ème 4.", "Section Manuels", "Secondaire", "Française", "6ème"],
    [60, "Maths 3ème 1", "Manuels", 18, 30.0, "CB2401", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-02-22", "Maths textbook 3ème 1.", "Section Manuels", "Secondaire", "Française", "3ème"],
    [61, "Français 3ème 2", "Manuels", 18, 30.0, "CB2402", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-02-23", "Français textbook 3ème 2.", "Section Manuels", "Secondaire", "Française", "3ème"],
    [62, "Sciences 3ème 3", "Manuels", 18, 30.0, "CB2403", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-02-24", "Sciences textbook 3ème 3.", "Section Manuels", "Secondaire", "Française", "3ème"],
    [63, "Art 3ème 4", "Manuels", 18, 30.0, "CB2404", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-02-25", "Art textbook 3ème 4.", "Section Manuels", "Secondaire", "Française", "3ème"],
    # Ajout pour 5ème
    [94, "Maths 5ème 1", "Manuels", 22, 29.0, "CB3201", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-03-26", "Maths textbook 5ème 1.", "Section Manuels", "Secondaire", "Française", "5ème"],
    [95, "Français 5ème 2", "Manuels", 22, 29.0, "CB3202", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-03-27", "Français textbook 5ème 2.", "Section Manuels", "Secondaire", "Française", "5ème"],
    [96, "Sciences 5ème 3", "Manuels", 22, 29.0, "CB3203", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-03-28", "Sciences textbook 5ème 3.", "Section Manuels", "Secondaire", "Française", "5ème"],
    [97, "Art 5ème 4", "Manuels", 22, 29.0, "CB3204", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-03-29", "Art textbook 5ème 4.", "Section Manuels", "Secondaire", "Française", "5ème"],
    # Ajout pour 4ème
    [98, "Maths 4ème 1", "Manuels", 20, 29.5, "CB3301", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-03-30", "Maths textbook 4ème 1.", "Section Manuels", "Secondaire", "Française", "4ème"],
    [99, "Français 4ème 2", "Manuels", 20, 29.5, "CB3302", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-03-31", "Français textbook 4ème 2.", "Section Manuels", "Secondaire", "Française", "4ème"],
    [100, "Sciences 4ème 3", "Manuels", 20, 29.5, "CB3303", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-04-01", "Sciences textbook 4ème 3.", "Section Manuels", "Secondaire", "Française", "4ème"],
    [101, "Art 4ème 4", "Manuels", 20, 29.5, "CB3304", "unité", "Fournisseur I", "contact@fournisseuri.com", "2024-04-02", "Art textbook 4ème 4.", "Section Manuels", "Secondaire", "Française", "4ème"],

    # Manuels - Secondaire (Anglophone, renommé de Grade à Form)
    [64, "Maths Form 1 1", "Manuels", 25, 28.0, "CB2501", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-02-26", "Maths textbook Form 1 1.", "Section Manuels", "Secondaire", "Anglophone", "Form 1"],
    [65, "English Form 1 2", "Manuels", 25, 28.0, "CB2502", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-02-27", "English textbook Form 1 2.", "Section Manuels", "Secondaire", "Anglophone", "Form 1"],
    [66, "Science Form 1 3", "Manuels", 25, 28.0, "CB2503", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-02-28", "Science textbook Form 1 3.", "Section Manuels", "Secondaire", "Anglophone", "Form 1"],
    [67, "Art Form 1 4", "Manuels", 25, 28.0, "CB2504", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-03-01", "Art textbook Form 1 4.", "Section Manuels", "Secondaire", "Anglophone", "Form 1"],
    # Ajout pour Form 2
    [102, "Maths Form 2 1", "Manuels", 22, 29.0, "CB3401", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-04-03", "Maths textbook Form 2 1.", "Section Manuels", "Secondaire", "Anglophone", "Form 2"],
    [103, "English Form 2 2", "Manuels", 22, 29.0, "CB3402", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-04-04", "English textbook Form 2 2.", "Section Manuels", "Secondaire", "Anglophone", "Form 2"],
    [104, "Science Form 2 3", "Manuels", 22, 29.0, "CB3403", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-04-05", "Science textbook Form 2 3.", "Section Manuels", "Secondaire", "Anglophone", "Form 2"],
    [105, "Art Form 2 4", "Manuels", 22, 29.0, "CB3404", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-04-06", "Art textbook Form 2 4.", "Section Manuels", "Secondaire", "Anglophone", "Form 2"],
    # Ajout pour Form 3
    [106, "Maths Form 3 1", "Manuels", 20, 29.5, "CB3501", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-04-07", "Maths textbook Form 3 1.", "Section Manuels", "Secondaire", "Anglophone", "Form 3"],
    [107, "English Form 3 2", "Manuels", 20, 29.5, "CB3502", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-04-08", "English textbook Form 3 2.", "Section Manuels", "Secondaire", "Anglophone", "Form 3"],
    [108, "Science Form 3 3", "Manuels", 20, 29.5, "CB3503", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-04-09", "Science textbook Form 3 3.", "Section Manuels", "Secondaire", "Anglophone", "Form 3"],
    [109, "Art Form 3 4", "Manuels", 20, 29.5, "CB3504", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-04-10", "Art textbook Form 3 4.", "Section Manuels", "Secondaire", "Anglophone", "Form 3"],
    [68, "Maths Form 4 1", "Manuels", 18, 30.0, "CB2601", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-03-02", "Maths textbook Form 4 1.", "Section Manuels", "Secondaire", "Anglophone", "Form 4"],
    [69, "English Form 4 2", "Manuels", 18, 30.0, "CB2602", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-03-03", "English textbook Form 4 2.", "Section Manuels", "Secondaire", "Anglophone", "Form 4"],
    [70, "Science Form 4 3", "Manuels", 18, 30.0, "CB2603", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-03-04", "Science textbook Form 4 3.", "Section Manuels", "Secondaire", "Anglophone", "Form 4"],
    [71, "Art Form 4 4", "Manuels", 18, 30.0, "CB2604", "unité", "Fournisseur J", "support@fournisseurj.co", "2024-03-05", "Art textbook Form 4 4.", "Section Manuels", "Secondaire", "Anglophone", "Form 4"],

    # Art & Loisirs (inchangé)
    [72, "Peinture acrylique (Bleu)", "Art & Loisirs", 20, 8.0, "CB1020", "unité", "Fournisseur F", "art@fournisseurf.com", "2024-04-01", "Tube de peinture acrylique couleur bleu.", "Rayon Art", "", "", ""],
    [73, "Crayons de couleur (Set de 12)", "Art & Loisirs", 40, 6.5, "CB1021", "pièce", "Fournisseur F", "art@fournisseurf.com", "2024-04-10", "Set de 12 crayons de couleur.", "Rayon Art", "", "", ""],
]

