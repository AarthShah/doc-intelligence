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
@click.option("--output-path", "-o", type=click.Path(dir_okay=False), help="Path to save the evaluation results (JSON or CSV).")
def run(dataset_path: str, model_config: str, metrics: tuple, output_path: str = None) -> None:
    """Run batch evaluation on a test dataset."""
    click.echo(f"Running evaluation with dataset: {dataset_path}")
    click.echo(f"Using model configuration: {model_config}")
    click.echo(f"Metrics: {', '.join(metrics)}")

    all_results = [] # Initialize all_results here

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
        
        for i, record in enumerate(dataset):
            click.echo(f"Evaluating record {i+1}/{len(dataset)}...")
            try:
                # Ensure that each record is a dict, if not, wrap it
                if not isinstance(record, dict):
                    record = {"content": record} # Assuming 'content' is a common key, adjust if needed

                record_results = evaluator.evaluate([record]) # Expects a list of records
                # The result from evaluator.evaluate might be a list if multiple records are processed,
                # or a single dict if only one was passed. Assuming it returns a list of dicts.
                if isinstance(record_results, list):
                    all_results.extend(record_results)
                else:
                    all_results.append(record_results) # Append if it's a single dict

            except Exception as e:
                click.echo(f"Error evaluating record {i+1}: {e}", err=True)
                all_results.append({"error": str(e), "record_index": i})

        click.echo(f"Evaluation completed successfully. Collected {len(all_results)} results.")

        # Calculate and display aggregated results
        if all_results:
            valid_results = [res for res in all_results if isinstance(res, dict) and "error" not in res]
            if valid_results:
                metrics_to_aggregate = set()
                for res in valid_results:
                    metrics_to_aggregate.update(res.keys())

                aggregated_scores = {metric: [] for metric in metrics_to_aggregate}
                for res in valid_results:
                    for metric, value in res.items():
                        if isinstance(value, (int, float)):
                            aggregated_scores[metric].append(value)

                summary = {}
                for metric, scores in aggregated_scores.items():
                    if scores:
                        summary[metric] = {
                            "average": sum(scores) / len(scores),
                            "min": min(scores),
                            "max": max(scores),
                            "count": len(scores)
                        }
                    else:
                        summary[metric] = "No scores available"
                
                click.echo("\n--- Aggregated Evaluation Results ---")
                click.echo(json.dumps(summary, indent=2))
                click.echo("-------------------------------------")

            error_records = [res for res in all_results if isinstance(res, dict) and "error" in res]
            if error_records:
                click.echo(f"\nEncountered errors in {len(error_records)} records:")
                for error_record in error_records:
                    click.echo(f"  Record {error_record.get('record_index', 'N/A')}: {error_record['error']}")
        
        # Handle saving results to a file
        if output_path:
            try:
                if output_path.endswith(".json"):
                    with open(output_path, "w", encoding="utf-8") as f:
                        json.dump(all_results, f, indent=2)
                elif output_path.endswith(".csv"):
                    if not all_results:
                         click.echo("No results to save to CSV.")
                         return

                    headers = None
                    flat_data = []
                    for record in all_results:
                        if isinstance(record, dict) and "error" not in record:
                            if headers is None:
                                headers = list(record.keys())
                            row = {h: record.get(h, None) for h in headers}
                            flat_data.append(row)
                        elif isinstance(record, dict) and "error" in record:
                            error_row = {"error": record["error"], "record_index": record.get("record_index", "N/A")}
                            if headers is None: # If only errors, use error keys
                                headers = list(error_row.keys())
                            else: # Ensure error row has all headers, filling missing with None
                                for h in headers:
                                    error_row.setdefault(h, None)
                            flat_data.append(error_row)
                    
                    if headers:
                        with open(output_path, "w", encoding="utf-8", newline="") as f:
                            writer = csv.DictWriter(f, fieldnames=headers)
                            writer.writeheader()
                            writer.writerows(flat_data)
                    else:
                        click.echo("Could not determine CSV headers.")
                else:
                    click.echo(f"Unsupported output file format for {output_path}. Please use .json or .csv.", err=True)
                    
                click.echo(f"Results saved to {output_path}")
            except Exception as e:
                click.echo(f"Error saving results to {output_path}: {e}", err=True)
        else:
            # Original behavior if no output path is specified
            if all_results:
                click.echo(f"Sample results (first 3 records): {json.dumps(all_results[:3], indent=2)}")
            else:
                click.echo("No results to display.")

    except Exception as e:
        click.echo(f"Error during evaluation process: {e}", err=True)
        raise click.Abort()
