class Menu(object):
    menu_id = None
    menu_class = "nav"

    def __init__(self, request):
        self._items = self._build_items(request)

    def __iter__(self):
        for i in self._items:
            yield i

    def _build_items(self, request):
        items = self.get_children(request)

        for i in items:
            self._mark_item(i, request)
        return items

    # naive path matching
    def _mark_item(self, item, request):
        item._active = item.is_matching(request)

        for c in item._children:
            self._mark_item(c, request)

    def get_children(self, request):
        raise NotImplementedError


class MenuItem(object):
    def __init__(self, label, url, *children, exact=False):
        self.label = label
        self.url = url
        self.exact = exact
        self._children = children
        self._active = False

    def is_matching(self, request):
        path = request.path

        if self.exact:
            return path == self.url

        return path.startswith(self.url)

    @property
    def active(self):
        return self._active

    @property
    def children(self):
        return self._children


class PageMenu(Menu):
    def get_pages(self, request):
        raise NotImplementedError

    def get_children(self, request):
        return [self.page_to_item(page) for page in self.get_pages(request) if page.show_in_menus]

    def page_to_item(self, page):
        return MenuItem(
            page.title,
            page.url,
            *[self.page_to_item(child) for child in page.get_children() if child.show_in_menus]
        )


class Manager(object):
    def __init__(self):
        self._registry = {}

    def register(self, name, menu):
        self._registry[name] = menu

    def get(self, name):
        return self._registry[name]


manager = Manager()

