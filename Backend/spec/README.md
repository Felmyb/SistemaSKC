# API Spec Kit (Backend)

This folder contains the OpenAPI specification and linting rules for the SmartKitchen Connect backend.

## Generate the spec

From `Backend/` run:

```bash
python manage.py export_openapi --output spec/openapi.json
```

## Lint the spec

Using Spectral (requires Node):

```bash
npx @stoplight/spectral-cli lint spec/openapi.json -r spec/.spectral.yaml
```

## CI Integration

The Azure Pipeline will generate the spec and lint it automatically on each run. The generated `spec/openapi.json` is also published as a build artifact.
