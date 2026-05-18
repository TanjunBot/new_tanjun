import os
import platform
import subprocess
import tempfile
from typing import cast

from discord import Client, File, TextChannel

from config import database_ip, database_password, database_port, database_user


def _write_defaults_file(user: str, password: str, host: str, port: int) -> str:
    """Create a temporary MySQL defaults file with credentials. Returns the file path."""
    content = (
        "[client]\n"
        f"user={user}\n"
        f"password={password}\n"
        f"host={host}\n"
        f"port={port}\n"
    )
    fd, path = tempfile.mkstemp(prefix="mysql_", suffix=".cnf", text=True)
    with os.fdopen(fd, "w") as f:
        f.write(content)
    return path


def dump_database_schema(user: str, password: str, host: str, port: int, output_file: str) -> None:
    if platform.system() != "Linux":
        print("Tried to create Database backup on a non Linux system. This is not supported. Abording..")
        return

    defaults_file = _write_defaults_file(user, password, host, port)
    try:
        dump_command = [
            "mysqldump",
            f"--defaults-extra-file={defaults_file}",
            "--all-databases",
            "--ignore-database=shlink",
        ]

        with open(output_file, "w") as file:
            subprocess.run(dump_command, stdout=file, check=True)
        print(f"Schema dumped to {output_file} successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while dumping the database schema: {e}")
    except FileNotFoundError:
        print("mysqldump command not found. Make sure MySQL is installed and mysqldump is in your PATH.")
    finally:
        try:
            os.unlink(defaults_file)
        except OSError:
            pass


async def create_database_backup(client: Client) -> None:
    assert database_user is not None
    assert database_password is not None
    dump_database_schema(database_user, database_password, database_ip, database_port, "backup.sql")

    channel = cast(TextChannel, client.get_channel(1259573137108893766))

    if channel is not None:
        await channel.send(file=File("backup.sql"))
