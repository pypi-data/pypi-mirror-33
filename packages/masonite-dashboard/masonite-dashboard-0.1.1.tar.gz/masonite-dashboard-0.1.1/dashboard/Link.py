class BaseLink:
    display = ''
    url = ''

    def visible(self):
        return True

    def show(self):
        return self.display

class UserLink:
    display = ''
    url = ''

    def visible(self):
        return True

    def show(self):
        return self.display