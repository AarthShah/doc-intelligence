import csv
import json
import click
from doc_intelligence.evaluation import UnifiedRAGEvaluator

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

        evaluator = UnifiedRAGEvaluator(model_config=model_config, metrics=list(metrics))
        all_results = []
        for i, record in enumerate(dataset):
            click.echo(f"Evaluating record {i+1}/{len(dataset)}...")
            try:
                record_results = evaluator.evaluate([record]) # Expects a list of records
                all_results.append(record_results)
            except Exception as e:
                click.echo(f"Error evaluating record {i+1}: {e}", err=True)
                # Optionally, append an error indicator or skip this record
                all_results.append({"error": str(e), "record_index": i})

        click.echo(f"Evaluation completed successfully. Collected {len(all_results)} results.")
        # You might want to format `all_results` more nicely, e.g., save to a file
        # For now, printing a summary or the first few results for brevity.
        click.echo(f"Sample results (first 3 records): {json.dumps(all_results[:3], indent=2)}")
        # If you want to see all results, uncomment the line below
        # click.echo(f"All results: {json.dumps(all_results, indent=2)}")

    except Exception as e:
        click.echo(f"Error loading dataset or initializing evaluator: {e}", err=True)
        raise click.Abort()
