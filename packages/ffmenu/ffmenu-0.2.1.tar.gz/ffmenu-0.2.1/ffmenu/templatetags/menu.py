from django import template
from ffmenu.menu import manager

register = template.Library()


@register.inclusion_tag('ffmenu/menu.html', takes_context=True)
def render_menu(context, name):
    menu_class = manager.get(name)
    menu = menu_class(context['request'])

    return {
        'menu': menu
    }
