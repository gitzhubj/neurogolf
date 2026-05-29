"""打包 ONNX 文件并通过 Kaggle API 提交"""
import sys
import json
import os
import argparse
import subprocess
import tempfile
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def setup_kaggle_credentials():
    """Create ~/.kaggle/kaggle.json from environment variables."""
    username = os.environ.get('KAGGLE_USERNAME', '')
    key = os.environ.get('KAGGLE_KEY', '')
    if not username or not key:
        return False

    kaggle_dir = Path.home() / '.kaggle'
    kaggle_dir.mkdir(parents=True, exist_ok=True)
    creds = {'username': username, 'key': key}
    with open(kaggle_dir / 'kaggle.json', 'w') as f:
        json.dump(creds, f)
    (kaggle_dir / 'kaggle.json').chmod(0o600)
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--competition', required=True)
    parser.add_argument('--registry', required=True)
    parser.add_argument('--message', default='Automated submission')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    # Set up Kaggle credentials file
    if not setup_kaggle_credentials():
        print("ERROR: KAGGLE_USERNAME and KAGGLE_KEY environment variables not set.")
        sys.exit(1)

    with open(args.registry) as f:
        registry = json.load(f)

    if not registry['tasks']:
        print("Registry is empty — nothing to submit.")
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        files_to_pack = []

        for tid, info in registry['tasks'].items():
            onnx_path = REPO_ROOT / 'onnx_export' / info['onnx_file']
            if onnx_path.exists():
                dest = tmpdir / onnx_path.name
                shutil.copy2(onnx_path, dest)
                files_to_pack.append(dest.name)

        if not files_to_pack:
            print("No ONNX files found — nothing to submit.")
            return

        zip_path = tmpdir / 'submission.zip'
        shutil.make_archive(str(zip_path.with_suffix('')), 'zip', tmpdir)

        if args.dry_run:
            print(f"[DRY RUN] competition: {args.competition}")
            print(f"[DRY RUN] files ({len(files_to_pack)}): {files_to_pack}")
            print(f"[DRY RUN] message: {args.message}")
            return

        cmd = [
            'kaggle', 'competitions', 'submit',
            '-c', args.competition,
            '-f', str(zip_path),
            '-m', args.message,
        ]
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print(f"ERROR: {result.stderr}", file=sys.stderr)
            sys.exit(1)
        print("Submission successful.")


if __name__ == '__main__':
    main()
