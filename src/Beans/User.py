class User:
    def __init__(self, name, role="utilisateur"):
        self.name = name
        self.role = role

    def is_admin(self):
        return self.role.lower() == "admin"
