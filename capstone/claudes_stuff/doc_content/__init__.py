"""Hand-written descriptions merged into the generated code documentation.

Every module except ``overview`` and ``api`` exposes ``FILES``, a dict keyed by
the project-relative source path::

    FILES = {
        "backend/src/features/plant_scan/service.rs": {
            "summary": "What the file is for (1-4 sentences).",
            "details": "Optional extra file-level notes: dependencies, how it fits in.",
            "symbols": {
                # Functions/methods/components/hooks/tests: a dict.
                "scan_plant_image": {
                    "description": "What it does and why.",
                    "params": {"image_bytes": "Raw image bytes."},  # optional
                    "returns": "What it returns.",                  # optional
                    "errors": ["MissingImage: no bytes", "..."],    # optional, str or list
                    "notes": "Side effects, edge cases, test hints.",  # optional
                },
                # Types/constants (or trivial functions): a plain string.
                "MAX_IMAGE_BYTES": "Upload size limit (10 MiB).",
            },
        },
    }

Symbol keys must match the names the extractor produces exactly (run
``generate_external_code_doc.py --check`` to list missing and stale keys):

* Rust free functions: ``name``; inherent methods: ``Type::method``; trait impl
  methods: ``Type::method [Trait]``; trait declarations: ``Trait::method``;
  items in inline modules: ``tests::name``.
* TypeScript: ``name``; inner functions: ``Parent.inner``; zustand store
  actions: ``useStore.action``.

``api.ROUTES`` is keyed by ``"METHOD /path"`` and holds ``summary``, ``request``,
``response``, ``errors``, ``notes`` and an optional ``access`` override.
"""

from . import backend, frontend, shared, tauri, tests

FILE_MODULES = (backend, shared, tauri, frontend, tests)
