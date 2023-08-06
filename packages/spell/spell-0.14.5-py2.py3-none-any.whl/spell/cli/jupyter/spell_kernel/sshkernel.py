#!/usr/bin/env python
import atexit
import json
import logging
import os
import shlex
import signal
import subprocess
import threading
import time

import pexpect

from spell.cli.jupyter.spell_kernel.logger import SpellKernelLogger


class SSHKernelException(Exception):
    pass


class ConnectionRefused(SSHKernelException):
    def __init__(self):
        super(ConnectionRefused, self).__init__("connection refused")


class ConnectionTimeout(SSHKernelException):
    def __init__(self):
        super(ConnectionTimeout, self).__init__("connection timeout")


class CommandNotFound(SSHKernelException):
    def __init__(self, command=None):
        msg = "command not found"
        if command is not None:
            msg += ": {}".format(command)
        super(CommandNotFound, self).__init__(msg)


class SSHKernel:
    def __init__(self, host, ssh_config, connection_info, conda_env, workdir, verbose=False):
        self.host = host
        self.ssh_command = self._build_ssh_command(ssh_config)
        self.connection_info = connection_info
        self.conda_env = conda_env
        self.workdir = workdir

        log_level = logging.DEBUG if verbose else logging.INFO
        self.logger = SpellKernelLogger("SpellKernel", level=log_level)

        self._kernel_conn = None
        self._interrupt_conn = None

        self._kernel_pid = None
        self._tunnel_proc = None
        self._running = True

    def connect_ssh(self):
        if not self._running:
            return

        self.logger.debug("Connecting via SSH")

        exception = [None]

        def get_kernel_conn():
            if self._kernel_conn is None or not self._kernel_conn.isalive():
                for i in range(10):
                    try:
                        self._kernel_conn = self._open_ssh_conn()
                        return
                    except SSHKernelException as e:
                        exception[0] = e
                        time.sleep(1)
                self._kernel_conn = None

        def get_interrupt_conn():
            if self._interrupt_conn is None or not self._interrupt_conn.isalive():
                for i in range(10):
                    try:
                        self._interrupt_conn = self._open_ssh_conn()
                        return
                    except SSHKernelException as e:
                        exception[0] = e
                        time.sleep(1)
                self._interrupt_conn = None

        kernel_thread = threading.Thread(target=get_kernel_conn)
        kernel_thread.start()
        interrupt_thread = threading.Thread(target=get_interrupt_conn)
        interrupt_thread.start()

        kernel_thread.join()
        interrupt_thread.join()

        # If the connection didn't work, raise an exception in the main thread
        if self._kernel_conn is None or self._interrupt_conn is None:
            if exception[0] is not None:
                raise exception[0]
            raise SSHKernelException("connection failed")

    def initialize_remote(self):
        if not self._running:
            return

        if self.conda_env is not None:
            self._kernel_conn.sendline(". activate '{}'".format(self.conda_env))
            expects = [
                ".*~\$",
                ".*command not found",
                pexpect.EOF,
                pexpect.TIMEOUT,
            ]
            i = self._kernel_conn.expect(expects, timeout=120)
            if i == 1:
                raise CommandNotFound("conda activate")
            if i == 2:
                raise ConnectionRefused()
            if i == 3:
                raise ConnectionTimeout()

        marshalled = json.dumps(self.connection_info)
        cmd = "(cd {} && sudo env \"PATH=$PATH\" spell-kernel '{}')".format(self.workdir, marshalled)
        self._kernel_conn.sendline(cmd)
        expects = [
            ".*~\$",
            ".*command not found",
            pexpect.EOF,
            pexpect.TIMEOUT,
        ]
        i = self._kernel_conn.expect(expects, timeout=120)
        if i == 1:
            raise CommandNotFound("spell-kernel")
        if i == 2:
            raise ConnectionRefused()
        if i == 3:
            raise ConnectionTimeout()
        kernel_lines = self._kernel_conn.after.decode("utf-8").split('\r\n')
        self._kernel_pid = int(kernel_lines[-2])
        self.logger.debug("Successfully started kernel, pid is {}".format(self._kernel_pid))

    def tunnel_ports(self):
        if not self._running:
            return

        port_forwards = " ".join(
            "-L 127.0.0.1:{port}:127.0.0.1:{port}".format(port=port)
            for key, port in self.connection_info.items()
            if key.endswith("_port")
        )
        ssh_cmd = "{ssh_cmd} -N {port_forwards} {host}".format(
            ssh_cmd=self.ssh_command,
            port_forwards=port_forwards,
            host=self.host,
        )

        def catch_sigint():
            signal.signal(signal.SIGINT, signal.SIG_IGN)

        self.logger.debug("Tunneling ports")
        try:
            devnull = open(os.devnull, 'w')
            tunnel_proc = subprocess.Popen(shlex.split(ssh_cmd),
                                           preexec_fn=catch_sigint,
                                           stdout=devnull, stderr=devnull)
        except Exception as e:
            raise SSHKernelException("could not tunnel ports: {}".format(str(e)))

        def cleanup_tunnels():
            try:
                tunnel_proc.terminate()
            except OSError:
                pass
        atexit.register(cleanup_tunnels)

        self._tunnel_proc = tunnel_proc
        pid = self._tunnel_proc.pid
        self.logger.debug("Successfully tunnelled ports, pid is {}".format(pid))

    def health_check(self):
        self._kernel_conn.sendline("spell-check '{}'".format(self._kernel_pid))
        expects = [
            ".*~\$",
            ".*command not found",
            pexpect.EOF,
            pexpect.TIMEOUT,
        ]
        i = self._kernel_conn.expect(expects, timeout=120)
        if i == 1:
            raise CommandNotFound("spell-check")
        if i == 2:
            raise ConnectionRefused()
        if i == 3:
            raise ConnectionTimeout()
        check_lines = self._kernel_conn.after.decode("utf-8").split('\r\n')
        ecode = int(check_lines[-2])
        return ecode == 0

    def keep_alive(self):
        if not self._running:
            return

        self._kernel_conn.timeout = 5

        while self._running:
            try:
                if not self._kernel_conn.isalive() or not self._interrupt_conn.isalive():
                    self.logger.debug("SSH connection died")
                    self.connect_ssh()

                if not self.health_check():
                    self.logger.debug("Kernel process died")
                    self.initialize_remote()

                if self._tunnel_proc.poll() is not None:
                    self.logger.debug("Tunnels died")
                    self.tunnel_ports()
            except (ConnectionTimeout, ConnectionRefused):
                pass
            finally:
                time.sleep(0.5)

        self.logger.info("Kernel has died")

    def interrupt(self):
        if self._kernel_pid is None:
            return

        self._interrupt_conn.sendline("sudo kill -2 '{}'".format(self._kernel_pid))
        expects = [
            ".*~\$",
            pexpect.EOF,
            pexpect.TIMEOUT,
        ]
        i = self._interrupt_conn.expect(expects, timeout=120)
        if i == 1:
            raise ConnectionRefused()
        if i == 2:
            raise ConnectionTimeout()
        self.logger.debug("Successfully interrupted kernel")

    def _open_ssh_conn(self):
        ssh_cmd = "{ssh_cmd} {host}".format(ssh_cmd=self.ssh_command,
                                            host=self.host)
        env = os.environ.copy()
        env["TERM"] = "xterm-old"
        ssh_conn = pexpect.spawn(ssh_cmd, env=env)
        expects = [
            ".*~\$",
            pexpect.EOF,
            pexpect.TIMEOUT,
        ]
        i = ssh_conn.expect(expects, timeout=120)
        if i == 1:
            raise ConnectionRefused()
        if i == 2:
            raise ConnectionTimeout()
        return ssh_conn

    def _build_ssh_command(self, ssh_config):
        cmd = "ssh -p {port} -l {user}".format(**ssh_config)
        for key_path in ssh_config.get("key_paths", []):
            cmd += " -i {path}".format(path=key_path)
        for opt in ssh_config.get("options", []):
            cmd += " -o {opt}".format(opt=opt)
        return cmd
