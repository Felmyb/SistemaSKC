from django.core.management.base import BaseCommand
from django.urls import reverse
from django.test import Client
from django.conf import settings
from django.test.utils import override_settings
from pathlib import Path
import json


class Command(BaseCommand):
    help = "Export OpenAPI schema to a JSON file using the internal schema endpoint"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            type=str,
            default="spec/openapi.json",
            help="Output path for the generated OpenAPI JSON (relative to Backend)",
        )

    def handle(self, *args, **options):
        output = options["output"]
        client = Client()

        schema_url = reverse("schema-json") + "?format=json"
        hosts = list(getattr(settings, "ALLOWED_HOSTS", []))
        for h in ("testserver", "localhost", "127.0.0.1"):
            if h not in hosts:
                hosts.append(h)

        with override_settings(ALLOWED_HOSTS=hosts):
            response = client.get(schema_url, **{"HTTP_HOST": "localhost", "HTTP_ACCEPT": "application/json"})
        if response.status_code != 200:
            self.stderr.write(self.style.ERROR(f"Failed to fetch schema: HTTP {response.status_code}"))
            return

        # Ensure directory exists (relative to Backend working dir)
        out_path = Path(output)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        # Write JSON (ensure pretty formatting)
        try:
            data = response.json()
        except Exception:
            try:
                data = json.loads(response.content.decode("utf-8"))
            except Exception:
                self.stderr.write(self.style.ERROR("Schema response is not valid JSON; writing raw content"))
                out_path.write_bytes(response.content)
                return

        with out_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS(f"OpenAPI spec exported to {out_path}"))
