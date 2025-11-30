import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class MinSixAlphaNumericValidator:
    def validate(self, password, user=None):
        if len(password) < 6:
            raise ValidationError(_("A senha deve ter pelo menos 6 caracteres."), code="password_too_short")
        if not re.search(r"[A-Za-z]", password):
            raise ValidationError(_("A senha deve conter pelo menos uma letra."), code="password_no_letter")
        if not re.search(r"\d", password):
            raise ValidationError(_("A senha deve conter pelo menos um número."), code="password_no_number")

    def get_help_text(self):
        return _("Sua senha deve ter pelo menos 6 caracteres, incluindo ao menos uma letra e um número.")