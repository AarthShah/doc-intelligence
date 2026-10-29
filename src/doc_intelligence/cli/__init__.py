import click

@click.group()
def cli() -> None:
    """Doc Intelligence CLI for document ingestion, retrieval, and evaluation."""
    pass

from doc_intelligence.cli.evaluation import evaluate
cli.add_command(evaluate)
