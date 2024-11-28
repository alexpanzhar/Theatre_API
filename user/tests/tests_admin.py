from django.contrib import admin
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext as _

from user.admin import UserAdmin
from user.models import User


class UserAdminTests(TestCase):
    def setUp(self):
        self.admin_site = admin.site

    def test_user_model_registered(self):
        """Test that the User model is registered in the admin site."""
        self.assertIn(User, self.admin_site._registry)
        self.assertIsInstance(self.admin_site._registry[User], UserAdmin)

    def test_fieldsets_configuration(self):
        """Test the fieldsets configuration in the admin."""
        expected_fieldsets = (
            (None, {"fields": ("email", "password")}),
            (_("Personal info"), {"fields": ("first_name", "last_name")}),
            (
                _("Permissions"),
                {
                    "fields": (
                        "is_active",
                        "is_staff",
                        "is_superuser",
                        "groups",
                        "user_permissions",
                    )
                },
            ),
            (_("Important dates"), {"fields": ("last_login", "date_joined")}),
        )
        self.assertEqual(UserAdmin.fieldsets, expected_fieldsets)

    def test_add_fieldsets_configuration(self):
        """Test the add_fieldsets configuration in the admin."""
        expected_add_fieldsets = (
            (
                None,
                {
                    "classes": ("wide",),
                    "fields": ("email", "password1", "password2"),
                },
            ),
        )
        self.assertEqual(UserAdmin.add_fieldsets, expected_add_fieldsets)

    def test_list_display_configuration(self):
        """Test the list_display configuration in the admin."""
        expected_list_display = ("email", "first_name", "last_name", "is_staff")
        self.assertEqual(UserAdmin.list_display, expected_list_display)

    def test_search_fields_configuration(self):
        """Test the search_fields configuration in the admin."""
        expected_search_fields = ("email", "first_name", "last_name")
        self.assertEqual(UserAdmin.search_fields, expected_search_fields)

    def test_ordering_configuration(self):
        """Test the ordering configuration in the admin."""
        expected_ordering = ("email",)
        self.assertEqual(UserAdmin.ordering, expected_ordering)

    def test_admin_changelist_accessible(self):
        """Test the admin changelist page for the User model is accessible."""
        # Create a superuser to access the admin
        admin_user = User.objects.create_superuser(
            email="admin@example.com",
            password="password123",
        )
        self.client.force_login(admin_user)

        url = reverse("admin:user_user_changelist")  # Default URL pattern for User in admin
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
