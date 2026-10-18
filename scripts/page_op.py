import pywikibot

class PageOp():
    def __init__(self, page=None, description=None):
        self.page = page
        self.description = description or []
    
    def get_title(self):
        return self.page and self.page.title() or self.title
    
    def __str__(self):
        return f"PageOp(description={self.description}, page={isinstance(self.page, pywikibot.Page) and self.page.title() or self.page})"
