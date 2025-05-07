import platform
import subprocess

from discord import Client, File, TextChannel

from config import database_password, database_user  # , database_ip


def dump_database_schema(user, password, output_file):
    if platform.system() != "Linux":
        return

    dump_command = [
        "mysqldump",
        "-u",
        user,
        f"--password={password}",
        "--all-databases",
        "--ignore-database=shlink",
    ]

    try:
        with open(output_file, "w") as file:
            subprocess.run(dump_command, stdout=file, check=True)
        print(f"Schema dumped to {output_file} successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while dumping the database schema: {e}")
    except FileNotFoundError:
        print("mysqldump command not found. Make sure MySQL is installed and mysqldump is in your PATH.")


async def create_database_backup(client: Client):
    dump_database_schema(database_user, database_password, "backup.sql")

    channel: TextChannel = client.get_channel(1259573137108893766)

    if channel is not None:
        await channel.send(file=File("backup.sql"))
