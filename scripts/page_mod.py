import inspect
import json

from page_op import PageOp
import pywikibot

class PageMod(PageOp):
    def __init__(self, id=None, page=None, title=None, summary=None, description=None):
        super().__init__(page, description)
        self.id = id
        self.title = title
        self.summary = summary or []
    
    def to_dict(self):
        """Convert PageMod object to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'title': self.get_title() or None,
            'summary': self.summary
        }

    def get_title(self):
        return self.page and self.page.title() or self.title
    
    def __str__(self):
        return f"PageMod(id={self.id}, title={self.get_title()}, summary={self.summary}, description={self.description}, page={isinstance(self.page, pywikibot.Page) and self.page.title() or self.page})"
    
    @classmethod
    def from_dict(cls, data):
        """Create PageMod object from dictionary (for JSON deserialization)."""
        return cls(data['id'], None, data['title'], data['summary'])
    
    def to_json(self):
        """Convert PageMod object to JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str):
        """Create PageMod object from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

class PageModifier():

    def __init__(self, summary):
        self.summary = summary

    def process_page(self, page):
        pre_text = page.text
        self.process_page_logic(page)
        return pre_text != page.text

    def process_page_logic(self, page):
        raise Exception("Unimplemented function! Implement {}.{} ({}).".format(
            self.__class__.__name__,
            self.process_page.__name__,
            inspect.getfile(self.__class__)))

