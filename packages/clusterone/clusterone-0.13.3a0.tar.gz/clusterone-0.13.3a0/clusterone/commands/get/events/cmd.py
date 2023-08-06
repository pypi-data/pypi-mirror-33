from time import sleep

import click
from click import echo, clear
from clusterone import authenticate
from clusterone.utilities import make_table
from clusterone.client_exceptions import SoftInternalServiceError


HEADER = ['Time', 'Job', 'Job Run ID', 'Status', 'Event']

@click.command()
@click.option(
    '--once',
    is_flag=True,
    help='Display snapshot of latest events.'
    )
@click.pass_obj
@authenticate()
def command(context, once):
    """
    Outputs a contionus stream of events. Press CTRL+C to exit.
    """

    session, client = context.session, context.client

    if once:
        output_events(client)
    else:
        while True:
            output_events(client, before_printing=clear)
            sleep(session.events_refresh_rate)


#TODO: Python2.7 compliance legacy - add * after last positional argument
def output_events(client, before_printing=None):
    """
    Lists events from the system on the stdout
    Before printing action is performed.

    The before_printing action was added as a way to perform
    event aquisition (as it may throw) before clearing the screen
    and therefore not interacting with exception handler
    """

    events_data = extract_data_from_events(client.get_events())

    #TODO: Find the origin of the problem - suspected culprits API returning empty event list - tried to reporoduce - failed. Possible reproduction guidlines: have a valid token, but invalid session.
    try:
        assert events_data
    except AssertionError as exception:
        raise SoftInternalServiceError

    if before_printing:
        before_printing()

    echo(make_table(events_data, header=HEADER))


def extract_data_from_events(events):
    """
    Transform events data into table displayable data
    """

    def get_event_data(event):
        """
        Aquire relevant data from single event
        """

        return [
            event['created_at'][:19],
            event['job_name'],
            event['job_run'],
            event['event_level_display'],
            event['event_type_display'],
        ]

    return [get_event_data(event) for event in events]
