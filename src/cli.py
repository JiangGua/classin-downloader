import re
import click

import bbparser

@click.group()
def cli():
    pass

@cli.command()
def bb():
    bbparser.download_all_videos_from_bb_txt()

@cli.command()
@click.argument('path')
def txt(path):
    bbparser.get_bb_videos(path)

@cli.command()
@click.argument('url')
def classin(url):
    classin_re = re.compile(r'(?<=https:\/\/www\.eeo\.cn\/live\.php\?lessonKey\=)[0-9a-zA-Z]+')
    keys = classin_re.findall(url)
    if not keys:
        key = url
    else:
        key = keys[0]
    bbparser.get_classin_video(key)

if __name__ == "__main__":
    cli()