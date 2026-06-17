import shutil
from pathlib import Path


def build():
    src_dir = Path(__file__).parent.resolve()
    dist_dir = src_dir / "dist"

    # Clean existing dist directory
    if dist_dir.exists():
        try:
            shutil.rmtree(dist_dir)
        except Exception as e:
            print(f"Warning: could not clean existing dist/ directory: {e}")

    dist_dir.mkdir(parents=True, exist_ok=True)

    # Copy index.html
    html_src = src_dir / "ui" / "templates" / "index.html"
    html_dst = dist_dir / "index.html"
    shutil.copy2(html_src, html_dst)

    # Copy static assets folder (css, js, etc.)
    static_src = src_dir / "ui" / "static"
    static_dst = dist_dir / "static"
    shutil.copytree(static_src, static_dst)

    print("Static build completed successfully in ./dist/")


if __name__ == "__main__":
    build()
