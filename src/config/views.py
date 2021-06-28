from django.views.generic import TemplateView

from rest_framework.authtoken.models import Token


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["tokens"] = Token.objects.filter(user=self.request.user)
        return context
