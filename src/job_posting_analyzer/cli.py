"""Terminal commands; help and offline commands never initialize an API client."""

import argparse
import json
import sys
from pathlib import Path

from .errors import InputError, OutputError, ProviderError, ResponseError
from .inputs import preflight_output, read_job, read_profile
from .report import render_report, terminal_text, write_report


def protect_input_paths(output, inputs):
    target = Path(output)
    try:
        for source in (Path(value) for value in inputs if value is not None):
            if target.resolve() == source.resolve() or (
                target.exists() and target.samefile(source)
            ):
                raise OutputError("Output destination must not replace an input file.")
    except (OSError, ValueError):
        raise OutputError("Output destination could not be checked against input files.") from None


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(
        prog="job-analyzer", description="Evidence-backed job advertisement analysis."
    )
    commands = command.add_subparsers(dest="command", required=True)
    analyze = commands.add_parser("analyze", help="Analyze a local UTF-8 job advertisement.")
    analyze.add_argument("job")
    analyze.add_argument("--profile")
    analyze.add_argument("--json", dest="output")
    analyze.add_argument("--overwrite", action="store_true")
    demo = commands.add_parser("demo", help="Run the clearly labeled simulated offline example.")
    demo.add_argument("--json", dest="output")
    demo.add_argument("--overwrite", action="store_true")
    evaluate = commands.add_parser(
        "evaluate", help="Compare extraction prompts on fictional cases."
    )
    mode = evaluate.add_mutually_exclusive_group(required=True)
    mode.add_argument("--offline", action="store_true")
    mode.add_argument("--live", action="store_true")
    evaluate.add_argument("--split", choices=["validation", "holdout", "all"], default="all")
    evaluate.add_argument("--max-requests", type=int, default=12)
    serve = commands.add_parser("serve", help="Open the loopback-only browser workspace.")
    serve.add_argument("--port", type=local_port, default=8000)
    return command


def local_port(value):
    try:
        port = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("Port must be between 1 and 65535.") from None
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError("Port must be between 1 and 65535.")
    return port


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure") and not stream.isatty():
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
    args = parser().parse_args(argv)
    try:
        if args.command == "serve":
            from .web import serve

            serve(port=args.port)
            return 0
        if getattr(args, "output", None):
            preflight_output(args.output, overwrite=args.overwrite)
        if args.command == "demo":
            from .demo import run_demo

            report = run_demo()
        elif args.command == "analyze":
            text = read_job(args.job)
            profile = read_profile(args.profile) if args.profile else None
            if args.output:
                protect_input_paths(args.output, [args.job, args.profile])
            from .analysis import analyze

            report = analyze(text, profile=profile)
        else:
            from .evaluation import run_evaluation

            result = run_evaluation(
                live=args.live, split=args.split, max_requests=args.max_requests
            )
            print(json.dumps(result, indent=2))
            return 0
        if args.output:
            if args.command == "analyze":
                protect_input_paths(args.output, [args.job, args.profile])
            write_report(report, args.output, overwrite=args.overwrite)
        print(render_report(report))
    except (InputError, ProviderError, ResponseError, OutputError) as error:
        codes = {InputError: 2, ProviderError: 3, ResponseError: 4, OutputError: 5}
        print(f"Error: {terminal_text(str(error))}", file=sys.stderr)
        return codes[type(error)]
    return 0
