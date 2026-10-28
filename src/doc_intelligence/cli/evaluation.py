import csv
import json
import click

@click.group()
def evaluate() -> None:
    """Run batch RAG evaluations on test datasets."""
    pass


@evaluate.command()
@click.option("--dataset-path", "-d", required=True, type=click.Path(exists=True, dir_okay=False), help="Path to the test dataset file.")
@click.option("--model-config", "-m", required=True, type=str, help="Model configuration name or path.")
@click.option("--metrics", "-e", multiple=True, default=["faithfulness", "answer_relevance"], help="Evaluation metrics to run.")
def run(dataset_path: str, model_config: str, metrics: tuple) -> None:
    """Run batch evaluation on a test dataset."""
    click.echo(f"Running evaluation with dataset: {dataset_path}")
    click.echo(f"Using model configuration: {model_config}")
    click.echo(f"Metrics: {', '.join(metrics)}")

    try:
        if dataset_path.endswith(".json"):
            with open(dataset_path, "r", encoding="utf-8") as f:
                dataset = json.load(f)
        elif dataset_path.endswith(".csv"):
            with open(dataset_path, "r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                dataset = list(reader)
        else:
            click.echo("Error: Unsupported dataset file format. Please provide a .json or .csv file.", err=True)
            raise click.Abort()
        click.echo(f"Successfully loaded {len(dataset)} records from {dataset_path}.")
    except Exception as e:
        click.echo(f"Error loading dataset: {e}", err=True)
        raise click.Abort()
