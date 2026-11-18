"""Compatibility entry point for the landscape RC-Free diagram."""
from export_architecture import export, resolve_drawio


def draw_pipeline():
    export("master-pipeline", resolve_drawio())


if __name__ == "__main__":
    draw_pipeline()
