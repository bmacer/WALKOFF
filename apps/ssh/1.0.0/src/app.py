import os
import logging
import asyncio

import asyncssh

from walkoff_app_sdk.app_base import AppBase

logger = logging.getLogger("apps")


class SSH(AppBase):
    __version__ = "1.0.0"
    app_name = "ssh"

    def __init__(self, redis, logger, console_logger=None):
        super().__init__(redis, logger, console_logger)

    async def exec_local_command(self, command):
        proc = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE,
                                                     stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        return {"stdout": str(stdout), "stderr": str(stderr)}

    async def exec_command(self, hosts, port=None, args=None, username=None, password=None):
        results = {}

        for host in hosts:
            try:
                async with asyncssh.connect(host=host, port=port, username=username, password=password,
                                            known_hosts=None) as conn:
                    for cmd in args:
                        temp = await conn.run(cmd)
                        output = temp.stdout
                        results[host] = {"stdout": output, "stderr": ""}
            except Exception as e:
                results[host] = {"stdout": "", "stderr": f"{e}"}

        return results

    async def sftp_copy(self, src_path, dest_path, src_host, src_port, src_username, src_password, dest_host, dest_port,
                        dest_username, dest_password):
        curr_dir = os.getcwd()
        temp_dir = os.path.join(curr_dir, r'temp_data')
        os.makedirs(temp_dir)

        async with asyncssh.connect(host=src_host, port=src_port, username=src_username, password=src_password,
                                    known_hosts=None) as conn:
            async with asyncssh.connect(host=dest_host, port=dest_port, username=dest_username, password=dest_password,
                                        tunnel=conn, known_hosts=None) as tunneled_conn:
                # grab remote file, place in container
                async with conn.start_sftp_client() as sftp:
                    results = await sftp.get(src_path, temp_dir)

                spliced_path = src_path.split('/')
                file_name = spliced_path[len(spliced_path) - 1]

                # copy grabbed file to desired location
                async with tunneled_conn.start_sftp_client() as sftp2:
                    results2 = await sftp2.put(temp_dir + "/" + file_name, dest_path)

        # cleaning up temp file
        for file in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        os.rmdir(temp_dir)

        return "Successfully Copied File."

    async def run_shell_script_file(self, local_file_name, hosts, port, username, password):
        results = {}

        curr_dir = os.getcwd()
        temp_dir = os.path.join(curr_dir, r'scripts')
        os.chdir(temp_dir)
        curr_dir = os.getcwd()
        local_file_path = os.path.join(curr_dir, local_file_name)

        for host in hosts:
            try:
                async with asyncssh.connect(host=host, port=port, username=username, password=password,
                                            known_hosts=None) as conn:
                    script = open(local_file_path, "r").read()
                    cmd = script
                    temp = await conn.run(cmd)
                    output = temp.stdout
                    results[host] = {"stdout": output, "stderr": ""}
            except Exception as e:
                results[host] = {"stdout": "", "stderr": f"{e}"}

        return results


if __name__ == "__main__":
    asyncio.run(SSH.run())