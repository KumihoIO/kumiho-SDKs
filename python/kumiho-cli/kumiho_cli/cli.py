"""Interactive helpers for acquiring Firebase ID tokens for Kumiho tests."""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Optional

import requests

from kumiho.auth_cli import (
    API_KEY_ENV,
    CONFIG_ENV,
    CONTROL_PLANE_API_ENV,
    ENV_FILE_ENV,
    PROJECT_ENV,
    REPO_ROOT_ENV,
    TOKEN_GRACE_ENV,
    Credentials,
    TokenAcquisitionError,
    _config_dir,
    _credentials_path,
    _default_repo_root,
    _load_credentials,
    build_parser as build_auth_parser,
    ensure_token,
)


def cmd_inspect(args: argparse.Namespace) -> None:
    try:
        import kumiho
        from kumiho.kref import Kref
    except ImportError:
        print("Error: 'kumiho' package is required for inspect command. Please install it.")
        return

    try:
        kumiho.auto_configure_from_discovery()
    except Exception as e:
        print(f"Warning: Auto-configuration failed: {e}")

    target = args.target

    if target.startswith("kref://"):
        try:
            kref = Kref(target)

            if kref.get_artifact_name():
                rev_kref_str = f"kref://{kref.get_path()}?r={kref.get_revision()}"
                revision = kumiho.get_revision(rev_kref_str)
                if not revision:
                    print(f"Revision not found: {rev_kref_str}")
                    return

                artifact = None
                for art in revision.get_artifacts():
                    if art.name == kref.get_artifact_name():
                        artifact = art
                        break

                if artifact:
                    print("Type: Artifact")
                    print(f"Kref: {target}")
                    print(f"Name: {artifact.name}")
                    print(f"Location: {artifact.location}")
                    print(f"Metadata: {artifact.metadata}")
                    print(f"Node Object: {artifact}")
                else:
                    print(
                        f"Artifact '{kref.get_artifact_name()}' not found in revision {rev_kref_str}"
                    )
                return

            if "?r=" in target or "&r=" in target:
                revision = kumiho.get_revision(target)
                if revision:
                    print("Type: Revision")
                    print(f"Kref: {revision.kref}")
                    print(f"Metadata: {revision.metadata}")
                    print(f"Node Object: {revision}")
                else:
                    print(f"Revision not found: {target}")
                return

            item = kumiho.get_item(target)
            if item:
                print("Type: Item")
                print(f"Kref: {item.kref}")
                print(f"Metadata: {item.metadata}")
                print(f"Node Object: {item}")
            else:
                print(f"Item not found: {target}")

        except Exception as e:
            print(f"Error resolving kref: {e}")

    else:
        try:
            artifacts = kumiho.get_artifacts_by_location(target)
            if not artifacts:
                print(f"No artifacts found for location: {target}")
                return

            print(f"Found {len(artifacts)} artifacts:")
            for art in artifacts:
                print(f"- {art.name} (Revision: {art.revision.kref})")
                print(f"  Metadata: {art.metadata}")
        except Exception as e:
            print(f"Error searching by location: {e}")


def cmd_whoami(args: argparse.Namespace) -> None:
    creds = _load_credentials()
    if not creds:
        print("Not logged in.")
        return

    print(f"Email: {creds.email}")
    print(f"Project ID: {creds.project_id or '<not set>'}")
    print(f"Expires At: {time.ctime(creds.expires_at)}")
    print(f"Credentials Path: {_credentials_path()}")


def cmd_config(args: argparse.Namespace) -> None:
    print("Kumiho Configuration:")
    print(f"  Config Dir: {_config_dir()}")
    print(f"  Credentials Path: {_credentials_path()}")
    print(f"  Workspace Root: {_default_repo_root()}")

    env_vars = [
        CONFIG_ENV,
        API_KEY_ENV,
        PROJECT_ENV,
        REPO_ROOT_ENV,
        ENV_FILE_ENV,
        TOKEN_GRACE_ENV,
        CONTROL_PLANE_API_ENV,
    ]

    print("\nEnvironment Variables:")
    for var in env_vars:
        val = os.getenv(var)
        if val:
            print(f"  {var}: {val}")
        else:
            print(f"  {var}: <not set>")


def cmd_search(args: argparse.Namespace) -> None:
    try:
        import kumiho
    except ImportError:
        print("Error: 'kumiho' package is required. Please install it.")
        return

    try:
        kumiho.auto_configure_from_discovery()
    except Exception as e:
        print(f"Warning: Auto-configuration failed: {e}")

    try:
        results = kumiho.item_search(
            context_filter=args.project,
            kind_filter=args.kind,
            name_filter=args.name,
        )

        if not results:
            print("No items found.")
            return

        print(f"Found {len(results)} items:")
        for item in results:
            print(f"- {item.kref} (Type: {item.type})")

    except Exception as e:
        print(f"Search failed: {e}")


def cmd_events(args: argparse.Namespace) -> None:
    try:
        import kumiho
    except ImportError:
        print("Error: 'kumiho' package is required. Please install it.")
        return

    try:
        kumiho.auto_configure_from_discovery()
    except Exception as e:
        print(f"Warning: Auto-configuration failed: {e}")

    cursor = args.cursor
    cursor_file = args.cursor_file
    if not cursor and cursor_file:
        path = Path(cursor_file)
        try:
            cursor = path.read_text(encoding="utf-8").strip() or None
        except FileNotFoundError:
            cursor = None

    try:
        caps = kumiho.get_event_capabilities()
        print(
            f"[kumiho-events] Tier={caps.tier} cursor={caps.supports_cursor} "
            f"replay={caps.supports_replay} retention_hours={caps.max_retention_hours}"
        )
    except Exception as e:
        print(f"Warning: Failed to fetch event capabilities: {e}")

    try:
        count = 0
        for event in kumiho.event_stream(
            routing_key_filter=args.routing_key_filter or "",
            kref_filter=args.kref_filter or "",
            cursor=cursor,
            from_beginning=bool(args.from_beginning),
        ):
            if args.json:
                print(
                    json.dumps(
                        {
                            "timestamp": event.timestamp,
                            "routing_key": event.routing_key,
                            "kref": event.kref.uri,
                            "author": event.author,
                            "details": event.details,
                            "cursor": event.cursor,
                        },
                        ensure_ascii=False,
                    )
                )
            else:
                ts = event.timestamp or ""
                print(f"{ts}\t{event.routing_key}\t{event.kref.uri}\tcursor={event.cursor}")

            if cursor_file and event.cursor:
                path = Path(cursor_file)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f"{event.cursor}\n", encoding="utf-8")

            count += 1
            if args.max_events and count >= args.max_events:
                break
    except KeyboardInterrupt:
        return


def cmd_tree(args: argparse.Namespace) -> None:
    try:
        import kumiho
    except ImportError:
        print("Error: 'kumiho' package is required. Please install it.")
        return

    try:
        kumiho.auto_configure_from_discovery()
    except Exception as e:
        print(f"Warning: Auto-configuration failed: {e}")

    target = args.target

    try:
        if not target:
            projects = kumiho.get_projects()
            print("Projects:")
            for p in projects:
                print(f"├── {p.name} ({p.project_id})")
            return

        project = kumiho.get_project(target)
        if project:
            print(f"Project: {project.name}")
            _print_space_tree(project.get_spaces(recursive=True))
            return

        if "/" in target:
            proj_name, space_path = target.split("/", 1)
            project = kumiho.get_project(proj_name)
            if project:
                space = project.get_space(space_path)
                if space:
                    print(f"Space: {space.path}")
                    items = space.get_items()
                    for item in items:
                        print(f"├── {item.name} ({item.type})")
                    return

        print(f"Target '{target}' not found or not supported for tree view.")

    except Exception as e:
        print(f"Tree failed: {e}")


def _print_space_tree(spaces) -> None:
    for space in spaces:
        indent = "  " * (space.path.count("/") - 1)
        print(f"{indent}├── {space.name}/")


def cmd_lineage(args: argparse.Namespace) -> None:
    try:
        import kumiho
    except ImportError:
        print("Error: 'kumiho' package is required. Please install it.")
        return

    try:
        kumiho.auto_configure_from_discovery()
    except Exception as e:
        print(f"Warning: Auto-configuration failed: {e}")

    target = args.target
    if not target.startswith("kref://"):
        print("Error: Target must be a valid kref URI.")
        return

    try:
        if "?r=" not in target:
            item = kumiho.get_item(target)
            if not item:
                print(f"Item not found: {target}")
                return
            print("Please specify a revision (e.g. ?r=1) for lineage analysis.")
            return

        revision = kumiho.get_revision(target)
        if not revision:
            print(f"Revision not found: {target}")
            return

        print(f"Lineage for: {revision.kref}")

        if args.direction in ["upstream", "both"]:
            print("\nUpstream Dependencies (Depends On):")
            deps = revision.get_all_dependencies(max_depth=args.depth)
            for kref in deps.revision_krefs:
                print(f"  <- {kref}")

        if args.direction in ["downstream", "both"]:
            print("\nDownstream Dependents (Used By):")
            deps = revision.get_all_dependents(max_depth=args.depth)
            for kref in deps.revision_krefs:
                print(f"  -> {kref}")

    except Exception as e:
        print(f"Lineage analysis failed: {e}")


def _get_subparsers(parser: argparse.ArgumentParser):
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return action
    raise RuntimeError("Failed to locate argparse subcommands")


def build_parser() -> argparse.ArgumentParser:
    parser = build_auth_parser()
    sub = _get_subparsers(parser)

    inspect = sub.add_parser("inspect", help="Inspect a Kumiho object by Kref or file path")
    inspect.add_argument("target", help="Kref URI or file path to inspect")
    inspect.set_defaults(func=cmd_inspect)

    whoami = sub.add_parser("whoami", help="Display current user and session info")
    whoami.set_defaults(func=cmd_whoami)

    config = sub.add_parser("config", help="Display configuration and environment variables")
    config.set_defaults(func=cmd_config)

    search = sub.add_parser("search", help="Search for items")
    search.add_argument("--project", help="Filter by project name")
    search.add_argument("--kind", help="Filter by item kind")
    search.add_argument("name", nargs="?", help="Filter by item name (wildcards supported)")
    search.set_defaults(func=cmd_search)

    events = sub.add_parser("events", help="Stream real-time events")
    events.add_argument("--routing-key-filter", default="", help="Routing key filter (wildcards supported)")
    events.add_argument("--kref-filter", default="", help="Kref filter (wildcards supported)")
    events.add_argument("--cursor", help="Resume from a previous event cursor")
    events.add_argument("--cursor-file", help="Read/write cursor to a file for resume support")
    events.add_argument("--from-beginning", action="store_true", help="Replay from the beginning (tier permitting)")
    events.add_argument("--max-events", type=int, default=0, help="Exit after N events (0 = run forever)")
    events.add_argument("--json", action="store_true", help="Output events as JSON lines")
    events.set_defaults(func=cmd_events)

    tree = sub.add_parser("tree", help="Visualize project or space hierarchy")
    tree.add_argument("target", nargs="?", help="Project name or space path (optional)")
    tree.set_defaults(func=cmd_tree)

    lineage = sub.add_parser("lineage", help="Analyze revision lineage")
    lineage.add_argument("target", help="Kref URI of the revision")
    lineage.add_argument("--depth", type=int, default=5, help="Traversal depth (default: 5)")
    lineage.add_argument(
        "--direction",
        choices=["upstream", "downstream", "both"],
        default="both",
        help="Direction of analysis",
    )
    lineage.set_defaults(func=cmd_lineage)

    return parser


def main(argv: Optional[list[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except TokenAcquisitionError as exc:
        parser.error(str(exc))
    except requests.HTTPError as exc:
        parser.error(f"KumihoClouds request failed: {exc}")


if __name__ == "__main__":
    main()
