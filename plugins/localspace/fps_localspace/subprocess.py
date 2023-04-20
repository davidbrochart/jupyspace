import asyncio


async def run_exec(*args, wait: bool = True):
    proc = await asyncio.create_subprocess_exec(*args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    if wait:
        returncode = await proc.wait()
        if returncode != 0:
            raise RuntimeError(f'Error executing: {" ".join(args)}')
    return proc


async def run_shell(cmd, wait: bool = True):
    proc = await asyncio.create_subprocess_shell(cmd)
    if wait:
        returncode = await proc.wait()
        if returncode != 0:
            raise RuntimeError(f"Error executing: {cmd}")
    return proc
