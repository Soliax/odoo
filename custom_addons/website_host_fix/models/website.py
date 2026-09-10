# -*- coding: utf-8 -*-
from odoo import api, models
from odoo.http import request


class Website(models.Model):
    _inherit = "website"

    @api.model
    def get_current_website(self, fallback=True):
        """Avoid using threading.current_thread().url as a domain.

        During module/XML install, that attribute is the file path being
        parsed. IDNA-encoding it raises UnicodeError: label too long
        (Odoo 19 website theme configurator / long paths).
        See https://github.com/odoo/odoo/issues/284682
        """
        is_frontend_request = request and getattr(request, "is_frontend", False)
        if request and request.session.get("force_website_id"):
            website_id = self.browse(request.session["force_website_id"]).exists()
            if not website_id:
                request.session.pop("force_website_id")
            else:
                return website_id

        website_id = self.env.context.get("website_id")
        if website_id:
            return self.browse(website_id)

        if not is_frontend_request and not fallback:
            return self.browse(False)

        domain_name = (request and request.httprequest.host) or ""
        if not self._is_valid_website_host(domain_name):
            domain_name = ""

        return self.browse(
            self.sudo()._get_current_website_id(domain_name, fallback=fallback)
        )

    @api.model
    def _is_valid_website_host(self, domain_name):
        if not domain_name:
            return False
        if "://" in domain_name or "/" in domain_name or "\\" in domain_name:
            return False
        host = domain_name.split(":")[0]
        if not host or len(host) > 253:
            return False
        for label in host.split("."):
            if not label or len(label) > 63:
                return False
        try:
            domain_name.encode("idna")
        except UnicodeError:
            return False
        return True
