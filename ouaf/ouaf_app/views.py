from django.db.models import Prefetch
from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required, login_not_required
from django.urls import reverse_lazy
from django.views.generic import ListView, FormView
from django.http import HttpRequest, HttpResponse
from .forms import PersonForm, RegistrationForm, ContactForm
from .models import OrganisationChartEntry, Activity, ActivityCategory, Animal, AnimalMedia
from django.contrib import messages
from django.utils.translation import gettext as _
from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.utils.html import strip_tags
from django.template.loader import render_to_string
import logging
import uuid
from django.core.cache import cache


def index(request):
    return render(request, "index.html")


def my_logout(request):
    logout(request)
    return redirect("/")


def signup_user(request: HttpRequest):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            new_user = authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'])
            login(request, new_user)
            return redirect("/")
        else:
            print(form.errors)
    else:
        form = RegistrationForm()
    template_name = "registration/signup.html"
    context = {"form": form}
    return render(request, template_name, context)


@login_required
def account_edit(request):
    if request.method == "POST":
        form = PersonForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
    else:
        form = PersonForm(instance=request.user)
    template_name = "account/account_edit.html"
    context = {"form": form}
    return render(request, template_name, context)


def organisation_chart(request):
    context = {"organisation_members": OrganisationChartEntry.objects.all()}
    return render(request, "organisationChart.html", context)


def mediation_animale(request):
    return render(request, "mediationAnimale.html")


def confidentialite(request):
    return render(request, "confidentialite.html")


class ActivityCategoryListView(ListView):
    model = ActivityCategory
    template_name = "activities/list.html"
    context_object_name = "categories"
    raise_exception = True


class ActivitiesByCategoryView(ListView):
    model = Activity
    template_name = "activities/by_category.html"
    context_object_name = "activities"

    def get_queryset(self):
        return Activity.objects.filter(category_id=self.kwargs["pk"]).order_by("title")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["category"] = ActivityCategory.objects.get(pk=self.kwargs["pk"])
        return ctx


logger = logging.getLogger(__name__)


class ContactView(FormView):
    """
    Handle the contact form workflow: validate input, apply anti-abuse protections,
    and send emails to both the organization and the user.

    Workflow:
        1. Apply per-IP rate limiting to prevent abuse (default: 5 submissions per 15 min).
        2. Validate the form (first/last name, email, phone, message, spam fields).
        3. Generate a unique request ID (UUID) for correlation and logging.
        4. Send a formatted email with details to the organization inbox.
        5. Send an acknowledgment (ACK) email to the user confirming receipt.
        6. Provide success or error feedback through Django messages.

    Features:
        - Rate limiting based on client IP address (stored in cache).
        - Sanitized subject lines to prevent header injection attacks.
        - Dual format emails (plain text + HTML) for maximum compatibility.
        - Separate templates for organization and acknowledgment messages.
        - Robust error handling: logs failures and prevents UX disruption if
          acknowledgment email delivery fails.
        - Custom headers (e.g., X-Contact-Request-ID) for traceability.

    Templates:
        - contact/contact.html: Form rendering.
        - emails/contact_to_org.html: HTML email to organization.
        - emails/contact_ack.html: HTML acknowledgment to user.

    Success URL:
        Redirects back to the "contact" page after successful submission.

    Attributes:
        template_name (str): Path to the contact form template.
        form_class (ContactForm): Form used for validation and cleaned data.
        RATE_LIMIT_MAX (int): Maximum number of allowed submissions per IP.
        RATE_LIMIT_WINDOW (int): Rate limit window duration (seconds).

    Methods:
        get_success_url():
            Return redirect URL after success.
        _client_ip():
            Extract the client IP address from request headers.
        dispatch(request, *args, **kwargs):
            Apply rate limiting before dispatching the request.
        form_valid(form):
            Process valid form submission, handle email sending, logging,
            and user feedback.
        _safe_subject(text, max_len=140):
            Sanitize and truncate subject lines for safe usage in SMTP headers.
    """
    template_name = "contact/contact.html"
    form_class = ContactForm

    RATE_LIMIT_MAX = 5  # 5 submit
    RATE_LIMIT_WINDOW = 15 * 60  # 15 minutes

    def get_success_url(self):
        return reverse_lazy("contact")

    def _client_ip(self) -> str:
        xff = self.request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            return xff.split(",")[0].strip()
        return self.request.META.get("REMOTE_ADDR", "0.0.0.0")

    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST":
            ip = self._client_ip()
            key = f"contact_rl:{ip}"
            current = cache.get(key, 0)

            if current >= self.RATE_LIMIT_MAX:
                messages.error(request, "Trop de tentatives. Réessayez dans quelques minutes.")
                return HttpResponse("Rate limit exceeded", status=429)

            added = cache.add(key, 1, timeout=self.RATE_LIMIT_WINDOW)
            if not added:
                try:
                    cache.incr(key)
                except Exception:
                    cache.set(key, current + 1, timeout=self.RATE_LIMIT_WINDOW)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        data = form.cleaned_data
        req_id = str(uuid.uuid4())

        subject = self._safe_subject(
            f"{getattr(settings, 'EMAIL_SUBJECT_PREFIX', '')}[Contact] "
            f"{data['first_name']} {data['last_name']}"
        )
        ctx = {
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "email": data["email"],
            "phone": data["phone"],
            "message": data["message"],
            "request_id": req_id,
        }
        html = render_to_string("emails/contact_to_org.html", ctx)
        text = strip_tags(html)

        to_recipients = getattr(settings, "CONTACT_RECIPIENTS", [settings.DEFAULT_FROM_EMAIL])

        org_msg = EmailMultiAlternatives(
            subject=subject,
            body=text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=to_recipients,
            reply_to=[data["email"]],
        )
        org_msg.attach_alternative(html, "text/html")
        org_msg.extra_headers = {"X-Contact-Request-ID": req_id}

        try:
            sent = org_msg.send(fail_silently=False)
            logger.info("Contact email sent",
                        extra={"request_id": req_id, "to": to_recipients, "result": sent})
        except Exception:
            logger.exception("Contact email failed", extra={"request_id": req_id})
            messages.error(self.request, "Désolé, l’envoi a échoué. Merci de réessayer dans quelques minutes.")
            return self.form_invalid(form)

        ack_subject = self._safe_subject("Nous avons bien reçu votre message")
        ack_ctx = {"first_name": data["first_name"], "request_id": req_id}
        ack_html = render_to_string("emails/contact_ack.html", ack_ctx)
        ack_text = strip_tags(ack_html)

        ack_msg = EmailMultiAlternatives(
            subject=ack_subject,
            body=ack_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[data["email"]],
        )
        ack_msg.attach_alternative(ack_html, "text/html")
        ack_msg.extra_headers = {"X-Contact-Request-ID": req_id}

        try:
            ack_msg.send(fail_silently=True)
        except Exception:
            logger.exception("Contact ACK failed", extra={"request_id": req_id})

        messages.success(self.request, "Merci ! Votre message a bien été envoyé. Nous vous répondrons au plus vite.")
        return super().form_valid(form)

    @staticmethod
    def _safe_subject(text: str, max_len: int = 140) -> str:
        """
        Sanitize an email subject line for safe usage in SMTP headers.

        Ensures:
            - No CR/LF injection (removes line breaks).
            - Single-line subject with leading/trailing spaces trimmed.
            - Maximum length enforced (default: 140 characters).

        Args:
            text (str): The raw subject line text (possibly user-provided).
            max_len (int, optional): Maximum length allowed for the subject.
                                     Defaults to 140.

        Returns:
            str: A sanitized and truncated subject line safe for email headers.
        """
        s = " ".join(str(text).splitlines()).strip()
        return s[:max_len]


def animal_list(request):
    animals = Animal.objects.prefetch_related(Prefetch("media", to_attr="medias")).all()
    for animal in animals:
        if animal.medias:
            pres_image = next(media for media in animal.medias if media.is_image)
            if pres_image:
                animal.presentation_image = pres_image.file
    return render(request, "animals/list.html", {"animals": animals})


def animal_detail(request, animal_id):
    animal = Animal.objects.filter(id=animal_id).first()
    medias = AnimalMedia.objects.filter(animal_id=animal_id)
    if medias:
        pres_image = next(media for media in medias if media.is_image)
        if pres_image:
            animal.presentation_image = pres_image.file
    return render(request, "animals/detail.html", {"animal": animal, "medias": medias})
