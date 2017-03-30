from errbot import BotPlugin, cmdfilter, botcmd, Message
import os
from subprocess import Popen, PIPE, STDOUT


class Jewbot(BotPlugin):
    """
    This is a very basic plugin to try out your new installation and get you started.
    Feel free to tweak me to experiment with Errbot.
    You can find me in your init directory in the subdirectory plugins.
    """

    @botcmd
    def jewhelp(self, msg , args):
        yield "Available Jewish commands:"
        yield " * !dbs script <ENVIRONMENT> <SCRIPT> <SCRIPT_ARGS> - run a dbs-back script from scripts directory"
        yield " * !dbs deployed <ENVIRONMENT> [VERSION] - set or get the version deployed on dbs-back"

    def _run_fab(self, fab):
        """run a dbs-back fab command and yield the output"""
        dbs_back_dir = self.bot_config.DBS_BACK_DIR
        dbs_back_env = self.bot_config.DBS_BACK_ENV
        cmd = ["/bin/bash", "-c",
               "cd {dir} && source {env}/bin/activate && fab \"{fab}\"".format(dir=dbs_back_dir, env=dbs_back_env, fab=fab)]
        self.log.debug("cmd={}".format(cmd))
        with Popen(cmd, stdout=PIPE, stderr=STDOUT) as proc:
            for line in proc.stdout:
                yield line.decode()

    def _run_script(self, env, script, args_str):
        """run a script using the fabfile run_script command"""
        yield "Jewbots roll out! To {} environment".format(env.upper())
        yield "Executing script '{} {}'".format(script, args_str)
        for line in self._run_fab("run_script:{},{},{}".format(env, script, args_str)):
            yield line

    @botcmd(admin_only=True, split_args_with=" ")
    def dbs_script(self, msg, args):
        if not args or args == [""]:
            yield "Available scripts:"
            yield " - !dbs script <dev|prd> ensure_required_metadata [--help]"
        else:
            for line in self._run_script(args.pop(0), args.pop(0), " ".join(args)):
                yield line

    @botcmd(admin_only=True, split_args_with=" ")
    def dbs_deployed(self, msg, args):
        env=args.pop(0)
        version = args.pop(0).strip().strip("v") if len(args) > 0 else None
        if version:
            for line in self._run_fab("set_deployed_version:{env},{version}".format(env=env, version=version)):
                self.log.debug(line)
            yield "Jewbot is pleased to announce that dbs-back version {} was deployed to {} environment".format(version, env.upper())
            yield "The release notes will probably be available here: https://github.com/Beit-Hatfutsot/dbs-back/releases/tag/{}".format(version)
        else:
            yield "Jewbot will now attempt to discover which dbs-back version is deployed on {} environment".format(env.upper())
            for line in self._run_fab("get_deployed_version:{env}".format(env=env)):
                yield line
            yield "Sorry, I couldn't find the version myself, but it might appear somewhere in the above output"
