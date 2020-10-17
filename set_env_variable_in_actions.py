from config import Config
import typer


def main(config_var: str) -> None:
    try:
        print(f"::set-output name={config_var}::{Config.__dict__[config_var]}")
    except KeyError as e:
        raise KeyError(f"Supplied a variable {e} that is not set in Config")


if __name__ == "__main__":
    typer.run(main)
