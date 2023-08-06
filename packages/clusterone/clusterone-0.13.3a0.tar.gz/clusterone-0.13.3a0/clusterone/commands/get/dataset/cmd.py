import click

from clusterone import authenticate
from clusterone.utilities import path_to_dataset, make_table


HEADER = ['Property', 'Value']

HEADER_BASE = [
    'Name',
    'Id',
    'Source',
    'URL'
]

def extract_data_from_dataset(dataset):
    extracted_data = [
        dataset['name'],
        dataset['id'],
        dataset['source'],
        dataset['http_url_to_repo'],
    ]

    key_value_pairs = zip(HEADER_BASE, extracted_data)

    return [pair for pair in key_value_pairs]

@click.command()
@click.pass_obj
@authenticate()
@click.argument(
    'dataset_path',
    )
def command(context, dataset_path):
    """
    Get information about a dataset
    """

    dataset = path_to_dataset(dataset_path, context=context)
    dataset_data = extract_data_from_dataset(dataset)
    click.echo(make_table(dataset_data, header=HEADER))

    return dataset
