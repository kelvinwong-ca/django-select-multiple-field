from django.db import connection
from django.test import TestCase
from django.urls import reverse
from django.utils.datastructures import MultiValueDict
from django.utils.http import urlencode

from test_projects.asserts import safe_assert_redirects

from .models import Article, TaggedItem


class ORMExactLookupTestCase(TestCase):
    """Test exact match lookups on SelectMultipleField"""

    def setUp(self):
        self.a1 = TaggedItem.objects.create(name="Django API", tags=["django", "api"])
        self.a2 = TaggedItem.objects.create(name="Python Web", tags=["python", "web"])
        self.a3 = TaggedItem.objects.create(name="Django DB", tags=["django", "db"])
        self.a4 = TaggedItem.objects.create(name="API Only", tags=["api"])
        self.a5 = TaggedItem.objects.create(name="No Tags", tags=[])

    def test_exact_match_stored_csv(self):
        """Exact match on stored CSV string"""
        # DB stores "django,api" - query with that exact string
        qs = TaggedItem.objects.filter(tags="django,api")
        self.assertEqual(list(qs), [self.a1])

    def test_exact_match_single_tag(self):
        """Exact match on single tag - pass list"""
        qs = TaggedItem.objects.filter(tags=["api"])
        self.assertEqual(list(qs), [self.a4])

    def test_exact_match_empty(self):
        """Exact match on empty string"""
        qs = TaggedItem.objects.filter(tags="")
        self.assertEqual(list(qs), [self.a5])

    def test_exact_match_order_matters(self):
        """Order matters in exact match"""
        qs = TaggedItem.objects.filter(tags="api,django")
        self.assertEqual(list(qs), [])

    def test_exact_match_not_list(self):
        """Passing list to filter auto-encodes via get_prep_value"""
        qs = TaggedItem.objects.filter(tags=["django", "api"])
        self.assertEqual(list(qs), [self.a1])


class ORMContainsLookupTestCase(TestCase):
    """Test __contains lookup"""

    def setUp(self):
        self.a1 = TaggedItem.objects.create(name="Django API", tags=["django", "api"])
        self.a2 = TaggedItem.objects.create(name="Python Web", tags=["python", "web"])
        self.a3 = TaggedItem.objects.create(name="Django DB", tags=["django", "db"])
        self.a4 = TaggedItem.objects.create(name="API Only", tags=["api"])
        self.a5 = TaggedItem.objects.create(name="No Tags", tags=[])

    def test_contains_single_tag(self):
        """__contains matches substring in CSV"""
        qs = TaggedItem.objects.filter(tags__contains="django")
        self.assertEqual(set(qs), {self.a1, self.a3})

    def test_contains_false_positive_risk(self):
        """__contains can match partial codes - 'py' matches 'python'"""
        qs = TaggedItem.objects.filter(tags__contains="py")
        # "python" contains "py" - matches a2 (python,web)
        self.assertEqual(qs.count(), 1)

    def test_contains_case_insensitive(self):
        """SQLite __contains is case-insensitive by default"""
        qs = TaggedItem.objects.filter(tags__contains="DJANGO")
        self.assertEqual(qs.count(), 2)  # "django" matches "DJANGO"

    def test_exclude_contains(self):
        """Exclude items containing a tag"""
        qs = TaggedItem.objects.exclude(tags__contains="django")
        self.assertEqual(set(qs), {self.a2, self.a4, self.a5})


class ORMInLookupTestCase(TestCase):
    """Test __in lookup"""

    def setUp(self):
        self.a1 = TaggedItem.objects.create(name="Django API", tags=["django", "api"])
        self.a2 = TaggedItem.objects.create(name="Python Web", tags=["python", "web"])
        self.a3 = TaggedItem.objects.create(name="Django DB", tags=["django", "db"])
        self.a4 = TaggedItem.objects.create(name="API Only", tags=["api"])
        self.a5 = TaggedItem.objects.create(name="No Tags", tags=[])

    def test_in_exact_csv_values(self):
        """__in matches exact CSV strings"""
        qs = TaggedItem.objects.filter(tags__in=["django,api", "python,web"])
        self.assertEqual(set(qs), {self.a1, self.a2})

    def test_in_with_empty(self):
        """__in with empty string"""
        qs = TaggedItem.objects.filter(tags__in=["django,api", ""])
        self.assertEqual(set(qs), {self.a1, self.a5})


class ORMNullBlankTestCase(TestCase):
    """Test null/blank behavior in queries"""

    def setUp(self):
        self.p1 = Article.objects.create(
            title="Django Article", optional_tags=["django", "orm"]
        )
        self.p2 = Article.objects.create(
            title="Python Article", optional_tags=["python"]
        )
        self.p3 = Article.objects.create(title="No Tags Article")
        self.p4 = Article.objects.create(title="Empty Tags", optional_tags=[])

    def test_null_stored_as_null(self):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT optional_tags FROM orm_test_article WHERE id = %s", [self.p3.pk]
            )
            row = cursor.fetchone()
        self.assertIsNone(row[0])

    def test_empty_list_stored_as_null(self):
        """With null=True, blank=True, empty list stores as NULL"""
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT optional_tags FROM orm_test_article WHERE id = %s", [self.p4.pk]
            )
            row = cursor.fetchone()
        self.assertIsNone(row[0])

    def test_filter_null_vs_empty(self):
        """NULL and empty string are both NULL with null=True"""
        null_qs = Article.objects.filter(optional_tags__isnull=True)
        empty_qs = Article.objects.filter(optional_tags="")
        # Both NULL - empty list also stores as NULL
        self.assertEqual(set(null_qs), {self.p3, self.p4})
        self.assertEqual(list(empty_qs), [])

    def test_contains_on_null_field(self):
        """__contains on null field excludes NULL rows"""
        qs = Article.objects.filter(optional_tags__contains="django")
        self.assertEqual(list(qs), [self.p1])


class ORMEdgeCasesTestCase(TestCase):
    """Edge cases and advanced queries"""

    def setUp(self):
        TaggedItem.objects.create(name="A1", tags=["python", "django"])
        TaggedItem.objects.create(name="A2", tags=["python"])
        TaggedItem.objects.create(name="A3", tags=[])

    def test_order_by_tags(self):
        """Order by tags (lexicographic on stored CSV)"""
        qs = TaggedItem.objects.order_by("tags")
        names = [item.name for item in qs]
        # CSV strings: "" < "python" < "python,django"
        self.assertEqual(names, ["A3", "A2", "A1"])

    def test_values_list_returns_decoded_list(self):
        """values_list returns Python list (decoded by field)"""
        vals = TaggedItem.objects.filter(name="A1").values_list("tags", flat=True)
        self.assertEqual(list(vals), [["python", "django"]])

    def test_values_returns_decoded_list(self):
        """values returns Python list"""
        vals = TaggedItem.objects.filter(name="A1").values("tags")
        self.assertEqual(list(vals), [{"tags": ["python", "django"]}])

    def test_tag_with_same_prefix(self):
        """Tags 'api' and 'api_v2' - contains 'api' matches both"""
        TaggedItem.objects.create(name="API v2", tags=["api_v2"])
        TaggedItem.objects.create(name="API", tags=["api"])
        qs = TaggedItem.objects.filter(tags__contains="api")
        self.assertEqual(qs.count(), 2)

    def test_bulk_create(self):
        items = [
            TaggedItem(name="Bulk1", tags=["a", "b"]),
            TaggedItem(name="Bulk2", tags=["c"]),
        ]
        TaggedItem.objects.bulk_create(items)
        self.assertEqual(
            TaggedItem.objects.filter(name="Bulk1").first().tags, ["a", "b"]
        )

    def test_update_tags(self):
        item = TaggedItem.objects.create(name="Orig", tags=["old"])
        item.tags = ["new", "tags"]
        item.save()
        item.refresh_from_db()
        self.assertEqual(item.tags, ["new", "tags"])


class ORMFormIntegrationTestCase(TestCase):
    """Test ORM operations through forms"""

    def test_create_via_form_then_query(self):
        data = {"name": "Form Item", "tags": ["django", "web"], "category": "tech"}
        response = self.client.post(
            reverse("orm:create"),
            urlencode(MultiValueDict(data), doseq=True),
            content_type="application/x-www-form-urlencoded",
        )
        self.assertEqual(response.status_code, 302)
        item = TaggedItem.objects.get(name="Form Item")
        self.assertEqual(item.tags, ["django", "web"])
        # Query back
        qs = TaggedItem.objects.filter(tags__contains="django")
        self.assertIn(item, qs)

    def test_update_via_form_then_query(self):
        item = TaggedItem.objects.create(
            name="Original", tags=["python"], category="tech"
        )
        data = {"name": "Updated", "tags": ["api", "db"], "category": "tech"}
        response = self.client.post(
            reverse("orm:update", args=[item.pk]),
            urlencode(MultiValueDict(data), doseq=True),
            content_type="application/x-www-form-urlencoded",
        )
        self.assertEqual(response.status_code, 302)
        item.refresh_from_db()
        self.assertEqual(item.tags, ["api", "db"])


class ORMMigrationTestCase(TestCase):
    def test_migration_applied(self):
        from django.db.migrations.recorder import MigrationRecorder

        recorder = MigrationRecorder(connection)
        applied = recorder.applied_migrations()
        self.assertIn(("orm_test", "0001_initial"), applied)
