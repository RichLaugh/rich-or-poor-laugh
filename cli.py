import click
from console import categories, scan_audio

@click.group()
def cli():
    """Главная группа команд для управления приложением."""
    pass

cli.add_command(categories.add_categories)
cli.add_command(scan_audio.scan_audio)

if __name__ == "__main__":
    cli()