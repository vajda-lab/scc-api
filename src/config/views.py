from django.views.generic import TemplateView, ListView
from ftmap.models import Example

class HomeView(TemplateView):
    template_name = "home.html"


class FeaturesView(TemplateView):
    template_name = "features.html"


class AboutView(TemplateView):
    template_name = "about.html"


class ContactView(TemplateView):
    template_name = "contact.html"


class ExamplesView(ListView):
    model = Example
    template_name = "examples.html"
