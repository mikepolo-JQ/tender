
from django.views.generic import TemplateView


class TestChatView(TemplateView):
    template_name = "chat/test.html"
