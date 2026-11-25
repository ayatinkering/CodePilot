"""Tree-sitter CST extraction; static references are explicitly approximate."""

import ast
import hashlib
from importlib.metadata import version
from pathlib import Path

import tree_sitter_python
from tree_sitter import Language, Parser

BRANCHES = {
    "if_statement",
    "elif_clause",
    "for_statement",
    "while_statement",
    "except_clause",
    "case_clause",
    "conditional_expression",
    "boolean_operator",
}
BLOCKS = {
    "if_statement",
    "for_statement",
    "while_statement",
    "try_statement",
    "with_statement",
    "match_statement",
}


def walk(node, skip_definitions=False):
    stack = [node]
    while stack:
        current = stack.pop()
        yield current
        stack.extend(
            reversed(
                [
                    c
                    for c in current.named_children
                    if not (
                        skip_definitions
                        and c.type
                        in {"function_definition", "class_definition", "decorated_definition"}
                    )
                ]
            )
        )


def text(node, source):
    return source[node.start_byte : node.end_byte].decode("utf-8", errors="replace") if node else ""


def docstring(body, source):
    if body is None or not body.named_children:
        return None
    first = body.named_children[0]
    if (
        first.type == "expression_statement"
        and first.named_children
        and first.named_children[0].type == "string"
    ):
        try:
            value = ast.literal_eval(text(first.named_children[0], source))
            return value if isinstance(value, str) else None
        except (ValueError, SyntaxError):
            return None
    return None


def metrics(body, parameters):
    nodes = list(walk(body, skip_definitions=True))
    depth = 0
    for node in nodes:
        ancestors, parent = 0, node
        while parent is not None and parent.id != body.id:
            ancestors += parent.type in BLOCKS
            parent = parent.parent
        depth = max(depth, ancestors)
    return {
        "branch_heuristic": 1 + sum(n.type in BRANCHES for n in nodes),
        "nesting": depth,
        "parameters": sum(
            n.type not in {"positional_separator", "keyword_separator"}
            for n in parameters.named_children
        )
        if parameters
        else 0,
    }


def parse_source(source: bytes, path: str, base_sha: str):
    parser = Parser(Language(tree_sitter_python.language()))
    tree = parser.parse(source)
    module = path.removesuffix(".py").replace("/", ".")
    symbols, edges = [], []
    symbols.append(
        {
            "name": module,
            "kind": "module",
            "path": path,
            "start_line": 1,
            "end_line": tree.root_node.end_point.row + 1,
            "signature": "",
            "docstring": docstring(tree.root_node, source),
            "parent": None,
            "parse_error": tree.root_node.has_error,
        }
    )

    def visit(node, scope, parent_kind):
        if node.type in {"function_definition", "class_definition"}:
            name = text(node.child_by_field_name("name"), source)
            qualified = scope + "." + name
            body = node.child_by_field_name("body")
            kind = (
                "class"
                if node.type == "class_definition"
                else "method"
                if parent_kind == "class"
                else "function"
            )
            decorated = (
                node.parent if node.parent and node.parent.type == "decorated_definition" else node
            )
            signature = (
                source[node.start_byte : body.start_byte].decode("utf-8", errors="replace").rstrip()
                if body
                else text(node, source)
            )
            symbol = {
                "name": qualified,
                "kind": kind,
                "parent": scope,
                "path": path,
                "start_line": decorated.start_point.row + 1,
                "end_line": node.end_point.row + 1,
                "signature": signature,
                "docstring": docstring(body, source),
                "parse_error": node.has_error,
                "async": text(node, source).startswith("async def "),
            }
            if body and kind != "class":
                symbol["metrics"] = metrics(body, node.child_by_field_name("parameters"))
                symbol["metrics"]["lines"] = node.end_point.row - node.start_point.row + 1
            symbols.append(symbol)
            # Decorators and defaults execute in the enclosing scope, not the function body.
            for child in node.named_children:
                visit(
                    child,
                    qualified if child == body else scope,
                    kind if child == body else parent_kind,
                )
            return
        if node.type == "call":
            edges.append(
                {
                    "source": scope,
                    "target_text": text(node.child_by_field_name("function"), source),
                    "kind": "call",
                    "path": path,
                    "line": node.start_point.row + 1,
                    "target": None,
                    "resolution": "unresolved",
                }
            )
        if node.type in {"import_statement", "import_from_statement"}:
            edges.append(
                {
                    "source": scope,
                    "target_text": text(node, source),
                    "kind": "import",
                    "path": path,
                    "line": node.start_point.row + 1,
                    "target": None,
                    "resolution": "unresolved",
                }
            )
        for child in node.named_children:
            visit(child, scope, parent_kind)

    visit(tree.root_node, module, "module")
    names = {s["name"] for s in symbols}
    for edge in edges:
        if edge["kind"] == "call" and edge["target_text"].isidentifier():
            scope = edge["source"]
            while scope:
                candidate = scope + "." + edge["target_text"]
                if candidate in names:
                    edge.update(target=candidate, resolution="heuristic")
                    break
                scope = scope.rpartition(".")[0]
    return {
        "path": path,
        "base_sha": base_sha,
        "sha256": hashlib.sha256(source).hexdigest(),
        "parser": {"binding": version("tree-sitter"), "grammar": version("tree-sitter-python")},
        "parse_error": tree.root_node.has_error,
        "symbols": symbols,
        "edges": edges,
    }


def index_snapshot(root: Path, manifest: dict):
    files = []
    for entry in manifest["files"]:
        path = entry["path"]
        if not path.endswith(".py"):
            continue
        target = root / path
        if not target.resolve().is_relative_to(root.resolve()) or target.is_symlink():
            raise ValueError("Snapshot path escape")
        source = target.read_bytes()
        if hashlib.sha256(source).hexdigest() != entry["sha256"]:
            raise ValueError("Snapshot changed since acquisition")
        files.append(parse_source(source, path, manifest["base_sha"]))
    return {"base_sha": manifest["base_sha"], "files": files}


def findings(index, thresholds=None):
    limits = thresholds or {"lines": 40, "nesting": 3, "parameters": 5, "branch_heuristic": 8}
    return [
        {
            "symbol": symbol["name"],
            "path": symbol["path"],
            "start_line": symbol["start_line"],
            "end_line": symbol["end_line"],
            "metric": key,
            "value": value,
            "threshold": limits[key],
        }
        for file in index["files"]
        for symbol in file["symbols"]
        for key, value in symbol.get("metrics", {}).items()
        if key in limits and value > limits[key]
    ]
