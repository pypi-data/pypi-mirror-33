import subprocess
import threading
import psutil


class CommandRunner(object):
    def __init__(self, cmd, timeout):
        self.cmd = cmd
        self.process = None
        self.stdout = None
        self.stderr = None
        self.timeout = timeout
 
    def run(self):
        def target():
            self.process = subprocess.Popen(self.cmd, shell=True,
                                            stderr=subprocess.PIPE,
                                            stdout=subprocess.PIPE)
            self.stdout, self.stderr = self.process.communicate()
 
        thread = threading.Thread(target=target)
        thread.setDaemon(True)
        thread.start()
 
        thread.join(self.timeout)
        if thread.is_alive():
            print 'Timeout! Terminating process!'
            p = psutil.Process(int(self.process.pid))
            for p_child in p.children():
                p_child.terminate()
            self.process.terminate()
            return -1, 'Timeout! Terminating process!'
        return self.process.returncode, self.stdout
  

if __name__ == "__main__":
    cmd_line = 'python sleep.py'
    cmd = CommandRunner(cmd_line, 11)
    code, output_size = cmd.run()
    print "%d(%s)" % (code, output_size)
