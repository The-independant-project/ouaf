from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class BackofficeAccessRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    required_group = "Backoffice"
    login_url = "login"

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.groups.filter(name=self.required_group).exists()


