"""Generate the Leaf Freak external code documentation as a Word document.

The generator is a hybrid: tree-sitter parses the Rust and TypeScript sources to
collect files, symbols, signatures, Axum routes and Tauri commands, and the
hand-written descriptions in ``doc_content/`` are merged on top. Symbols that
exist in code but have no description are rendered as "Undocumented" and listed
in a coverage report so the descriptions can be kept current.

Usage:
    env/bin/python generate_external_code_doc.py [--output PATH] [--inventory PATH]
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import tree_sitter_rust  # noqa: E402
import tree_sitter_typescript  # noqa: E402
from docx import Document  # noqa: E402
from docx.document import Document as DocxDocument  # noqa: E402
from docx.enum.style import WD_STYLE_TYPE  # noqa: E402
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK  # noqa: E402
from docx.oxml import OxmlElement  # noqa: E402
from docx.oxml.ns import qn  # noqa: E402
from docx.shared import Inches, Pt, RGBColor  # noqa: E402
from docx.table import Table, _Cell  # noqa: E402
from docx.text.paragraph import Paragraph  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402
from tree_sitter import Language, Node, Parser  # noqa: E402

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DEFAULT_OUTPUT = SCRIPT_DIR / "output" / "Leaf_Freak_External_Code_Documentation.docx"

sys.path.insert(0, str(SCRIPT_DIR))

import doc_content  # noqa: E402
from doc_content import api as api_content  # noqa: E402
from doc_content import overview as overview_content  # noqa: E402

# ---------------------------------------------------------------------------
# Source discovery
# ---------------------------------------------------------------------------

AREA_BACKEND = "Backend Server"
AREA_SHARED = "Shared Crates"
AREA_TAURI = "Tauri Shell"
AREA_CAMERA = "Camera Plugin"
AREA_FRONTEND = "Frontend"
AREA_TESTS = "Tests"

AREA_ORDER = [AREA_BACKEND, AREA_SHARED, AREA_TAURI, AREA_CAMERA, AREA_FRONTEND]

# (root relative to project, glob, area). Order matters: first match wins.
SOURCE_ROOTS = [
    ("backend/src/tests", "**/*.rs", AREA_TESTS),
    ("backend/crates/tb_client/tests", "**/*.rs", AREA_TESTS),
    ("backend/src", "**/*.rs", AREA_BACKEND),
    ("backend/crates/server_types/src", "**/*.rs", AREA_SHARED),
    ("backend/crates/tb_client/src", "**/*.rs", AREA_SHARED),
    ("src-tauri/src", "**/*.rs", AREA_TAURI),
    ("src-tauri/crates/tauri-plugin-camera/src", "**/*.rs", AREA_CAMERA),
    ("src", "**/*.ts", AREA_FRONTEND),
    ("src", "**/*.tsx", AREA_FRONTEND),
]

SHADCN_UI_DIR = "src/components/ui"
# Custom code that lives inside the shadcn ui folder and is documented in full.
SHADCN_UI_CUSTOM = ("src/components/ui/canvas-effects/",)
EXCLUDED_DIRS = ("src/generated/",)

TAURI_REGISTRY = "src-tauri/src/commands/tauri_registry.rs"
TAURI_GENERATED_COMMANDS = "src/generated/commands.ts"
TB_CLIENT_CLIENTS_DIR = "backend/crates/tb_client/src/clients"
BACKEND_MAIN = "backend/src/main.rs"


def rel(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()


def is_shadcn_ui(path: str) -> bool:
    return path.startswith(SHADCN_UI_DIR + "/") and not path.startswith(SHADCN_UI_CUSTOM)


def discover_sources() -> tuple[dict[str, str], list[str]]:
    """Return ({relative path: area}, [shadcn ui paths])."""
    files: dict[str, str] = {}
    shadcn: list[str] = []
    for root, pattern, area in SOURCE_ROOTS:
        base = PROJECT_ROOT / root
        if not base.exists():
            continue
        for path in sorted(base.glob(pattern)):
            path_rel = rel(path)
            if path_rel in files or path_rel in shadcn:
                continue
            if path_rel.startswith(EXCLUDED_DIRS) or path_rel.endswith(".d.ts"):
                continue
            if is_shadcn_ui(path_rel):
                shadcn.append(path_rel)
                continue
            files[path_rel] = area
    return files, sorted(shadcn)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

FUNCTION_KINDS = {
    "function",
    "method",
    "trait method",
    "component",
    "hook",
    "inner function",
    "store action",
    "tauri command",
    "route handler",
    "test",
}


@dataclass
class Param:
    name: str
    type: str


@dataclass
class Symbol:
    name: str
    kind: str
    line: int
    signature: str = ""
    params: list[Param] = field(default_factory=list)
    returns: str = ""
    doc: str = ""
    attributes: list[str] = field(default_factory=list)
    visibility: str = ""
    is_test: bool = False

    @property
    def is_function(self) -> bool:
        return self.kind in FUNCTION_KINDS


@dataclass
class SourceFile:
    path: str
    area: str
    language: str
    line_count: int
    module_doc: str = ""
    symbols: list[Symbol] = field(default_factory=list)


@dataclass
class Route:
    method: str
    path: str
    handler: str
    file: str
    line: int
    access: str


@dataclass
class TauriCommand:
    name: str
    frontend_binding: str
    signature: str
    params: list[Param]
    returns: str
    doc: str
    client_calls: list[str]
    endpoints: list[str]


# ---------------------------------------------------------------------------
# Tree-sitter helpers
# ---------------------------------------------------------------------------

RUST = Language(tree_sitter_rust.language())
TS = Language(tree_sitter_typescript.language_typescript())
TSX = Language(tree_sitter_typescript.language_tsx())


def text(node: Node | None) -> str:
    if node is None:
        return ""
    return node.text.decode("utf-8", errors="replace")


def squash(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def clean_doc_lines(lines: list[str]) -> str:
    cleaned: list[str] = []
    for line in lines:
        line = line.strip()
        line = re.sub(r"^(///|//!)\s?", "", line)
        line = re.sub(r"^/\*\*+\s?|\s*\*+/$", "", line)
        line = re.sub(r"^\*\s?", "", line)
        cleaned.append(line.rstrip())
    return "\n".join(cleaned).strip()


def leading_trivia(node: Node, trivia_types: tuple[str, ...]) -> list[Node]:
    """Comments and attributes immediately preceding a node, in source order."""
    collected: list[Node] = []
    sibling = node.prev_sibling
    while sibling is not None and sibling.type in trivia_types:
        collected.append(sibling)
        sibling = sibling.prev_sibling
    return list(reversed(collected))


def header_text(node: Node, body: Node | None) -> str:
    source = node.text
    if body is not None:
        source = source[: body.start_byte - node.start_byte]
    header = squash(source.decode("utf-8", errors="replace").rstrip("{; \n"))
    return re.sub(r",?\s+\)", ")", re.sub(r"([(<])\s+", r"\1", header))


# ---------------------------------------------------------------------------
# Rust extraction
# ---------------------------------------------------------------------------

RUST_TYPE_KINDS = {
    "struct_item": "struct",
    "enum_item": "enum",
    "trait_item": "trait",
    "type_item": "type alias",
    "const_item": "const",
    "static_item": "static",
}


def rust_doc_and_attrs(node: Node) -> tuple[str, list[str]]:
    trivia = leading_trivia(node, ("line_comment", "block_comment", "attribute_item"))
    doc_lines = [
        text(n) for n in trivia if n.type != "attribute_item" and text(n).startswith(("///", "/**"))
    ]
    attrs = [squash(text(n)) for n in trivia if n.type == "attribute_item"]
    return clean_doc_lines(doc_lines), attrs


def rust_visibility(node: Node) -> str:
    for child in node.children:
        if child.type == "visibility_modifier":
            return text(child)
    return ""


def rust_params(params_node: Node | None) -> list[Param]:
    params: list[Param] = []
    if params_node is None:
        return params
    for child in params_node.named_children:
        if child.type == "self_parameter":
            params.append(Param(text(child), "Self"))
        elif child.type == "parameter":
            params.append(
                Param(
                    squash(text(child.child_by_field_name("pattern"))),
                    squash(text(child.child_by_field_name("type"))),
                )
            )
    return params


def rust_base_type_name(type_text: str) -> str:
    return re.split(r"[<\s]", type_text.strip(), maxsplit=1)[0]


def rust_function_symbol(node: Node, name: str, kind: str, in_test_mod: bool) -> Symbol:
    doc, attrs = rust_doc_and_attrs(node)
    body = node.child_by_field_name("body")
    is_test = in_test_mod or any(re.search(r"#\[(tokio::)?test", a) for a in attrs)
    if any("tauri::command" in a for a in attrs):
        kind = "tauri command"
    if is_test and any(re.search(r"#\[(tokio::)?test", a) for a in attrs):
        kind = "test"
    return Symbol(
        name=name,
        kind=kind,
        line=node.start_point[0] + 1,
        signature=header_text(node, body),
        params=rust_params(node.child_by_field_name("parameters")),
        returns=squash(text(node.child_by_field_name("return_type"))),
        doc=doc,
        attributes=attrs,
        visibility=rust_visibility(node),
        is_test=is_test,
    )


def rust_walk(container: Node, prefix: str, in_test_mod: bool, out: list[Symbol]) -> None:
    for node in container.named_children:
        if node.type == "function_item":
            name = prefix + text(node.child_by_field_name("name"))
            out.append(rust_function_symbol(node, name, "function", in_test_mod))
        elif node.type == "impl_item":
            type_name = rust_base_type_name(text(node.child_by_field_name("type")))
            trait = node.child_by_field_name("trait")
            body = node.child_by_field_name("body")
            if body is None:
                continue
            trait_suffix = f" [{squash(text(trait))}]" if trait is not None else ""
            for item in body.named_children:
                if item.type == "function_item":
                    sym = rust_function_symbol(
                        item,
                        f"{prefix}{type_name}::{text(item.child_by_field_name('name'))}{trait_suffix}",
                        "method",
                        in_test_mod,
                    )
                    if trait is not None:
                        sym.attributes.append(f"impl {squash(text(trait))} for {type_name}")
                    out.append(sym)
        elif node.type == "trait_item":
            trait_name = text(node.child_by_field_name("name"))
            doc, attrs = rust_doc_and_attrs(node)
            out.append(
                Symbol(
                    name=prefix + trait_name,
                    kind="trait",
                    line=node.start_point[0] + 1,
                    signature=header_text(node, node.child_by_field_name("body")),
                    doc=doc,
                    attributes=attrs,
                    visibility=rust_visibility(node),
                    is_test=in_test_mod,
                )
            )
            body = node.child_by_field_name("body")
            for item in body.named_children if body else []:
                if item.type in ("function_item", "function_signature_item"):
                    out.append(
                        rust_function_symbol(
                            item,
                            f"{prefix}{trait_name}::{text(item.child_by_field_name('name'))}",
                            "trait method",
                            in_test_mod,
                        )
                    )
        elif node.type in RUST_TYPE_KINDS:
            doc, attrs = rust_doc_and_attrs(node)
            body = node.child_by_field_name("body")
            signature = header_text(node, body) if node.type != "const_item" else squash(text(node))
            out.append(
                Symbol(
                    name=prefix + text(node.child_by_field_name("name")),
                    kind=RUST_TYPE_KINDS[node.type],
                    line=node.start_point[0] + 1,
                    signature=signature[:160],
                    doc=doc,
                    attributes=attrs,
                    visibility=rust_visibility(node),
                    is_test=in_test_mod,
                )
            )
        elif node.type == "mod_item":
            body = node.child_by_field_name("body")
            if body is None:
                continue
            _, attrs = rust_doc_and_attrs(node)
            is_test_mod = in_test_mod or any("cfg(test)" in a for a in attrs)
            mod_name = text(node.child_by_field_name("name"))
            rust_walk(body, f"{prefix}{mod_name}::", is_test_mod, out)


def extract_rust(source: bytes) -> tuple[str, list[Symbol]]:
    tree = Parser(RUST).parse(source)
    module_doc_lines: list[str] = []
    for node in tree.root_node.children:
        if node.type in ("line_comment", "block_comment") and text(node).startswith(("//!", "/*!")):
            module_doc_lines.append(text(node).replace("/*!", "/**"))
        elif node.type not in ("line_comment", "block_comment"):
            break
    symbols: list[Symbol] = []
    rust_walk(tree.root_node, "", False, symbols)
    return clean_doc_lines(module_doc_lines), symbols


# ---------------------------------------------------------------------------
# TypeScript extraction
# ---------------------------------------------------------------------------

TS_TYPE_KINDS = {
    "interface_declaration": "interface",
    "type_alias_declaration": "type alias",
    "enum_declaration": "enum",
}
TS_FUNCTION_VALUES = ("arrow_function", "function_expression", "function")
TS_WRAPPER_CALLS = ("useCallback", "forwardRef", "React.forwardRef", "memo", "React.memo")


def ts_doc(node: Node) -> str:
    trivia = leading_trivia(node, ("comment",))
    doc_lines = [text(n) for n in trivia if text(n).startswith("/**")]
    lines: list[str] = []
    for chunk in doc_lines:
        lines.extend(chunk.splitlines())
    return clean_doc_lines(lines)


def ts_params(params_node: Node | None) -> list[Param]:
    params: list[Param] = []
    if params_node is None:
        return params
    for child in params_node.named_children:
        if child.type in ("required_parameter", "optional_parameter"):
            name = squash(text(child.child_by_field_name("pattern")))
            if child.type == "optional_parameter":
                name += "?"
            type_text = squash(text(child.child_by_field_name("type"))).lstrip(":").strip()
            params.append(Param(name, type_text))
    return params


def contains_jsx(node: Node) -> bool:
    stack = [node]
    while stack:
        current = stack.pop()
        if current.type in ("jsx_element", "jsx_self_closing_element", "jsx_fragment"):
            return True
        stack.extend(current.children)
    return False


def classify_ts_function(name: str, func: Node, is_tsx: bool) -> str:
    if re.match(r"^use[A-Z0-9]", name):
        return "hook"
    if name[:1].isupper() and (is_tsx or contains_jsx(func)):
        return "component"
    return "function"


def declaration_keyword(node: Node) -> str:
    first = node.children[0] if node.children else None
    return text(first) if first is not None and text(first) in ("const", "let", "var") else "const"


def unwrap_function_value(value: Node | None) -> Node | None:
    """Return the function node for `() => {}`, `useCallback(() => {})`, `forwardRef(...)`."""
    if value is None:
        return None
    if value.type in TS_FUNCTION_VALUES:
        return value
    if value.type == "call_expression" and text(value.child_by_field_name("function")) in TS_WRAPPER_CALLS:
        args = value.child_by_field_name("arguments")
        for arg in args.named_children if args else []:
            if arg.type in TS_FUNCTION_VALUES:
                return arg
    return None


def ts_function_symbol(
    name: str, kind: str, func: Node, doc_node: Node, signature_prefix: str
) -> Symbol:
    body = func.child_by_field_name("body")
    if func.type == "function_declaration":
        signature = header_text(doc_node if doc_node.type == "export_statement" else func, body)
    else:
        signature = squash(signature_prefix + header_text(func, body))
    return Symbol(
        name=name,
        kind=kind,
        line=func.start_point[0] + 1,
        signature=signature,
        params=ts_params(func.child_by_field_name("parameters")),
        returns=squash(text(func.child_by_field_name("return_type"))).lstrip(":").strip(),
        doc=ts_doc(doc_node),
    )


def find_store_actions(call: Node) -> list[tuple[str, Node]]:
    """Function-valued properties of the object literal passed to a zustand `create`."""
    actions: list[tuple[str, Node]] = []
    stack = [call]
    while stack:
        current = stack.pop()
        if current.type == "object":
            for pair in current.named_children:
                if pair.type == "pair":
                    value = pair.child_by_field_name("value")
                    if value is not None and value.type in TS_FUNCTION_VALUES:
                        actions.append((text(pair.child_by_field_name("key")), value))
                elif pair.type == "method_definition":
                    actions.append((text(pair.child_by_field_name("name")), pair))
            if actions:
                return actions
        stack.extend(reversed(current.named_children))
    return actions


def ts_inner_functions(parent_name: str, func: Node, out: list[Symbol]) -> None:
    body = func.child_by_field_name("body")
    if body is None or body.type != "statement_block":
        return
    for stmt in body.named_children:
        if stmt.type == "function_declaration":
            name = text(stmt.child_by_field_name("name"))
            out.append(
                ts_function_symbol(f"{parent_name}.{name}", "inner function", stmt, stmt, "")
            )
        elif stmt.type in ("lexical_declaration", "variable_declaration"):
            for decl in stmt.named_children:
                if decl.type != "variable_declarator":
                    continue
                inner = unwrap_function_value(decl.child_by_field_name("value"))
                if inner is None:
                    continue
                name = text(decl.child_by_field_name("name"))
                keyword = declaration_keyword(stmt)
                out.append(
                    ts_function_symbol(
                        f"{parent_name}.{name}", "inner function", inner, stmt, f"{keyword} {name} = "
                    )
                )


def ts_handle_declaration(
    node: Node, doc_node: Node, exported: str, out: list[Symbol], is_tsx: bool
) -> None:
    prefix = f"{exported} " if exported else ""
    if node.type == "function_declaration":
        name = text(node.child_by_field_name("name"))
        sym = ts_function_symbol(name, classify_ts_function(name, node, is_tsx), node, doc_node, "")
        sym.visibility = exported
        out.append(sym)
        ts_inner_functions(name, node, out)
    elif node.type in ("lexical_declaration", "variable_declaration"):
        keyword = declaration_keyword(node)
        for decl in node.named_children:
            if decl.type != "variable_declarator":
                continue
            name = text(decl.child_by_field_name("name"))
            value = decl.child_by_field_name("value")
            func = unwrap_function_value(value)
            if func is not None:
                sym = ts_function_symbol(
                    name,
                    classify_ts_function(name, func, is_tsx),
                    func,
                    doc_node,
                    f"{prefix}{keyword} {name} = ",
                )
                sym.visibility = exported
                out.append(sym)
                ts_inner_functions(name, func, out)
            elif value is not None and value.type == "call_expression" and re.match(r"^use[A-Z]", name):
                callee = text(value.child_by_field_name("function"))
                out.append(
                    Symbol(
                        name=name,
                        kind="store",
                        line=decl.start_point[0] + 1,
                        signature=squash(f"{prefix}{keyword} {name} = {callee}(...)"),
                        doc=ts_doc(doc_node),
                        visibility=exported,
                    )
                )
                for action_name, action in find_store_actions(value):
                    out.append(
                        ts_function_symbol(f"{name}.{action_name}", "store action", action, action, f"{action_name}: ")
                    )
            else:
                out.append(
                    Symbol(
                        name=name,
                        kind="const" if keyword == "const" else "variable",
                        line=decl.start_point[0] + 1,
                        signature=squash(f"{prefix}{keyword} {text(decl)}")[:160],
                        doc=ts_doc(doc_node),
                        visibility=exported,
                    )
                )
    elif node.type in TS_TYPE_KINDS:
        out.append(
            Symbol(
                name=text(node.child_by_field_name("name")),
                kind=TS_TYPE_KINDS[node.type],
                line=node.start_point[0] + 1,
                signature=squash(prefix + header_text(node, node.child_by_field_name("body")))[:160],
                doc=ts_doc(doc_node),
                visibility=exported,
            )
        )
    elif node.type == "class_declaration":
        class_name = text(node.child_by_field_name("name"))
        out.append(
            Symbol(
                name=class_name,
                kind="class",
                line=node.start_point[0] + 1,
                signature=squash(prefix + header_text(node, node.child_by_field_name("body"))),
                doc=ts_doc(doc_node),
                visibility=exported,
            )
        )
        body = node.child_by_field_name("body")
        for member in body.named_children if body else []:
            if member.type == "method_definition":
                method_name = text(member.child_by_field_name("name"))
                out.append(
                    ts_function_symbol(f"{class_name}.{method_name}", "method", member, member, "")
                )


def extract_typescript(source: bytes, is_tsx: bool) -> tuple[str, list[Symbol]]:
    tree = Parser(TSX if is_tsx else TS).parse(source)
    symbols: list[Symbol] = []
    module_doc = ""
    first = tree.root_node.named_children[0] if tree.root_node.named_children else None
    if first is not None and first.type == "comment" and text(first).startswith("/**"):
        nxt = first.next_named_sibling
        # A leading block comment separated from the next node by a blank line is a file doc.
        if nxt is None or nxt.start_point[0] > first.end_point[0] + 1:
            module_doc = clean_doc_lines(text(first).splitlines())
    default_export_names: set[str] = set()
    for node in tree.root_node.named_children:
        if node.type == "export_statement":
            decl = node.child_by_field_name("declaration")
            is_default = any(child.type == "default" for child in node.children)
            if decl is None:
                for child in node.named_children:
                    if child.type in ("function_declaration", "class_declaration"):
                        decl = child
            if decl is not None:
                ts_handle_declaration(
                    decl, node, "export default" if is_default else "export", symbols, is_tsx
                )
            elif is_default:
                value = node.child_by_field_name("value")
                if value is not None and value.type == "identifier":
                    default_export_names.add(text(value))
        else:
            ts_handle_declaration(node, node, "", symbols, is_tsx)
    for sym in symbols:
        if sym.name in default_export_names:
            sym.visibility = "export default"
    return module_doc, symbols


# ---------------------------------------------------------------------------
# Project-wide extraction: files, routes, Tauri commands
# ---------------------------------------------------------------------------


def extract_file(path: str, area: str) -> SourceFile:
    source = (PROJECT_ROOT / path).read_bytes()
    line_count = source.count(b"\n") + 1
    if path.endswith(".rs"):
        module_doc, symbols = extract_rust(source)
        language = "Rust"
    else:
        module_doc, symbols = extract_typescript(source, path.endswith(".tsx"))
        language = "TypeScript (TSX)" if path.endswith(".tsx") else "TypeScript"
    return SourceFile(path, area, language, line_count, module_doc, symbols)


ROUTE_CALL = re.compile(r"\.route\(\s*\"([^\"]+)\"\s*,", re.S)
METHOD_HANDLER = re.compile(r"\b(get|post|put|patch|delete)\((\w+)\)")


def route_access_level(path: str, router_source: str, route_pos: int) -> str:
    """Infer access level from the sub-router chain the route belongs to."""
    if path.endswith("/dev.rs") or path.endswith("dev/routes.rs"):
        return "Dev only"
    statement_end = router_source.find(";", route_pos)
    statement_start = router_source.rfind("let ", 0, route_pos)
    chain = router_source[statement_start if statement_start != -1 else 0 : statement_end]
    tail = router_source[route_pos:statement_end]
    if "require_super_admin_auth" in tail:
        return "Super admin"
    if "require_auth" in tail:
        return "Authenticated"
    if "public" in chain or "rate_limit_auth" in router_source:
        return "Public (rate limited)"
    return "Public"


def extract_routes(files: dict[str, SourceFile]) -> list[Route]:
    routes: list[Route] = []
    for path in sorted(files):
        if not path.startswith("backend/src/") or not path.endswith(".rs"):
            continue
        source = (PROJECT_ROOT / path).read_text()
        for match in ROUTE_CALL.finditer(source):
            depth, i = 1, match.end()
            while i < len(source) and depth:
                depth += {"(": 1, ")": -1}.get(source[i], 0)
                i += 1
            args = source[match.end() : i - 1]
            line = source.count("\n", 0, match.start()) + 1
            access = route_access_level(path, source, match.start())
            for method, handler in METHOD_HANDLER.findall(args):
                routes.append(Route(method.upper(), match.group(1), handler, path, line, access))
    return routes


def extract_client_endpoints() -> dict[str, list[str]]:
    """Map `<client>::<method>` in tb_client to the backend paths it calls."""
    endpoints: dict[str, list[str]] = {}
    for client_file in sorted((PROJECT_ROOT / TB_CLIENT_CLIENTS_DIR).glob("*.rs")):
        _, symbols = extract_rust(client_file.read_bytes())
        source = client_file.read_text()
        lines = source.splitlines()
        method_symbols = [s for s in symbols if s.kind == "method"]
        for idx, sym in enumerate(method_symbols):
            end = method_symbols[idx + 1].line - 1 if idx + 1 < len(method_symbols) else len(lines)
            body = "\n".join(lines[sym.line - 1 : end])
            http_methods = re.findall(r"\.http\s*\.(get|post|put|patch|delete)\(", body)
            paths = re.findall(r"join\(\s*&?(?:format!\()?\"(/[^\"]*)\"", body)
            if paths:
                verb = http_methods[0].upper() if http_methods else ""
                client = client_file.stem
                endpoints[f"{client}::{sym.name.split('::')[-1]}"] = [
                    f"{verb} {p}".strip() for p in paths
                ]
    return endpoints


def to_camel(name: str) -> str:
    head, *rest = name.split("_")
    return head + "".join(part.title() for part in rest)


def extract_tauri_commands(files: dict[str, SourceFile]) -> list[TauriCommand]:
    registry = (PROJECT_ROOT / TAURI_REGISTRY).read_text()
    match = re.search(r"generate_handler!\[(.*?)\]", registry, re.S)
    registered = [n.strip() for n in match.group(1).split(",") if n.strip()] if match else []
    generated_path = PROJECT_ROOT / TAURI_GENERATED_COMMANDS
    generated = generated_path.read_text() if generated_path.exists() else ""
    bindings = dict(
        (cmd, fn)
        for fn, cmd in re.findall(r"export async function (\w+)\([^)]*\)[^{]*\{\s*return invoke\('(\w+)'", generated)
    )
    endpoints = extract_client_endpoints()

    command_symbols: dict[str, tuple[SourceFile, Symbol]] = {}
    for source_file in files.values():
        for sym in source_file.symbols:
            if sym.kind == "tauri command":
                command_symbols[sym.name] = (source_file, sym)

    def function_bodies(source_file: SourceFile) -> dict[str, str]:
        lines = (PROJECT_ROOT / source_file.path).read_text().splitlines()
        ordered = sorted(source_file.symbols, key=lambda s: s.line)
        bodies: dict[str, str] = {}
        for idx, sym in enumerate(ordered):
            if not sym.is_function:
                continue
            end = ordered[idx + 1].line - 1 if idx + 1 < len(ordered) else len(lines)
            bodies[sym.name] = "\n".join(lines[sym.line - 1 : end])
        return bodies

    def client_calls_for(name: str, bodies: dict[str, str], seen: set[str]) -> list[str]:
        """Client calls made by a function, following calls into same-file helpers."""
        seen.add(name)
        body = bodies.get(name, "")
        calls = [f"{c}_client::{m}" for c, m in re.findall(r"\.(\w+)_client\(\)\s*\.(\w+)\(", body)]
        body_without_header = body.split("{", 1)[-1]
        for helper in re.findall(r"\b(\w+)\(", body_without_header):
            if helper in bodies and helper not in seen:
                calls.extend(client_calls_for(helper, bodies, seen))
        return calls

    def dedupe(values: list[str]) -> list[str]:
        return list(dict.fromkeys(values))

    commands: list[TauriCommand] = []
    for name in registered:
        if name not in command_symbols:
            commands.append(TauriCommand(name, bindings.get(name, ""), "", [], "", "", [], []))
            continue
        source_file, sym = command_symbols[name]
        client_calls = dedupe(client_calls_for(name, function_bodies(source_file), set()))
        cmd_endpoints = dedupe([e for call in client_calls for e in endpoints.get(call, [])])
        # Tauri exposes command arguments to JavaScript in camelCase.
        params = [
            Param(to_camel(p.name), p.type)
            for p in sym.params
            if not p.type.startswith("BackendApiState")
        ]
        commands.append(
            TauriCommand(
                name=name,
                frontend_binding=bindings.get(name, ""),
                signature=sym.signature,
                params=params,
                returns=sym.returns,
                doc=sym.doc,
                client_calls=client_calls,
                endpoints=cmd_endpoints,
            )
        )
    return commands


def git_commit() -> str:
    try:
        return (
            subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
            or "unknown"
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


# ---------------------------------------------------------------------------
# Model building
# ---------------------------------------------------------------------------


@dataclass
class DocModel:
    files: dict[str, SourceFile]
    shadcn_files: list[str]
    shadcn_exports: dict[str, list[str]]
    routes: list[Route]
    commands: list[TauriCommand]
    commit: str
    generated_at: str


def build_model() -> DocModel:
    sources, shadcn = discover_sources()
    files = {path: extract_file(path, area) for path, area in sources.items()}
    shadcn_exports: dict[str, list[str]] = {}
    for path in shadcn:
        source = (PROJECT_ROOT / path).read_text()
        export_block = re.search(r"export\s*\{([^}]*)\}", source)
        names = (
            [n.strip().split(" as ")[-1] for n in export_block.group(1).split(",") if n.strip()]
            if export_block
            else re.findall(r"export (?:default )?(?:function|const) (\w+)", source)
        )
        shadcn_exports[path] = names
    return DocModel(
        files=files,
        shadcn_files=shadcn,
        shadcn_exports=shadcn_exports,
        routes=extract_routes(files),
        commands=extract_tauri_commands(files),
        commit=git_commit(),
        generated_at=dt.datetime.now().strftime("%B %d, %Y %I:%M %p"),
    )


def write_inventory(model: DocModel, path: Path) -> None:
    inventory = {
        "files": {
            p: {
                "area": f.area,
                "language": f.language,
                "symbols": [
                    {
                        "name": s.name,
                        "kind": s.kind,
                        "line": s.line,
                        "signature": s.signature,
                        "params": [p.name for p in s.params],
                        "is_test": s.is_test,
                    }
                    for s in f.symbols
                ],
            }
            for p, f in model.files.items()
        },
        "routes": [asdict(r) for r in model.routes],
        "commands": [asdict(c) for c in model.commands],
    }
    path.write_text(json.dumps(inventory, indent=2))


# ---------------------------------------------------------------------------
# Merging hand-written descriptions
# ---------------------------------------------------------------------------


@dataclass
class SymbolDoc:
    description: str = ""
    params: dict[str, str] = field(default_factory=dict)
    returns: str = ""
    errors: list[str] = field(default_factory=list)
    notes: str = ""

    @property
    def is_empty(self) -> bool:
        return not self.description


def load_descriptions() -> dict[str, dict]:
    merged: dict[str, dict] = {}
    for module in doc_content.FILE_MODULES:
        for path, entry in getattr(module, "FILES", {}).items():
            target = merged.setdefault(path, {"summary": "", "details": "", "symbols": {}})
            for key in ("summary", "details"):
                if entry.get(key):
                    target[key] = (target[key] + "\n\n" + entry[key]).strip()
            target["symbols"].update(entry.get("symbols", {}))
    return merged


def symbol_doc(raw: object, fallback_doc: str) -> SymbolDoc:
    if isinstance(raw, str):
        return SymbolDoc(description=raw)
    if isinstance(raw, dict):
        errors = raw.get("errors", [])
        return SymbolDoc(
            description=raw.get("description", "") or fallback_doc,
            params=dict(raw.get("params", {})),
            returns=raw.get("returns", ""),
            errors=[errors] if isinstance(errors, str) else list(errors),
            notes=raw.get("notes", ""),
        )
    return SymbolDoc(description=fallback_doc)


@dataclass
class Coverage:
    undocumented_files: list[str]
    undocumented_symbols: list[tuple[str, str, str]]  # (path, name, kind)
    undescribed_types: list[tuple[str, str, str]]
    stale_symbols: list[tuple[str, str]]
    stale_files: list[str]
    undocumented_routes: list[str]
    stale_routes: list[str]

    @property
    def function_gap(self) -> int:
        return len(self.undocumented_symbols)


def route_key(route: Route) -> str:
    return f"{route.method} {route.path}"


def compute_coverage(model: DocModel, descriptions: dict[str, dict]) -> Coverage:
    undocumented_files, undocumented, undescribed_types, stale = [], [], [], []
    for path, source_file in model.files.items():
        entry = descriptions.get(path, {})
        if not entry.get("summary") and not source_file.module_doc:
            undocumented_files.append(path)
        described = entry.get("symbols", {})
        names = {s.name for s in source_file.symbols}
        for sym in source_file.symbols:
            if sym.name in described or sym.doc:
                continue
            bucket = undocumented if sym.is_function else undescribed_types
            bucket.append((path, sym.name, sym.kind))
        stale.extend((path, name) for name in described if name not in names)
    stale_files = sorted(p for p in descriptions if p not in model.files)
    keys = {route_key(r) for r in model.routes}
    return Coverage(
        undocumented_files=undocumented_files,
        undocumented_symbols=undocumented,
        undescribed_types=undescribed_types,
        stale_symbols=stale,
        stale_files=stale_files,
        undocumented_routes=sorted(k for k in keys if k not in api_content.ROUTES),
        stale_routes=sorted(k for k in api_content.ROUTES if k not in keys),
    )


def print_coverage(coverage: Coverage, verbose: bool) -> None:
    def section(title: str, items: list) -> None:
        print(f"{title}: {len(items)}")
        if verbose:
            for item in items:
                print("   ", " | ".join(item) if isinstance(item, tuple) else item)

    section("Files without a summary", coverage.undocumented_files)
    section("Undocumented functions/methods", coverage.undocumented_symbols)
    section("Types/constants without a description", coverage.undescribed_types)
    section("Stale symbol descriptions (not found in code)", coverage.stale_symbols)
    section("Stale file descriptions (file not found)", coverage.stale_files)
    section("Routes without API notes", coverage.undocumented_routes)
    section("Stale API notes (route not found)", coverage.stale_routes)


# ---------------------------------------------------------------------------
# Word document: primitives
# ---------------------------------------------------------------------------

BRAND = RGBColor(0x2E, 0x6B, 0x3A)
MUTED = RGBColor(0x5F, 0x6B, 0x63)
CODE_FONT = "Consolas"
HEADER_FILL = "DCEFD9"
CODE_FILL = "F2F4F1"
LABEL_FILL = "F2F7F0"
UNDOCUMENTED = "Undocumented."
DIAGRAM_PATH = SCRIPT_DIR / "output" / "architecture_diagram.png"


def shade(element, fill: str) -> None:
    """Apply a background fill to a paragraph/cell/style property element."""
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    element.append(shd)


def add_field(paragraph: Paragraph, instruction: str, placeholder: str = "") -> None:
    """Insert a Word field (TOC, PAGE, ...) that Word computes when the document is opened."""
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = instruction
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    run._r.extend([begin, instr, separate])
    paragraph.add_run(placeholder)
    end_run = paragraph.add_run()
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    end_run._r.append(end)


def add_rich_text(
    paragraph: Paragraph,
    value: str,
    *,
    bold: bool = False,
    italic: bool = False,
    size: float | None = None,
    color: RGBColor | None = None,
) -> None:
    """Add text, rendering `backticked` segments in the inline code style."""
    for index, segment in enumerate(re.split(r"`([^`]+)`", value)):
        if not segment:
            continue
        run = paragraph.add_run(segment)
        if index % 2 == 1:
            run.style = "Inline Code"
        run.bold = bold or None
        run.italic = italic or None
        if size:
            run.font.size = Pt(size)
        if color is not None:
            run.font.color.rgb = color


def add_paragraphs(doc: DocxDocument, value: str, style: str | None = None) -> None:
    for chunk in re.split(r"\n\s*\n", value.strip()):
        if chunk.strip():
            add_rich_text(doc.add_paragraph(style=style), squash_lines(chunk))


def squash_lines(value: str) -> str:
    return " ".join(line.strip() for line in value.splitlines() if line.strip())


def add_labeled(doc: DocxDocument, label: str, value: str) -> None:
    paragraph = doc.add_paragraph()
    paragraph.add_run(f"{label}: ").bold = True
    add_rich_text(paragraph, squash_lines(value))


def add_code(doc: DocxDocument, value: str) -> None:
    lines = value.splitlines() or [""]
    paragraph = doc.add_paragraph(style="Code Block")
    for index, line in enumerate(lines):
        if index:
            paragraph.add_run().add_break()
        paragraph.add_run(line)


def add_bullets(doc: DocxDocument, items: list[str], numbered: bool = False) -> None:
    for item in items:
        add_rich_text(doc.add_paragraph(style="List Number" if numbered else "List Bullet"), item)


def set_cell_text(cell: _Cell, value: str, *, bold: bool = False, code: bool = False) -> None:
    cell.text = ""
    paragraph = cell.paragraphs[0]
    if code:
        run = paragraph.add_run(value)
        run.style = "Inline Code"
        run.bold = bold or None
    else:
        add_rich_text(paragraph, value, bold=bold)


def add_table(
    doc: DocxDocument,
    headers: list[str],
    rows: list[list[str]],
    widths: list[float] | None = None,
    code_columns: tuple[int, ...] = (),
) -> Table:
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    for index, header in enumerate(headers):
        cell = table.rows[0].cells[index]
        set_cell_text(cell, header, bold=True)
        shade(cell._tc.get_or_add_tcPr(), HEADER_FILL)
    header_props = table.rows[0]._tr.get_or_add_trPr()
    repeat = OxmlElement("w:tblHeader")
    repeat.set(qn("w:val"), "true")
    header_props.append(repeat)
    for row in rows:
        cells = table.add_row().cells
        for index, value in enumerate(row):
            set_cell_text(cells[index], str(value), code=index in code_columns)
    if widths:
        table.autofit = False
        for index, width in enumerate(widths):
            table.columns[index].width = Inches(width)
        for row in table.rows:
            for index, width in enumerate(widths):
                row.cells[index].width = Inches(width)
    doc.add_paragraph(style="Table Spacer")
    return table


def add_key_value_table(doc: DocxDocument, rows: list[tuple[str, str]]) -> None:
    rows = [(k, v) for k, v in rows if v]
    if not rows:
        return
    table = doc.add_table(rows=0, cols=2)
    table.style = "Table Grid"
    for key, value in rows:
        cells = table.add_row().cells
        set_cell_text(cells[0], key, bold=True)
        shade(cells[0]._tc.get_or_add_tcPr(), LABEL_FILL)
        cells[1].text = ""
        chunks = [c for c in re.split(r"\n\s*\n", value.strip()) if c.strip()]
        for index, chunk in enumerate(chunks):
            paragraph = cells[1].paragraphs[0] if index == 0 else cells[1].add_paragraph()
            add_rich_text(paragraph, squash_lines(chunk))
    table.autofit = False
    table.columns[0].width, table.columns[1].width = Inches(1.4), Inches(5.1)
    for row in table.rows:
        row.cells[0].width = Inches(1.4)
        row.cells[1].width = Inches(5.1)
    doc.add_paragraph(style="Table Spacer")


def render_blocks(doc: DocxDocument, blocks: list[tuple]) -> None:
    for block in blocks:
        kind = block[0]
        if kind == "p":
            add_paragraphs(doc, block[1])
        elif kind == "bullets":
            add_bullets(doc, block[1])
        elif kind == "steps":
            add_bullets(doc, block[1], numbered=True)
        elif kind == "code":
            add_code(doc, block[1])
        elif kind == "table":
            add_table(doc, block[1], block[2])


def configure_document(doc: DocxDocument) -> None:
    section = doc.sections[0]
    section.page_width, section.page_height = Inches(8.5), Inches(11)
    for side in ("left_margin", "right_margin"):
        setattr(section, side, Inches(1))
    section.top_margin = section.bottom_margin = Inches(0.9)

    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(10.5)
    normal.paragraph_format.space_after = Pt(4)

    for level, size in ((1, 20), (2, 15), (3, 12.5), (4, 11)):
        style = styles[f"Heading {level}"]
        style.font.name = "Calibri"
        style.font.size = Pt(size)
        style.font.color.rgb = BRAND
        style.font.bold = True
        style.paragraph_format.space_before = Pt({1: 18, 2: 14, 3: 12, 4: 10}[level])
        style.paragraph_format.space_after = Pt(4)
        style.paragraph_format.keep_with_next = True
    styles["Heading 1"].paragraph_format.page_break_before = True

    code = styles.add_style("Code Block", WD_STYLE_TYPE.PARAGRAPH)
    code.base_style = normal
    code.font.name = CODE_FONT
    code.font.size = Pt(8.5)
    code.paragraph_format.space_before = Pt(2)
    code.paragraph_format.space_after = Pt(6)
    code.paragraph_format.left_indent = Inches(0.1)
    shade(code.element.get_or_add_pPr(), CODE_FILL)

    inline = styles.add_style("Inline Code", WD_STYLE_TYPE.CHARACTER)
    inline.font.name = CODE_FONT
    inline.font.size = Pt(9)
    inline.font.color.rgb = RGBColor(0x1F, 0x3B, 0x24)

    meta = styles.add_style("Meta", WD_STYLE_TYPE.PARAGRAPH)
    meta.base_style = normal
    meta.font.size = Pt(9)
    meta.font.italic = True
    meta.font.color.rgb = MUTED

    spacer = styles.add_style("Table Spacer", WD_STYLE_TYPE.PARAGRAPH)
    spacer.base_style = normal
    spacer.font.size = Pt(4)
    spacer.paragraph_format.space_after = Pt(0)

    # Ask Word to refresh fields (table of contents, page numbers) when the file is opened.
    update = OxmlElement("w:updateFields")
    update.set(qn("w:val"), "true")
    doc.settings.element.append(update)

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_rich_text(footer, f"{overview_content.TITLE} {overview_content.SUBTITLE}  |  Page ", size=8.5, color=MUTED)
    add_field(footer, "PAGE", "1")


# ---------------------------------------------------------------------------
# Word document: architecture diagram
# ---------------------------------------------------------------------------

EXTERNAL_NODES = {"openai", "gbif", "maptiler", "sqlite", "files", "keyring"}


def render_architecture_diagram(path: Path) -> Path:
    box_w, box_h, col_gap, row_gap = 1.75, 0.8, 2.35, 1.45
    centers = {
        node_id: (col * col_gap, -row * row_gap) for node_id, _, col, row in overview_content.DIAGRAM_NODES
    }
    fig, ax = plt.subplots(figsize=(11, 4.6), dpi=200)
    for node_id, label, _, _ in overview_content.DIAGRAM_NODES:
        x, y = centers[node_id]
        external = node_id in EXTERNAL_NODES
        ax.add_patch(
            FancyBboxPatch(
                (x - box_w / 2, y - box_h / 2),
                box_w,
                box_h,
                boxstyle="round,pad=0.02,rounding_size=0.12",
                facecolor="#EEF1EE" if external else "#DCEFD9",
                edgecolor="#7A857D" if external else "#2E6B3A",
                linewidth=1.3,
                linestyle="--" if external else "-",
            )
        )
        ax.text(x, y, label, ha="center", va="center", fontsize=9, color="#1F2A22")

    def edge_point(src: tuple[float, float], dst: tuple[float, float]) -> tuple[float, float]:
        dx, dy = dst[0] - src[0], dst[1] - src[1]
        scale = min(
            (box_w / 2 + 0.04) / abs(dx) if dx else float("inf"),
            (box_h / 2 + 0.04) / abs(dy) if dy else float("inf"),
        )
        return src[0] + dx * scale, src[1] + dy * scale

    for src, dst, label in overview_content.DIAGRAM_EDGES:
        start = edge_point(centers[src], centers[dst])
        end = edge_point(centers[dst], centers[src])
        ax.annotate(
            "",
            xy=end,
            xytext=start,
            arrowprops={"arrowstyle": "-|>", "color": "#3D4A40", "lw": 1.2, "shrinkA": 0, "shrinkB": 0},
        )
        if label:
            mx, my = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
            ax.text(
                mx,
                my,
                label,
                ha="center",
                va="center",
                fontsize=7.5,
                color="#2E6B3A",
                bbox={"boxstyle": "round,pad=0.15", "facecolor": "white", "edgecolor": "none"},
            )
    xs = [c[0] for c in centers.values()]
    ys = [c[1] for c in centers.values()]
    ax.set_xlim(min(xs) - box_w, max(xs) + box_w)
    ax.set_ylim(min(ys) - box_h, max(ys) + box_h)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


# ---------------------------------------------------------------------------
# Word document: chapters
# ---------------------------------------------------------------------------

SHOWN_ATTRIBUTE = re.compile(r"tauri::command|^impl |#\[(tokio::)?test|cfg\(")


def first_sentence(value: str) -> str:
    value = squash_lines(value)
    match = re.match(r"(.+?[.!?])(\s|$)", value)
    return match.group(1) if match else value


def lookup_param_doc(param_name: str, docs: dict[str, str]) -> str:
    if param_name in docs:
        return docs[param_name]
    candidates = {
        param_name.removeprefix("mut ").lstrip("&"),
        param_name.rstrip("?"),
    }
    inner = re.search(r"\((?:mut )?(\w+)\)", param_name)
    if inner:
        candidates.add(inner.group(1))
    for candidate in candidates:
        if candidate in docs:
            return docs[candidate]
    return ""


def render_symbol(doc: DocxDocument, sym: Symbol, raw: object, level: int = 4) -> None:
    sdoc = symbol_doc(raw, sym.doc)
    heading = doc.add_heading(level=level)
    heading.add_run(sym.name)
    kind_run = heading.add_run(f"   {sym.kind}")
    kind_run.font.size = Pt(9)
    kind_run.font.color.rgb = MUTED
    kind_run.bold = False

    meta_parts = [f"Line {sym.line}"]
    if sym.visibility:
        meta_parts.append(sym.visibility)
    meta_parts.extend(a for a in sym.attributes if SHOWN_ATTRIBUTE.search(a))
    doc.add_paragraph("  |  ".join(meta_parts), style="Meta")

    if sym.signature:
        add_code(doc, sym.signature)

    if sdoc.description:
        add_paragraphs(doc, sdoc.description)
    else:
        doc.add_paragraph(UNDOCUMENTED, style="Meta")
    if sym.doc and sdoc.description != sym.doc:
        add_rich_text(doc.add_paragraph(style="Meta"), "Source comment: " + squash_lines(sym.doc))

    params = [p for p in sym.params if "self" not in p.name]
    if params or sdoc.params:
        rows: list[list[str]] = []
        matched: set[str] = set()
        for param in params:
            description = lookup_param_doc(param.name, sdoc.params)
            matched.update(k for k, v in sdoc.params.items() if v == description and description)
            rows.append([param.name, param.type or "-", description or "-"])
        for name, description in sdoc.params.items():
            if name not in matched and not any(r[0] == name for r in rows):
                rows.append([name, "-", description])
        add_table(doc, ["Parameter", "Type", "Description"], rows, [1.6, 1.9, 3.0], code_columns=(0, 1))

    if sdoc.returns or sym.returns:
        paragraph = doc.add_paragraph()
        paragraph.add_run("Returns: ").bold = True
        if sym.returns:
            run = paragraph.add_run(sym.returns.lstrip("-> ").strip())
            run.style = "Inline Code"
            if sdoc.returns:
                paragraph.add_run(". ")
        if sdoc.returns:
            add_rich_text(paragraph, squash_lines(sdoc.returns))
    if sdoc.errors:
        doc.add_paragraph().add_run("Errors:").bold = True
        add_bullets(doc, sdoc.errors)
    if sdoc.notes:
        add_labeled(doc, "Notes", sdoc.notes)


def render_types_table(doc: DocxDocument, symbols: list[Symbol], described: dict) -> None:
    if not symbols:
        return
    rows = []
    for sym in symbols:
        description = symbol_doc(described.get(sym.name), sym.doc).description or "-"
        rows.append([sym.name, sym.kind, squash_lines(description)])
    doc.add_paragraph().add_run("Types and constants").bold = True
    add_table(doc, ["Name", "Kind", "Description"], rows, [1.7, 0.9, 3.9], code_columns=(0,))


def render_file(
    doc: DocxDocument,
    source_file: SourceFile,
    entry: dict,
    *,
    include_tests: bool,
    only_tests: bool = False,
    level: int = 3,
) -> None:
    doc.add_heading(source_file.path, level=level)
    doc.add_paragraph(
        f"{source_file.language}  |  {source_file.line_count} lines  |  {source_file.area}",
        style="Meta",
    )
    if not only_tests:
        summary = entry.get("summary") or source_file.module_doc
        if summary:
            add_paragraphs(doc, summary)
        else:
            doc.add_paragraph(UNDOCUMENTED, style="Meta")
        if entry.get("details"):
            add_paragraphs(doc, entry["details"])
        if source_file.module_doc and entry.get("summary"):
            add_rich_text(
                doc.add_paragraph(style="Meta"),
                "Source comment: " + squash_lines(source_file.module_doc),
            )

    described = entry.get("symbols", {})

    def wanted(sym: Symbol) -> bool:
        if only_tests:
            return sym.is_test
        return include_tests or not sym.is_test

    symbols = [s for s in source_file.symbols if wanted(s)]
    render_types_table(doc, [s for s in symbols if not s.is_function], described)
    for sym in symbols:
        if sym.is_function:
            render_symbol(doc, sym, described.get(sym.name), level=level + 1)


def render_title_page(doc: DocxDocument, model: DocModel) -> None:
    for _ in range(6):
        doc.add_paragraph()
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run(overview_content.TITLE)
    run.font.size = Pt(40)
    run.bold = True
    run.font.color.rgb = BRAND
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle.add_run(overview_content.SUBTITLE)
    run.font.size = Pt(20)
    run.font.color.rgb = MUTED
    doc.add_paragraph()
    function_count = sum(
        1 for f in model.files.values() for s in f.symbols if s.is_function and not s.is_test
    )
    test_count = sum(1 for f in model.files.values() for s in f.symbols if s.kind == "test")
    for line in (
        f"Generated {model.generated_at} from commit {model.commit}",
        f"{len(model.files)} source files  |  {function_count} functions and methods  |  "
        f"{test_count} tests",
        f"{len(model.routes)} HTTP endpoints  |  {len(model.commands)} Tauri commands",
    ):
        paragraph = doc.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_rich_text(paragraph, line, size=11, color=MUTED)
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    contents = doc.add_paragraph()
    run = contents.add_run("Contents")
    run.font.size = Pt(18)
    run.bold = True
    run.font.color.rgb = BRAND
    add_field(
        doc.add_paragraph(),
        'TOC \\o "1-3" \\h \\z \\u',
        "Right-click and choose Update Field (or press F9) to build the table of contents.",
    )


def render_introduction(doc: DocxDocument) -> None:
    doc.add_heading("1. Introduction", level=1)
    for section in overview_content.INTRODUCTION_SECTIONS:
        doc.add_heading(section["heading"], level=2)
        render_blocks(doc, section["blocks"])


def render_architecture(doc: DocxDocument, model: DocModel) -> None:
    doc.add_heading("2. Architecture Overview", level=1)
    render_blocks(doc, overview_content.ARCHITECTURE_INTRO)
    diagram = render_architecture_diagram(DIAGRAM_PATH)
    doc.add_picture(str(diagram), width=Inches(6.5))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(
        "Figure 1. Runtime components. Solid boxes are project code; dashed boxes are external "
        "services and storage.",
        style="Meta",
    ).alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_heading("Layers", level=2)
    add_table(
        doc,
        ["Layer", "Location", "Responsibility"],
        [list(row) for row in overview_content.ARCHITECTURE_LAYERS],
        [1.5, 1.6, 3.4],
        code_columns=(1,),
    )

    doc.add_heading("Source Layout", level=2)
    doc.add_paragraph("Code covered by this document, by area (counted from the source on generation):")
    rows = []
    for area in AREA_ORDER + [AREA_TESTS]:
        files = [f for f in model.files.values() if f.area == area]
        functions = sum(1 for f in files for s in f.symbols if s.is_function and (area == AREA_TESTS or not s.is_test))
        rows.append([area, str(len(files)), str(sum(f.line_count for f in files)), str(functions)])
    add_table(doc, ["Area", "Files", "Lines", "Functions"], rows, [2.5, 1.2, 1.2, 1.6])

    doc.add_heading(overview_content.REQUEST_EXAMPLE_HEADING, level=2)
    add_bullets(doc, overview_content.REQUEST_EXAMPLE_STEPS, numbered=True)


def render_setup(doc: DocxDocument) -> None:
    doc.add_heading("3. Build, Run and Test", level=1)
    for section in overview_content.SETUP_SECTIONS:
        doc.add_heading(section["heading"], level=2)
        render_blocks(doc, section["blocks"])
    doc.add_heading("Environment Variables", level=2)
    add_table(
        doc, overview_content.ENV_VARS_HEADERS, overview_content.ENV_VARS, [1.6, 1.1, 1.0, 2.8], code_columns=(0,)
    )
    doc.add_heading("Configuration Keys", level=2)
    doc.add_paragraph("Keys in backend/appsettings.ron (override with APP__<section>__<key>):")
    add_table(
        doc, overview_content.CONFIG_KEYS_HEADERS, overview_content.CONFIG_KEYS, [2.2, 1.4, 2.9], code_columns=(0,)
    )
    add_bullets(doc, overview_content.CONFIG_NOTES)


def endpoint_users(model: DocModel) -> dict[str, list[str]]:
    users: dict[str, list[str]] = {}
    for command in model.commands:
        for endpoint in command.endpoints:
            users.setdefault(endpoint, []).append(command.name)
    return users


def sorted_routes(model: DocModel) -> list[Route]:
    return sorted(model.routes, key=lambda r: (route_access(r).startswith("Dev"), r.path, r.method))


def route_access(route: Route) -> str:
    return api_content.ROUTES.get(route_key(route), {}).get("access") or route.access


def render_api(doc: DocxDocument, model: DocModel) -> None:
    doc.add_heading("4. HTTP API Reference", level=1)
    render_blocks(doc, overview_content.API_INTRO)
    routes = sorted_routes(model)

    doc.add_heading("Endpoint Summary", level=2)
    add_table(
        doc,
        ["Method", "Path", "Access", "Summary"],
        [
            [
                r.method,
                r.path,
                route_access(r),
                first_sentence(api_content.ROUTES.get(route_key(r), {}).get("summary", "")) or "-",
            ]
            for r in routes
        ],
        [0.65, 2.2, 1.55, 2.1],
        code_columns=(0, 1),
    )

    users = endpoint_users(model)
    doc.add_heading("Endpoint Details", level=2)
    for route in routes:
        notes = api_content.ROUTES.get(route_key(route), {})
        doc.add_heading(route_key(route), level=3)
        if notes.get("summary"):
            add_paragraphs(doc, notes["summary"])
        else:
            doc.add_paragraph(UNDOCUMENTED, style="Meta")
        add_key_value_table(
            doc,
            [
                ("Access", route_access(route)),
                ("Handler", f"`{route.handler}` in `{route.file}` (route defined on line {route.line})"),
                ("Request", notes.get("request", "")),
                ("Response", notes.get("response", "")),
                ("Errors", notes.get("errors", "")),
                ("Notes", notes.get("notes", "")),
                (
                    "Used by",
                    ", ".join(f"`{c}`" for c in users.get(route_key(route), []))
                    or "Not called by the Tauri app.",
                ),
            ],
        )


def find_symbol(model: DocModel, name: str, kind: str) -> tuple[SourceFile, Symbol] | None:
    for source_file in model.files.values():
        for sym in source_file.symbols:
            if sym.name == name and sym.kind == kind:
                return source_file, sym
    return None


def render_tauri_commands(doc: DocxDocument, model: DocModel, descriptions: dict[str, dict]) -> None:
    doc.add_heading("5. Tauri Command Reference", level=1)
    render_blocks(doc, overview_content.TAURI_INTRO)

    doc.add_heading("Command Summary", level=2)
    add_table(
        doc,
        ["Command", "Frontend binding", "Backend endpoint(s)"],
        [
            [c.name, c.frontend_binding or "(no binding)", ", ".join(c.endpoints) or "(none)"]
            for c in model.commands
        ],
        [1.9, 1.9, 2.7],
        code_columns=(0, 1, 2),
    )

    doc.add_heading("Command Details", level=2)
    for command in model.commands:
        doc.add_heading(command.name, level=3)
        found = find_symbol(model, command.name, "tauri command")
        raw = None
        if found:
            raw = descriptions.get(found[0].path, {}).get("symbols", {}).get(command.name)
        sdoc = symbol_doc(raw, command.doc)
        if sdoc.description:
            add_paragraphs(doc, sdoc.description)
        else:
            doc.add_paragraph(UNDOCUMENTED, style="Meta")
        if command.frontend_binding:
            args = ", ".join(p.name for p in command.params)
            call = f"await {command.frontend_binding}({{ {args} }})" if args else f"await {command.frontend_binding}()"
            add_code(doc, f"// TypeScript (src/generated/commands.ts)\n{call}")
        if command.signature:
            add_code(doc, f"// Rust\n{command.signature}")
        if command.params:
            add_table(
                doc,
                ["Argument (JS)", "Rust type", "Description"],
                [
                    [p.name, p.type, lookup_param_doc(p.name, sdoc.params) or lookup_param_doc(to_snake(p.name), sdoc.params) or "-"]
                    for p in command.params
                ],
                [1.5, 1.9, 3.1],
                code_columns=(0, 1),
            )
        add_key_value_table(
            doc,
            [
                ("Returns", (f"`{command.returns.lstrip('-> ').strip()}`. " if command.returns else "") + sdoc.returns),
                ("Errors", "\n\n".join(sdoc.errors)),
                ("tb_client calls", ", ".join(f"`{c}`" for c in command.client_calls)),
                ("Backend endpoints", ", ".join(f"`{e}`" for e in command.endpoints)),
                ("Notes", sdoc.notes),
            ],
        )


def to_snake(name: str) -> str:
    return re.sub(r"([A-Z])", lambda m: "_" + m.group(1).lower(), name)


def render_module_reference(doc: DocxDocument, model: DocModel, descriptions: dict[str, dict]) -> None:
    doc.add_heading("6. Module Reference", level=1)
    doc.add_paragraph(
        "One section per source file, grouped by area. Inline unit tests are covered in the Test "
        "Reference chapter instead."
    )
    for number, area in enumerate(AREA_ORDER, start=1):
        files = sorted((f for f in model.files.values() if f.area == area), key=lambda f: f.path)
        if not files:
            continue
        doc.add_heading(f"6.{number} {area}", level=2)
        intro = overview_content.AREA_INTROS.get(area)
        if intro:
            add_paragraphs(doc, intro)
        add_table(
            doc,
            ["File", "Purpose"],
            [
                [f.path, first_sentence(descriptions.get(f.path, {}).get("summary", "") or f.module_doc) or "-"]
                for f in files
            ],
            [2.8, 3.7],
            code_columns=(0,),
        )
        for source_file in files:
            render_file(doc, source_file, descriptions.get(source_file.path, {}), include_tests=False)


def render_tests(doc: DocxDocument, model: DocModel, descriptions: dict[str, dict]) -> None:
    doc.add_heading("7. Test Reference", level=1)
    render_blocks(doc, overview_content.TESTS_INTRO)
    for section in overview_content.SETUP_SECTIONS:
        if section["heading"] == "Running the Tests":
            doc.add_paragraph().add_run("How to run the tests").bold = True
            render_blocks(doc, section["blocks"][:1])

    suites = sorted((f for f in model.files.values() if f.area == AREA_TESTS), key=lambda f: f.path)
    all_tests = [
        (f, s) for f in model.files.values() for s in f.symbols if s.kind == "test"
    ]
    doc.add_heading("Test Index", level=2)
    add_table(
        doc,
        ["Test", "File", "Verifies"],
        [
            [
                s.name,
                f.path,
                first_sentence(
                    symbol_doc(descriptions.get(f.path, {}).get("symbols", {}).get(s.name), s.doc).description
                )
                or "-",
            ]
            for f, s in sorted(all_tests, key=lambda item: (item[0].path, item[1].line))
        ],
        [1.9, 1.7, 2.9],
        code_columns=(0, 1),
    )

    doc.add_heading("Integration Test Suites", level=2)
    for source_file in suites:
        render_file(doc, source_file, descriptions.get(source_file.path, {}), include_tests=True)

    inline = sorted(
        (f for f in model.files.values() if f.area != AREA_TESTS and any(s.is_test for s in f.symbols)),
        key=lambda f: f.path,
    )
    if inline:
        doc.add_heading("Inline Unit Tests", level=2)
        doc.add_paragraph(
            "Test modules embedded in source files (#[cfg(test)] mod tests). Run them with cargo test "
            "in the crate that owns the file."
        )
        for source_file in inline:
            render_file(
                doc, source_file, descriptions.get(source_file.path, {}), include_tests=True, only_tests=True
            )


def render_appendices(doc: DocxDocument, model: DocModel, coverage: Coverage) -> None:
    doc.add_heading("Appendix A. shadcn/ui Primitive Components", level=1)
    doc.add_paragraph(
        "These files in src/components/ui were generated by the shadcn/ui CLI. They are thin, "
        "styled wrappers around Base UI / Radix-style primitives and contain no application "
        "logic, so they are listed rather than documented function by function."
    )
    add_table(
        doc,
        ["File", "Exported components"],
        [[p, ", ".join(model.shadcn_exports.get(p, [])) or "-"] for p in model.shadcn_files],
        [2.4, 4.1],
        code_columns=(0,),
    )

    doc.add_heading("Appendix B. Documentation Coverage", level=1)
    doc.add_paragraph(
        "Generated from a comparison between the symbols found in the code and the hand-written "
        "descriptions. Items listed here exist in the code but have no description yet; run "
        "generate_external_code_doc.py --check for the same report on the command line."
    )
    total_functions = sum(1 for f in model.files.values() for s in f.symbols if s.is_function)
    add_table(
        doc,
        ["Measure", "Count"],
        [
            ["Source files", str(len(model.files))],
            ["Files without a summary", str(len(coverage.undocumented_files))],
            ["Functions, methods, components and tests", str(total_functions)],
            ["Undocumented functions", str(len(coverage.undocumented_symbols))],
            ["Types/constants without a description", str(len(coverage.undescribed_types))],
            ["HTTP routes without API notes", str(len(coverage.undocumented_routes))],
            ["Stale descriptions (no longer in code)", str(len(coverage.stale_symbols) + len(coverage.stale_files) + len(coverage.stale_routes))],
        ],
        [4.5, 2.0],
    )
    if coverage.undocumented_symbols:
        doc.add_heading("Undocumented Functions", level=2)
        add_table(
            doc,
            ["File", "Symbol", "Kind"],
            [list(item) for item in coverage.undocumented_symbols],
            [2.8, 2.6, 1.1],
            code_columns=(0, 1),
        )
    if coverage.undocumented_files:
        doc.add_heading("Files Without a Summary", level=2)
        add_bullets(doc, coverage.undocumented_files)


def write_document(
    model: DocModel, descriptions: dict[str, dict], coverage: Coverage, output: Path
) -> None:
    doc = Document()
    configure_document(doc)
    render_title_page(doc, model)
    render_introduction(doc)
    render_architecture(doc, model)
    render_setup(doc)
    render_api(doc, model)
    render_tauri_commands(doc, model, descriptions)
    render_module_reference(doc, model, descriptions)
    render_tests(doc, model, descriptions)
    render_appendices(doc, model, coverage)
    doc.core_properties.title = f"{overview_content.TITLE} {overview_content.SUBTITLE}"
    doc.core_properties.subject = "External code documentation"
    doc.save(str(output))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def filter_coverage(coverage: Coverage, prefix: str) -> Coverage:
    def keep(item: object) -> bool:
        path = item[0] if isinstance(item, tuple) else item
        return str(path).startswith(prefix)

    return Coverage(
        undocumented_files=[i for i in coverage.undocumented_files if keep(i)],
        undocumented_symbols=[i for i in coverage.undocumented_symbols if keep(i)],
        undescribed_types=[i for i in coverage.undescribed_types if keep(i)],
        stale_symbols=[i for i in coverage.stale_symbols if keep(i)],
        stale_files=[i for i in coverage.stale_files if keep(i)],
        undocumented_routes=coverage.undocumented_routes,
        stale_routes=coverage.stale_routes,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Path of the .docx to write")
    parser.add_argument("--inventory", type=Path, help="Also write a JSON inventory of extracted symbols")
    parser.add_argument("--check", action="store_true", help="Only report documentation coverage; no docx")
    parser.add_argument("--path-prefix", default="", help="Limit --check output to files under this prefix")
    args = parser.parse_args()

    model = build_model()
    descriptions = load_descriptions()
    coverage = compute_coverage(model, descriptions)

    if args.inventory:
        write_inventory(model, args.inventory)
        print(f"Inventory written to {args.inventory}")

    if args.check:
        print_coverage(filter_coverage(coverage, args.path_prefix), verbose=True)
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_document(model, descriptions, coverage, args.output)
    print(f"Documentation written to {args.output}")
    print_coverage(coverage, verbose=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
