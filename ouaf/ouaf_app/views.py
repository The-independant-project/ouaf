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
    Handle the contact form workflow with anti-abuse protections and three modes
    (standard contact, volunteer application, membership/adhesion).

    Overview:
        This view validates user input, applies per-IP rate limiting,
        renders email content from templates, sends an email to the organization,
        and sends an acknowledgment (ACK) to the user. It also adapts UI copy,
        email subjects, and success messaging based on the requested mode.

    Modes & Routing:
        - Mode selection is driven by the `type` query parameter:
            * "contact" (default)
            * "volunteer" | "benevole" | "bénévole"
            * "adhesion" | "adhésion" | "membership" | "join" | "adherer" | "adhérer"
        - The success redirect preserves the current `type` query parameter.

    UI & Context:
        - `MODE_CONFIG` centralizes per-mode copy:
            * title, intro, textarea placeholder
            * subject builder, ACK subject, success message
        - Template context includes:
            * `mode` (str): "contact" | "volunteer" | "adhesion"
            * `is_volunteer` (bool)
            * `is_membership` (bool)
            * `contact_title` (str)
            * `contact_intro` (str)

    Workflow:
        1. Apply per-IP rate limiting (default: 5 submissions / 15 minutes via cache).
        2. Validate the form (first/last name, email, phone, message, spam fields).
        3. Generate a unique request ID (UUID) for logging and correlation.
        4. Build context and render organization email (HTML + text fallback).
        5. Send the organization email (hard-fail on error with user-friendly message).
        6. Render and send the user ACK email (fail silently but log errors).
        7. Display a mode-specific success message and redirect.

    Email & Security:
        - Subjects are sanitized to prevent header injection and to enforce a max length.
        - Extra header: "X-Contact-Request-ID" is added to both emails.
        - Emails are sent with plain text and HTML alternatives.

    Templates:
        - "contact/contact.html"            : form rendering.
        - "emails/contact_to_org.html"      : HTML email to the organization.
        - "emails/contact_ack.html"         : HTML acknowledgment to the user.

    Settings:
        - CONTACT_RECIPIENTS (list[str])    : organization recipients (required).
        - DEFAULT_FROM_EMAIL (str)          : sender address.
        - EMAIL_SUBJECT_PREFIX (str, opt.)  : prefix added to outgoing subjects.

    Rate limiting:
        - Window length: RATE_LIMIT_WINDOW (seconds).
        - Max submissions: RATE_LIMIT_MAX per IP within the window.
        - Uses `cache.add`/`cache.incr` guarded by fallback `cache.set`.

    Attributes:
        template_name (str): Path to the contact form template.
        form_class (ContactForm): Form used for validation and cleaned data.
        RATE_LIMIT_MAX (int): Max submissions per IP per window.
        RATE_LIMIT_WINDOW (int): Window size in seconds.
        MODE_CONFIG (dict): Per-mode UI copy and behavior.

    Methods:
        get_context_data(**kwargs):
            Inject per-mode UI strings and flags into the template context.
        get_success_url():
            Preserve current `type` query parameter on redirect.
        _mode() -> str:
            Resolve the current mode from the `type` query parameter.
        get_form(form_class=None):
            Apply per-mode placeholder to the message field.
        _client_ip() -> str:
            Extract the client IP from X-Forwarded-For or REMOTE_ADDR.
        dispatch(request, *args, **kwargs):
            Enforce rate limiting before processing POST submissions.
        form_valid(form):
            Render and send organization + ACK emails, manage logging and messages.
        _safe_subject(text: str, max_len: int = 140) -> str:
            Sanitize and truncate subject lines for safe SMTP headers.
    """
    template_name = "contact/contact.html"
    form_class = ContactForm

    RATE_LIMIT_MAX = 5
    RATE_LIMIT_WINDOW = 15 * 60

    MODE_CONFIG = {
        "contact": {
            "title": "Contactez l’association",
            "intro": "Remplissez le formulaire ci-dessous, nous reviendrons vers vous rapidement.",
            "placeholder": "Expliquez-nous votre demande…",
            "subject": lambda d: f"[Contact] {d['first_name']} {d['last_name']}",
            "ack": "Nous avons bien reçu votre message",
            "success": "Merci ! Votre message a bien été envoyé. Nous vous répondrons au plus vite.",
        },
        "volunteer": {
            "title": "Devenir bénévole",
            "intro": "Envoyez-nous votre candidature : motivations, disponibilités et centres d’intérêt.",
            "placeholder": ("Présentez-vous et expliquez vos motivations, "
                            "vos disponibilités et le type de missions qui vous intéressent."),
            "subject": lambda d: "Candidature bénévolat",
            "ack": "Nous avons bien reçu votre candidature",
            "success": "Merci ! Votre candidature a bien été envoyée. Nous vous répondrons au plus vite.",
        },
        "adhesion": {
            "title": "Adhérer à l’association",
            "intro": "Envoyez votre candidature d’adhésion. Nous reviendrons vers vous pour la suite.",
            "placeholder": ("Présentez-vous et expliquez vos motivations à adhérer, "
                            "votre intérêt pour l’association et vos éventuelles disponibilités."),
            "subject": lambda d: "Candidature adhésion",
            "ack": "Nous avons bien reçu votre candidature d’adhésion",
            "success": "Merci ! Votre candidature d’adhésion a bien été envoyée. Nous vous répondrons au plus vite.",
        },
    }

    def _mode(self) -> str:
        raw = (self.request.GET.get("type") or "").lower()
        if raw in {"volunteer", "benevole", "bénévole"}:
            return "volunteer"
        if raw in {"adhesion", "adhésion", "membership", "join", "adherer", "adhérer"}:
            return "adhesion"
        return "contact"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        cfg = self.MODE_CONFIG[self._mode()]
        ctx.update({
            "contact_title": cfg["title"],
            "contact_intro": cfg["intro"],
            "is_volunteer": self._mode() == "volunteer",
            "is_membership": self._mode() == "adhesion",
            "mode": self._mode(),
        })
        return ctx

    def get_success_url(self):
        base = reverse_lazy("contact")
        mode = self.request.GET.get("type")
        return f"{base}?type={mode}" if mode else base

    def _is_volunteer_mode(self) -> bool:
        return (self.request.GET.get("type") or "").lower() in {"volunteer", "benevole", "bénévole"}

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        cfg = self.MODE_CONFIG[self._mode()]
        form.fields["message"].widget.attrs["placeholder"] = cfg["placeholder"]
        return form

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

            if current > 0:
                try:
                    cache.incr(key)
                except Exception:
                    cache.set(key, current + 1, timeout=self.RATE_LIMIT_WINDOW)
            else:
                cache.add(key, 1, timeout=self.RATE_LIMIT_WINDOW)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        data = form.cleaned_data
        req_id = str(uuid.uuid4())

        cfg = self.MODE_CONFIG[self._mode()]
        subject_base = cfg["subject"](data)
        subject = self._safe_subject(f"{getattr(settings, 'EMAIL_SUBJECT_PREFIX', '')}{subject_base}")

        ctx = {
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "email": data["email"],
            "phone": data["phone"],
            "message": data["message"],
            "request_id": req_id,
            "is_volunteer": self._mode() == "volunteer",
            "is_membership": self._mode() == "adhesion",
            "mode": self._mode(),
        }
        html = render_to_string("emails/contact_to_org.html", ctx)
        text = strip_tags(html)

        to_recipients = settings.CONTACT_RECIPIENTS
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
            org_msg.send(fail_silently=False)
        except Exception:
            logger.exception("Contact email failed", extra={"request_id": req_id})
            messages.error(self.request, "Désolé, l’envoi a échoué. Merci de réessayer dans quelques minutes.")
            return self.form_invalid(form)

        ack_subject = self._safe_subject(cfg["ack"])
        ack_html = render_to_string("emails/contact_ack.html", ctx)
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

        messages.success(self.request, cfg["success"])
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
