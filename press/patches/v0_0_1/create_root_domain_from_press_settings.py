# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


def execute():
	frappe.reload_doc("press", "doctype", "root_domain")
	press_settings = frappe.get_doc("Press Settings", "Press Settings")
	if not frappe.db.exists("Root Domain", press_settings.domain):
		frappe.get_doc(
			{
				"doctype": "Root Domain",
				"name": press_settings.domain,
				"dns_provider": press_settings.dns_provider,
				"aws_access_key_id": press_settings.aws_access_key_id,
				"aws_secret_access_key": press_settings.get_password("aws_secret_access_key"),
			}
		).insert()
