class LoginInfo:
    def __init__(self):
        self.contacts = {}

    def getUserId(self, teamId):
        return self.contacts[teamId].userId

    def setContacts(self, contacts):
        self.contacts = contacts
        return self.contacts
