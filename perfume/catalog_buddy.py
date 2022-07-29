import click
from slack_sdk import WebClient
from datetime import date
from dotenv import dotenv_values

@click.command(name='postcat')
@click.argument('filepath', type=click.Path(exists=True))
def post_catalog_message(filepath):
    conf = dotenv_values()
    client = WebClient(token=conf['SLACK_CODE'])
    client.files_upload(channels=conf['SLACK_CHANNEL'], file=filepath, title=f'catalog_{str(date.today())}.csv', initial_comment='Hey, buddies! The catalog has been updated, have a nice day!')

if __name__ == '__main__':
    post_catalog_message()