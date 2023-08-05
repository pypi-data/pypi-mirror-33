import MockSSH

from twisted.internet import reactor
from threading import Thread

INCOMPLETE_COMMAND = "ERROR: Incomplete command"

# From https://stackoverflow.com/a/2838309
def get_open_port():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("",0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port

class MockAerohive:

    def __init__(self):
        self.running = False
        self.reactor_running = False
        self.users = {}
        self.hostname = "AH-2A0B00"
        self.commands = [
            self.command_hostname(),
        ]

    def addUser(self, username, password):
        self.users[username] = password
        return self

    def prompt(self):
        return self.hostname + "#"

    def run(self, interface="127.0.0.1", port=None):
        if port == None:
            port = get_open_port()
        self.running = True
        # Re-implementation of MockSSH.startThreadedServer,
        # that doesn't start Reactor inside a Thread if it's already running.
        sshFactory = MockSSH.getSSHFactory(
            self.commands,
            prompt=self.prompt(),
            keypath=".",
            **self.users
        )
        self.listener = reactor.listenTCP(port, sshFactory, interface='')
        if not reactor.running:
            Thread(target=reactor.run, args=(False,)).start()
        self.reactor_running = True
        return port

    def stop(self):
        if self.running:
            self.listener.stopListening()
        self.running = False
        return self

    def stopAll(self):
        MockSSH.stopThreadedServer()
        self.running = False
        return self

    def unknownKeyword(self, command, args, correctArgs=0, expectedArgs=[]):
        """Create an Aerohive `unknown keyword or invalid input` error message.

        :param str command: The command entered.
        :param args: All arguments provided.
        :type args: list[str]
        :param int correctArgs: The expected number of arguments.
        :param expectedArgs: Possible options for the first incorrect argument.  Used to align the error message.
            Provide an empty array if there are no possible arguments.
        :type expectedArgs: list[str]
        :returns: str -- The error message to show to the user.
        """
        # Create the portion of the command that is "correct", to pad the error message (and align the carrot)
        # prompt + correct args + substring of first incorrect argument that matches a known command
        correct = self.prompt() + command
        added = 0
        for arg in args:
            if added >= correctArgs:
                break
            correct += " " + arg
            added += 1
        if correctArgs > 0:
            correct += " "
        if len(args) > correctArgs:
            incorrectArg = args[correctArgs]
            shortestMatch = ""
            for arg in expectedArgs:
                # First, check if the entire possible argument matches - e.g. user provided "foobars" when "foobar" is
                # the command.
                if incorrectArg[0:len(arg)] == arg:
                    if (len(arg) + 1) > len(shortestMatch):
                        shortestMatch = arg + incorrectArg[len(arg)]
                    x = 1 # noop needed for "continue" to be detected by coverage
                    continue
                # If the entire string doesn't match, go character-by-character to see how many (if any) characters
                # match before differing.
                matched = ""
                for i in range(min(len(arg), len(incorrectArg))):
                    if arg[i] != incorrectArg[i]:
                        if (i + 1) > len(shortestMatch):
                            shortestMatch = matched + incorrectArg[i]
                        break
                    matched += arg[i]
            correct += shortestMatch
        return (" " * len(correct)) + "^-- unknown keyword or invalid input"

    def command_hostname(self):
        server = self
        class command_hostname(MockSSH.SSHCommand):
            name = "hostname"
            def start(self):
                if len(self.args) < 1:
                    self.writeln(INCOMPLETE_COMMAND)
                elif len(self.args) > 1:
                    self.writeln(server.unknownKeyword("hostname", self.args, 1, []))
                else:
                    server.hostname = self.args[0]
                    self.protocol.prompt = server.prompt()
                    self.write(server.prompt())
                self.exit()
        return command_hostname
