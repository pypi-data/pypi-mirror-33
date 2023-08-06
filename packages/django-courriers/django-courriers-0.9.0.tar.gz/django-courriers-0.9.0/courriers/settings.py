from django.conf import settings


BACKEND_CLASS = getattr(
    settings, "COURRIERS_BACKEND_CLASS", "courriers.backends.simple.SimpleBackend"
)

MAILCHIMP_API_KEY = getattr(settings, "COURRIERS_MAILCHIMP_API_KEY", "")

MAILJET_API_KEY = getattr(settings, "COURRIERS_MAILJET_API_KEY", "")

MAILJET_CONTACTSLIST_LIMIT = getattr(
    settings, "COURRIERS_MAILJET_CONTACTSLIST_LIMIT", 1000
)

MAILJET_CONTACTFILTER_LIMIT = getattr(
    settings, "COURRIERS_MAILJET_CONTACTFILTER_LIMIT", 1000
)

MAILJET_API_SECRET_KEY = getattr(settings, "COURRIERS_MAILJET_API_SECRET_KEY", "")

DEFAULT_FROM_EMAIL = getattr(
    settings, "COURRIERS_DEFAULT_FROM_EMAIL", settings.DEFAULT_FROM_EMAIL
)

DEFAULT_FROM_NAME = getattr(settings, "COURRIERS_DEFAULT_FROM_NAME", "")

ALLOWED_LANGUAGES = getattr(settings, "COURRIERS_ALLOWED_LANGUAGES", settings.LANGUAGES)

PRE_PROCESSORS = getattr(settings, "COURRIERS_PRE_PROCESSORS", ())

PAGINATE_BY = getattr(settings, "COURRIERS_PAGINATE_BY", 9)

FAIL_SILENTLY = getattr(settings, "COURRIERS_FAIL_SILENTLY", False)

NEWSLETTERLIST_MODEL = getattr(
    settings,
    "COURRIERS_NEWSLETTERLIST_MODEL",
    "courriers.models.newsletterlist.NewsletterList",
)

NEWSLETTER_MODEL = getattr(
    settings, "COURRIERS_NEWSLETTER_MODEL", "courriers.models.newsletter.Newsletter"
)

NEWSLETTERITEM_MODEL = getattr(
    settings,
    "COURRIERS_NEWSLETTERITEM_MODEL",
    "courriers.models.newsletteritem.NewsletterItem",
)

NEWSLETTERSEGMENT_MODEL = getattr(
    settings,
    "COURRIERS_NEWSLETTERSEGMENT_MODEL",
    "courriers.models.newslettersegment.NewsletterSegment",
)
