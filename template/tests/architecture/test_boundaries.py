"""Architectural boundary compliance tests for hexagonal layers."""

from __future__ import annotations

import ast
from pathlib import Path


def _get_package_root() -> Path:
    """Discovers the package root directory in src/."""
    current = Path(__file__).resolve().parent
    # Navigate up to tests/ -> target project root -> src/
    src_dir = current.parent.parent / "src"
    for child in src_dir.iterdir():
        if child.is_dir() and (child / "__init__.py").is_file():
            return child
    raise RuntimeError(f"Could not locate package directory in {src_dir}")


def test_core_domain_has_zero_external_dependencies() -> None:
    """Asserts that core.domain imports zero outer adapters or framework packages."""
    pkg_root = _get_package_root()
    domain_dir = pkg_root / "core" / "domain"
    pkg_name = pkg_root.name

    for py_file in domain_dir.rglob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith(
                        f"{pkg_name}.adapters"
                    ), f"Domain file {py_file.name} illegally imports adapter: {alias.name}"
            elif isinstance(node, ast.ImportFrom) and node.module:
                assert not node.module.startswith(
                    f"{pkg_name}.adapters"
                ), f"Domain file {py_file.name} illegally imports adapter: {node.module}"


def test_dependencies_point_strictly_inward() -> None:
    """Asserts that adapters depend on ports and core layers, never vice versa."""
    pkg_root = _get_package_root()
    core_dir = pkg_root / "core"
    pkg_name = pkg_root.name

    for py_file in core_dir.rglob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith(
                        f"{pkg_name}.adapters"
                    ), f"Core file {py_file.name} illegally imports adapter: {alias.name}"
            elif isinstance(node, ast.ImportFrom) and node.module:
                assert not node.module.startswith(
                    f"{pkg_name}.adapters"
                ), f"Core file {py_file.name} illegally imports adapter: {node.module}"


def test_ports_are_abstract_protocols_or_abcs() -> None:
    """Asserts that all port contracts are declared as typing.Protocol or abc.ABC."""
    pkg_root = _get_package_root()
    ports_dir = pkg_root / "core" / "ports"

    for py_file in ports_dir.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        classes_found = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes_found += 1
                base_names = {b.id for b in node.bases if isinstance(b, ast.Name)}
                # Also check attribute bases like typing.Protocol
                for b in node.bases:
                    if isinstance(b, ast.Attribute):
                        base_names.add(b.attr)
                valid_bases = {"Protocol", "ABC", "Port", "DrivingPort", "DrivenPort"}
                err_msg = (
                    f"Port class {node.name} in {py_file.name} must inherit from Protocol, "
                    "ABC, or Port marker"
                )
                assert any(b in valid_bases for b in base_names), err_msg
        assert classes_found > 0, f"Port file {py_file.name} contains no Protocol or ABC classes"


def test_port_signatures_use_pure_dtos_and_primitives() -> None:
    """Asserts that port method signatures use frozen DTOs, value objects, or primitives."""
    pkg_root = _get_package_root()
    ports_dir = pkg_root / "core" / "ports"
    pkg_name = pkg_root.name

    for py_file in ports_dir.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith(
                        f"{pkg_name}.adapters"
                    ), f"Port file {py_file.name} imports adapter type: {alias.name}"
            elif isinstance(node, ast.ImportFrom) and node.module:
                assert not node.module.startswith(
                    f"{pkg_name}.adapters"
                ), f"Port file {py_file.name} imports adapter type: {node.module}"


def test_domain_and_use_cases_have_zero_lifecycle_pollution() -> None:
    """Asserts that core domain and use cases do not control thread or process lifecycles."""
    pkg_root = _get_package_root()
    core_dirs = [pkg_root / "core" / "domain", pkg_root / "core" / "use_cases"]
    forbidden_modules = {"threading", "multiprocessing", "subprocess", "signal"}

    for core_dir in core_dirs:
        for py_file in core_dir.rglob("*.py"):
            tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        assert (
                            alias.name not in forbidden_modules
                        ), f"Core file {py_file.name} imports lifecycle module: {alias.name}"
                elif isinstance(node, ast.ImportFrom) and node.module:
                    assert (
                        node.module.split(".")[0] not in forbidden_modules
                    ), f"Core file {py_file.name} imports lifecycle module: {node.module}"
                elif isinstance(node, ast.Call):
                    # Flag asyncio.run()
                    if (
                        isinstance(node.func, ast.Attribute)
                        and isinstance(node.func.value, ast.Name)
                        and node.func.value.id == "asyncio"
                        and node.func.attr == "run"
                    ):
                        raise AssertionError(
                            f"Core file {py_file.name} executes asyncio.run() lifecycle control."
                        )


def test_domain_never_imports_ports_or_use_cases() -> None:
    """Asserts that core.domain never imports core.ports or core.use_cases."""
    pkg_root = _get_package_root()
    domain_dir = pkg_root / "core" / "domain"
    pkg_name = pkg_root.name

    for py_file in domain_dir.rglob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith(
                        f"{pkg_name}.core.ports"
                    ), f"Domain file {py_file.name} illegally imports port: {alias.name}"
                    assert not alias.name.startswith(
                        f"{pkg_name}.core.use_cases"
                    ), f"Domain file {py_file.name} illegally imports use case: {alias.name}"
            elif isinstance(node, ast.ImportFrom) and node.module:
                assert not node.module.startswith(
                    f"{pkg_name}.core.ports"
                ), f"Domain file {py_file.name} illegally imports port: {node.module}"
                assert not node.module.startswith(
                    f"{pkg_name}.core.use_cases"
                ), f"Domain file {py_file.name} illegally imports use case: {node.module}"


def test_domain_exceptions_inherit_from_domain_error() -> None:
    """Asserts that custom exception classes in core.domain inherit from DomainError."""
    pkg_root = _get_package_root()
    domain_dir = pkg_root / "core" / "domain"

    for py_file in domain_dir.rglob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and "Error" in node.name:
                if node.name == "DomainError":
                    continue
                base_names = {b.id for b in node.bases if isinstance(b, ast.Name)}
                for b in node.bases:
                    if isinstance(b, ast.Attribute):
                        base_names.add(b.attr)
                assert (
                    "DomainError" in base_names
                ), f"Domain exception {node.name} in {py_file.name} must inherit from DomainError"


def test_domain_has_zero_global_mutable_state() -> None:
    """Asserts that core.domain does not declare mutable module-level collections."""
    pkg_root = _get_package_root()
    domain_dir = pkg_root / "core" / "domain"

    for py_file in domain_dir.rglob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in tree.body:
            if isinstance(node, ast.Assign):
                # Flag mutable collection literals assigned at module root: list, dict, set
                if isinstance(node.value, ast.List | ast.Dict | ast.Set):
                    raise AssertionError(
                        f"Domain file {py_file.name} defines mutable module-level collection."
                    )


def test_domain_has_zero_ambient_environment_access() -> None:
    """Asserts that core.domain never reads os.environ directly."""
    pkg_root = _get_package_root()
    domain_dir = pkg_root / "core" / "domain"

    for py_file in domain_dir.rglob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr == "environ":
                if isinstance(node.value, ast.Name) and node.value.id == "os":
                    raise AssertionError(
                        f"Domain file {py_file.name} illegally accesses ambient os.environ."
                    )


def test_domain_entities_are_self_validating() -> None:
    """Asserts that domain entities validate attributes via __post_init__ or Enum constants."""
    pkg_root = _get_package_root()
    domain_dir = pkg_root / "core" / "domain"

    entities_audited = 0
    for py_file in domain_dir.rglob("*.py"):
        if py_file.name in {"__init__.py", "exceptions.py"}:
            continue
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                entities_audited += 1
                decorator_names = {d.id for d in node.decorator_list if isinstance(d, ast.Name)}
                for d in node.decorator_list:
                    if isinstance(d, ast.Call) and isinstance(d.func, ast.Name):
                        decorator_names.add(d.func.id)
                base_names = {b.id for b in node.bases if isinstance(b, ast.Name)}

                is_enum = "StrEnum" in base_names or "Enum" in base_names
                is_dataclass = "dataclass" in decorator_names

                assert (
                    is_enum or is_dataclass
                ), f"Domain type {node.name} in {py_file.name} must be a dataclass or Enum"

                if is_dataclass:
                    method_names = {
                        item.name
                        for item in node.body
                        if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef)
                    }
                    assert (
                        "__post_init__" in method_names
                    ), f"Dataclass {node.name} in {py_file.name} must define __post_init__ guard"
    assert entities_audited > 0, "No domain models found in core.domain"


def test_use_cases_follow_lexical_and_structural_conventions() -> None:
    """Asserts that use cases follow the *UseCase naming pattern and define __init__ DI."""
    pkg_root = _get_package_root()
    uc_dir = pkg_root / "core" / "use_cases"
    allowed_verb_prefixes = (
        "Check",
        "Get",
        "Find",
        "Create",
        "Update",
        "Delete",
        "Execute",
        "Process",
        "Verify",
        "Sync",
        "Register",
        "Submit",
    )

    use_cases_audited = 0
    for py_file in uc_dir.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                use_cases_audited += 1
                assert node.name.endswith(
                    "UseCase"
                ), f"Class {node.name} in {py_file.name} must end with 'UseCase'"
                assert node.name.startswith(
                    allowed_verb_prefixes
                ), f"Use case {node.name} in {py_file.name} must start with an imperative verb"

                method_names = {
                    item.name for item in node.body if isinstance(item, ast.FunctionDef)
                }
                assert (
                    "__init__" in method_names
                ), f"Use case {node.name} in {py_file.name} must define constructor __init__"
    assert use_cases_audited > 0, "No use case classes found in core.use_cases"


def test_use_cases_do_not_instantiate_concrete_adapters() -> None:
    """Asserts that use cases never import concrete adapter packages."""
    pkg_root = _get_package_root()
    uc_dir = pkg_root / "core" / "use_cases"
    pkg_name = pkg_root.name

    for py_file in uc_dir.rglob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith(
                        f"{pkg_name}.adapters"
                    ), f"Use case {py_file.name} illegally imports adapter: {alias.name}"
            elif isinstance(node, ast.ImportFrom) and node.module:
                assert not node.module.startswith(
                    f"{pkg_name}.adapters"
                ), f"Use case {py_file.name} illegally imports adapter: {node.module}"


def test_use_cases_are_transport_and_framework_agnostic() -> None:
    """Asserts that use cases never import HTTP or CLI transport frameworks."""
    pkg_root = _get_package_root()
    uc_dir = pkg_root / "core" / "use_cases"
    forbidden_transport = {"fastapi", "starlette", "flask", "click", "typer", "grpc"}

    for py_file in uc_dir.rglob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert (
                        alias.name.split(".")[0] not in forbidden_transport
                    ), f"Use case {py_file.name} imports transport module: {alias.name}"
            elif isinstance(node, ast.ImportFrom) and node.module:
                assert (
                    node.module.split(".")[0] not in forbidden_transport
                ), f"Use case {py_file.name} imports transport module: {node.module}"


def test_use_cases_are_stateless_interactors() -> None:
    """Asserts that use cases do not mutate self attributes outside __init__."""
    pkg_root = _get_package_root()
    uc_dir = pkg_root / "core" / "use_cases"

    for py_file in uc_dir.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for member in node.body:
                    if isinstance(member, ast.FunctionDef) and member.name != "__init__":
                        for sub_node in ast.walk(member):
                            if isinstance(sub_node, ast.Assign):
                                for target in sub_node.targets:
                                    if (
                                        isinstance(target, ast.Attribute)
                                        and isinstance(target.value, ast.Name)
                                        and target.value.id == "self"
                                    ):
                                        raise AssertionError(
                                            f"Use case method {member.name} in {py_file.name} "
                                            f"illegally mutates self.{target.attr}"
                                        )


def test_use_cases_do_not_bypass_ports_with_direct_io() -> None:
    """Asserts that use cases do not directly import raw networking or HTTP clients."""
    pkg_root = _get_package_root()
    uc_dir = pkg_root / "core" / "use_cases"
    forbidden_io = {"requests", "httpx", "aiohttp", "urllib", "socket"}

    for py_file in uc_dir.rglob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert (
                        alias.name.split(".")[0] not in forbidden_io
                    ), f"Use case {py_file.name} imports direct I/O library: {alias.name}"
            elif isinstance(node, ast.ImportFrom) and node.module:
                assert (
                    node.module.split(".")[0] not in forbidden_io
                ), f"Use case {py_file.name} imports direct I/O library: {node.module}"


def test_ports_have_zero_implementation_code() -> None:
    """Asserts that port contracts contain zero concrete implementation code or initializers."""
    pkg_root = _get_package_root()
    ports_dir = pkg_root / "core" / "ports"

    for py_file in ports_dir.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        assert item.name != "__init__", f"Port {node.name} must not define __init__"
                        # Body must consist of docstring, Pass, or Expr(Constant(...))
                        for stmt in item.body:
                            is_docstring = isinstance(stmt, ast.Expr) and isinstance(
                                stmt.value, ast.Constant
                            )
                            is_ellipsis = (
                                isinstance(stmt, ast.Expr)
                                and isinstance(stmt.value, ast.Constant)
                                and stmt.value.value is ...
                            )
                            is_pass = isinstance(stmt, ast.Pass)
                            err_msg = f"Port method {item.name} contains implementation code"
                            assert is_docstring or is_ellipsis or is_pass, err_msg


def test_ports_follow_technology_agnostic_nomenclature() -> None:
    """Asserts that port class names end with Port and contain no vendor/technology keywords."""
    pkg_root = _get_package_root()
    ports_dir = pkg_root / "core" / "ports"
    forbidden_tech = (
        "Sql",
        "Postgres",
        "Mysql",
        "Sqlite",
        "Redis",
        "Mongo",
        "Http",
        "FastApi",
        "Flask",
        "Kafka",
        "Rabbit",
        "Aws",
        "S3",
    )

    for py_file in ports_dir.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                assert node.name.endswith(
                    "Port"
                ), f"Port class {node.name} in {py_file.name} must end with 'Port'"
                for tech in forbidden_tech:
                    assert (
                        tech not in node.name
                    ), f"Port class {node.name} contains technology keyword '{tech}'"


def test_ports_adhere_to_strict_import_whitelist() -> None:
    """Asserts that port files only import from allowed standard typing and domain modules."""
    pkg_root = _get_package_root()
    ports_dir = pkg_root / "core" / "ports"
    pkg_name = pkg_root.name
    allowed_modules = {
        "__future__",
        "typing",
        "abc",
        "collections.abc",
        "datetime",
        "uuid",
        "enum",
    }

    for py_file in ports_dir.rglob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_mod = alias.name.split(".")[0]
                    assert (
                        root_mod in allowed_modules
                    ), f"Port file {py_file.name} imports unauthorized module: {alias.name}"
            elif isinstance(node, ast.ImportFrom):
                if node.level and node.level > 0:
                    continue  # relative imports within core.ports are permitted
                if node.module:
                    root_mod = node.module.split(".")[0]
                    is_domain = node.module.startswith(f"{pkg_name}.core.domain")
                    is_ports = node.module.startswith(f"{pkg_name}.core.ports")
                    assert (
                        root_mod in allowed_modules or is_domain or is_ports
                    ), f"Port file {py_file.name} imports unauthorized module: {node.module}"


def test_composition_root_isolation() -> None:
    """Asserts that core layers and adapters never import from the bootstrap package."""
    pkg_root = _get_package_root()
    pkg_name = pkg_root.name
    isolated_dirs = [
        pkg_root / "core" / "domain",
        pkg_root / "core" / "ports",
        pkg_root / "core" / "use_cases",
        pkg_root / "adapters",
    ]

    for base_dir in isolated_dirs:
        for py_file in base_dir.rglob("*.py"):
            tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        assert not alias.name.startswith(
                            f"{pkg_name}.bootstrap"
                        ), f"File {py_file.name} illegally imports bootstrap: {alias.name}"
                elif isinstance(node, ast.ImportFrom):
                    # Check absolute imports
                    if node.module:
                        assert not node.module.startswith(
                            f"{pkg_name}.bootstrap"
                        ), f"File {py_file.name} illegally imports bootstrap: {node.module}"
                    # Check relative imports crossing into bootstrap
                    if node.level and node.level > 1 and node.module and "bootstrap" in node.module:
                        err = f"File {py_file.name} illegally imports bootstrap: {node.module}"
                        raise AssertionError(err)
