# coding=utf-8
import logging
import datetime
import os
from command import CommandRunner
import re
import time


class AdbUtil:
    def __init__(self, device_id="", logger_name=None):
        self.device_id = device_id
        self.logger = logging.getLogger(logger_name)

    def run_command(self, command, timeout=180):
        print command
        self.logger.info("run command: %s, timeout:%d" % (command, timeout))
        cmd = CommandRunner(command, timeout)
        code, output = cmd.run()
        return output

    @staticmethod
    def list_devices():
        command = "adb devices"
        cmd = CommandRunner(command, 180)
        code, output = cmd.run()
        devices = output.split("\n")
        device_list = []
        for device in devices[1:]:
            device_id = device.replace("device", "").strip()
            if len(device_id) == 0:
                continue
            device_list.append(device_id)

        return device_list

    def adb_command(self, command, timeout=180):
        if len(self.device_id) != 0:
            cmd = "adb -s %s %s" % (self.device_id, command)
        else:
            cmd = "adb %s" % command
        return self.run_command(cmd, timeout)

    def keep_app_alive(self, package):
        running_apps = self.get_running_apps()
        if package not in running_apps:
            self.start_app(package)

    def set_phone_time(self):
        now_time = datetime.datetime.now().strftime('%m%d%H%M%Y.%S')
        command = "shell date %s" % now_time
        self.adb_command(command)

    def prepare_phone_for_test(self):
        # root
        self.adb_command("root")
        # 最大化休眠时间
        self.adb_command("shell settings put system screen_off_timeout 1800000")
        # 取消时区自动获取
        self.adb_command("shell settings put global auto_time 0")
        # 接电不息屏
        self.adb_command("shell settings put global stay_on_while_plugged_in 3")
        # 禁止旋转
        self.adb_command("shell settings put system user_rotation 0")
        # 24小时制
        self.adb_command("shell settings put system time_12_24 24")
        # 设置当前时间
        self.set_phone_time()

    def start_app(self, package):
        self.adb_command("shell monkey -p %s -c android.intent.category.LAUNCHER 1" % package)

    def install_app(self, apk_path):
        self.adb_command("install -r %s" % apk_path)

    def monkey_app(self, package, times):
        self.adb_command("shell monkey -p %s %d" % (package, times))

    def uninstall_app(self, package):
        self.adb_command("uninstall %s" % package)
        self.adb_command("shell rm -fr /data/app/%s*" % package)

    def stop_app(self, package):
        running_apps = self.get_running_apps()
        if package in running_apps:
            self.adb_command("shell am force-stop %s" % package)

    def get_packages(self, white_list=[]):
        command = "shell pm list package -3"
        content = self.adb_command(command)

        package_list = []
        for line in content.split("\n"):
            try:
                package = line.split(":")[1].strip()

                is_white = 0
                for white_app in white_list:
                    if package.find(white_app) != -1:
                        is_white = 1
                        break
                if is_white == 1:
                    continue

                package_list.append(package)
            except:
                pass
        return package_list

    def clean_all_app(self, white_list):
        package_list = self.get_packages(white_list)
        for package in package_list:
            self.stop_app(package)
            self.uninstall_app(package)

    def enable_wifi(self):
        self.adb_command("shell svc wifi enable")

    def get_apk_package(self, apk_path):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        aapt_path = os.path.join(base_dir, "aapt.exe")
        name_pattern = re.compile(".*name=\'(.*?)\'.*")

        # get package name
        aapt_command = "%s d badging %s" % (aapt_path, apk_path)
        content = self.run_command(aapt_command)
        for line in content.split("\n"):
            match = name_pattern.match(line)
            if match:
                return match.group(1)

        return None

    def disable_airplane_model(self):
        self.adb_command("shell settings put global airplane_mode_on 0")
        self.adb_command("shell am broadcast -a android.intent.action.AIRPLANE_MODE")

    def hide_status_bar(self):
        self.adb_command("settings put global policy_control immersive.full=*")

    def reboot_device(self, password):
        self.adb_command("reboot")
        while True:
            device_online = self.device_id in self.list_devices()
            if device_online:
                break
            time.sleep(5)
            print "waiting for %s bootup..." % self.device_id

        print "device %s bootup success..." % self.device_id
        time.sleep(15)
        self.adb_command("shell input tap 1178 1452")
        self.adb_command("shell input text %s" % password)
        self.adb_command("shell input keyevent 66")
        time.sleep(15)
        self.adb_command("shell input tap 1178 1452")

    def check_if_screen_on(self):
        content = self.adb_command("shell dumpsys window policy")
        for line in content.split("\n"):
            if line.find("mScreenOnEarly") != -1:
                if line.find("mScreenOnEarly=false") != -1:
                    return False
                if line.find("mScreenOnEarly=true") != -1:
                    return True

    def check_if_screen_lock(self):
        content = self.adb_command("shell dumpsys window policy")
        for line in content.split("\n"):
            if line.find("isStatusBarKeyguard") != -1:
                if line.find("isStatusBarKeyguard=false") != -1:
                    return False
                if line.find("isStatusBarKeyguard=true") != -1:
                    return True

    def unlock_device(self, password):
        if self.check_if_screen_on():
            self.adb_command("shell input keyevent 26")
            time.sleep(2)
        self.adb_command("shell input keyevent 26")
        if not self.check_if_screen_lock():
            return
        # adb_command(device_id, "shell input keyevent 66")
        self.adb_command("shell input keyevent 82")
        self.adb_command("shell input text %s" % password)
        self.adb_command("shell input keyevent 66")

    def retrieve_data(self):
        pattern = re.compile("\d{4}_\d{2}_\d{2}_\d{2}.csv")
        command = "shell ls /sdcard/"
        output = self.adb_command(command)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        for file_name in output.split("\n"):
            file_name = file_name.strip().split(".csv")[0] + ".csv"
            match = pattern.match(file_name)
            if match:
                command = "pull /sdcard/%s %s" % (file_name, "%s/result/%s_%s" % (base_dir, self.device_id, file_name))
                self.adb_command(command)

    def get_running_apps(self):
        command = "shell ps -A"
        output = self.adb_command(command)
        pattern = re.compile("\s+")
        running_apps = []
        for line in output.split("\n"):
            line = line.strip()
            if len(line) == 0:
                continue
            parts = pattern.split(line)
            if not parts[0].startswith("u0"):
                continue

            if parts[-1].find(".") == -1:
                continue

            package = parts[-1].split(":")[0]
            running_apps.append(package)

        return running_apps

    def get_crash_packages(self):
        output = self.adb_command("logcat -s AndroidRuntime -t 10000")
        pattern = re.compile(".*AndroidRuntime: Process: (.*), PID:.*")
        crash_packages = []
        for line in output.split("\n"):
            match = pattern.match(line)
            if match:
                crash_package = match.group(1).strip()
                crash_package = crash_package.split(":")[0].strip()
                crash_packages.append(crash_package)

        return crash_packages, output


if __name__ == "__main__":
    white_list = ["com.coloros.safecenter", "com.antiy"]
    sample_dir = "Z:\\ai\\sample\\blackmail_float"
    logger_name = "auto_test"
    logging.basicConfig(level=logging.INFO,
                        name=logger_name,
                        format='%(asctime)s %(filename)s: %(message)s',
                        datefmt='%a,%d %b %Y %H:%M:%S',
                        filename='%s/auto_test.%s' % (sample_dir, time.strftime('%Y%m%d', time.localtime(time.time()))),
                        filemode='a+')
    adb_util = AdbUtil()
    print adb_util.get_running_apps()


