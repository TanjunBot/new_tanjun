import asyncio
import contextlib
import os
import platform
import tempfile
from typing import cast

from discord import Client, File, TextChannel

from config import database_ip, database_password, database_port, database_schema, database_user


def _write_defaults_file(user: str, password: str, host: str, port: int) -> str:
    """Create a temporary MySQL defaults file with credentials. Returns the file path."""
    content = f"[client]\nuser={user}\npassword={password}\nhost={host}\nport={port}\n"
    fd, path = tempfile.mkstemp(prefix="mysql_", suffix=".cnf", text=True)
    with os.fdopen(fd, "w") as f:
        f.write(content)
    return path


async def dump_database_schema(user: str, password: str, host: str, port: int, output_file: str) -> None:
    if platform.system() != "Linux":
        print("Tried to create Database backup on a non Linux system. This is not supported. Abording..")
        return

    defaults_file = _write_defaults_file(user, password, host, port)
    try:
        dump_command = [
            "mysqldump",
            f"--defaults-extra-file={defaults_file}",
            "--single-transaction",
            "--quick",
            database_schema,
        ]

        with open(output_file, "w") as file:
            process = await asyncio.create_subprocess_exec(
                *dump_command,
                stdout=file,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await process.communicate()

        if process.returncode != 0:
            error_text = stderr.decode() if stderr else "Unknown error"
            raise RuntimeError(f"An error occurred while dumping the database schema to {output_file}: {error_text}")
        else:
            print(f"Schema dumped to {output_file} successfully.")
    except FileNotFoundError:
        print("mysqldump command not found. Make sure MySQL is installed and mysqldump is in your PATH.")
    finally:
        with contextlib.suppress(OSError):
            os.unlink(defaults_file)


async def create_database_backup(client: Client) -> None:
    assert database_user is not None
    assert database_password is not None
    await dump_database_schema(database_user, database_password, database_ip, database_port, "backup.sql")

    channel = cast(TextChannel, client.get_channel(1259573137108893766))

    if channel is not None:
        await channel.send(file=File("backup.sql"))
