from errbot import BotPlugin, botcmd
from subprocess import Popen, PIPE, STDOUT
import time
from io import BytesIO


class LowLevelJewbot(BotPlugin):
    """
    Low level Jewbot functionality and logic
    """

    def _run_fab(self, fab):
        """run a dbs-back fab command and yield the output line by line, raises Exception if command fails (after yielding the output lines)"""
        dbs_back_dir = self.bot_config.DBS_BACK_DIR
        dbs_back_env = self.bot_config.DBS_BACK_ENV
        cmd = ["/bin/bash", "-c",
               "cd {dir} && source {env}/bin/activate && fab \"{fab}\"".format(dir=dbs_back_dir, env=dbs_back_env, fab=fab)]
        self.log.debug("cmd={}".format(cmd))
        with Popen(cmd, stdout=PIPE, stderr=STDOUT) as proc:
            for line in iter(proc.stdout.readline, b''):
                yield line.decode()
        if proc.returncode != 0:
            raise Exception("fab command {} failed with returncode = {}".format(fab, proc.returncode))

    def _run_script(self, env, script, args_str):
        """run a script using the fabfile run_script command"""
        yield "\n".join(["Jewbots roll out! To {} environment".format(env.upper()),
                         "Executing script '{} {}'".format(script, args_str)])
        for line in self._run_fab("run_script:{},{},{}".format(env, script, args_str)):
            yield line

    def _jewlidate(self, msg, args, min_args=0):
        """
        Jewish validate the given msg and args - check permissions
        currently requires admin for every command
        """
        if self._bot.__class__.__name__ != "TextBackend":
            # permissions validation is skipped for TextBackend, assuming it's only run locally for testing
            if msg.frm.nick.strip().strip("@") not in [u.strip().strip("@") for u in self.bot_config.BOT_ADMINS]:
                raise Exception("User {} is not in BOT_ADMINS list".format(msg.frm.nick))
        if min_args > 0:
            num_args = 0 if not args or args == [""] else len(args)
            if num_args < min_args:
                raise Exception("Not enough arguments, command must have at least {} arguments".format(min_args))

    def _jewlog(self, initial_lines, lines_generator, final_lines, reply_to_msg=None):
        """
        runs a process or command while streaming the output to #jewbot-log channel
        """
        flush_interval = 5  # seconds
        if len(initial_lines) > 0:
            yield "\n".join(initial_lines)
        tmp_lines = [line for line in initial_lines]
        all_output_lines = []
        last_time = time.time()
        send_lines = lambda lines: self.send(self.build_identifier("#jewbot-log"), "\n".join(lines))
        try:
            for line in lines_generator:
                tmp_lines.append(line)
                all_output_lines.append(line)
                if time.time() - last_time > flush_interval:
                    last_time = time.time()
                    send_lines(tmp_lines)
                    tmp_lines = []
        except Exception:
            send_lines(tmp_lines)
            raise
        if reply_to_msg:
            self.send_stream_request(reply_to_msg.frm, BytesIO("\n".join(all_output_lines).encode("utf-8")), name="Jewbot log")
            yield "\n".join(final_lines)
        else:
            yield "\n".join(all_output_lines + final_lines)
        tmp_lines += final_lines
        send_lines(tmp_lines)

    def activate(self) -> None:
        """run on plugin activation - allows to modify core functionality / run stuff on startup"""
        self._bot.MSG_ERROR_OCCURRED = 'Jewbot cannot perform your request, seek rabinical advice'
        self._bot.MSG_UNKNOWN_COMMAND = 'Unknown command: "%(command)s". '
        super().activate()



class Jewbot(LowLevelJewbot):
    """
    Main Jewbot plugin - contains all Jewbot functionality
    In the future will probably be split in sub-plugins or refactored
    """

    @botcmd
    def jewhelp(self, msg , args):
        """show help specific to jewbot"""
        yield "\n".join(["Available Jewish commands:",
                         " * !dbs script <ENVIRONMENT> <SCRIPT> <SCRIPT_ARGS> - run a dbs-back script from scripts directory",
                         " * !dbs deployed <ENVIRONMENT> [VERSION] - set or get the version deployed on dbs-back",])

    @botcmd(split_args_with=" ")
    def dbs_script(self, msg, args):
        """run a script from dbs-back scripts diretory on the given environment"""
        self._jewlidate(msg, args, min_args=2)
        bh_env, script, args_str = args.pop(0), args.pop(0), " ".join(args)
        for line in self._jewlog(["Jewbots roll out! To {} environment".format(bh_env.upper()),
                                  "Executing script '{} {}', check #jewbot-log to see progress".format(script, args_str)],
                                 self._run_fab("run_script:{},{},{}".format(bh_env, script, args_str)),
                                 ["Great Success! Ran script '{} {}' on {} environment".format(script, args_str, bh_env.upper())],
                                 reply_to_msg=msg):
            yield line

    @botcmd(split_args_with=" ")
    def dbs_deployed(self, msg, args):
        """set or get the deployed version on the different environments"""
        self._jewlidate(msg, args, min_args=1)
        env=args.pop(0)
        version = args.pop(0).strip().strip("v") if len(args) > 0 else None
        if version:
            # set the deployed version
            for line in self._jewlog([],
                                     self._run_fab("set_deployed_version:{env},{version}".format(env=env, version=version)),
                                     ["Jewbot is pleased to announce that dbs-back version {} was deployed to {} environment".format(version, env.upper()),
                                      "The release notes will probably be available here: https://github.com/Beit-Hatfutsot/dbs-back/releases/tag/{}".format(version)],):
                yield line
        else:
            # try to get the deployed version
            # TODO: figure out the actual version, instead of relying on the log
            yield "Jewbot will now attempt to discover which dbs-back version is deployed on {} environment".format(env.upper())
            yield "\n".join(["Sorry, I couldn't find the version myself, but it might appear somewhere in the output:"]
                            + list(self._run_fab("get_deployed_version:{env}".format(env=env))))
