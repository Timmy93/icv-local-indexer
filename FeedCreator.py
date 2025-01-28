import rfeed

class FeedCreator:

    def __init__(self, title, link, description):
        self.title = title
        self.link = link
        self.description = description
        self.items = []

    def add_item(self, title, link, description):
        self.items.append(rfeed.Item(title=title, link=link, description=description))

    def create_feed(self):
        feed = rfeed.Feed(title=self.title, link=self.link, description=self.description, items=self.items)
        return feed.rss()