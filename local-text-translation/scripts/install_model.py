#!/usr/bin/env python3
from __future__ import annotations

import argparse
import argostranslate.package


def main() -> None:
    parser = argparse.ArgumentParser(description="Install one Argos translation model.")
    parser.add_argument("--from", dest="source", default="en")
    parser.add_argument("--to", dest="target", default="zh")
    args = parser.parse_args()
    installed = argostranslate.package.get_installed_packages()
    if any(p.from_code == args.source and p.to_code == args.target for p in installed):
        print(f"Model {args.source}->{args.target} is already installed.")
        return
    print("Updating the Argos package index (network required once)...")
    argostranslate.package.update_package_index()
    candidates = [p for p in argostranslate.package.get_available_packages()
                  if p.from_code == args.source and p.to_code == args.target]
    if not candidates:
        raise SystemExit(f"No Argos model found for {args.source}->{args.target}.")
    package = sorted(candidates, key=lambda p: p.package_version, reverse=True)[0]
    download = package.download()
    argostranslate.package.install_from_path(download)
    print(f"Installed {args.source}->{args.target} model {package.package_version}.")


if __name__ == "__main__":
    main()

