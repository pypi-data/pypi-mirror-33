import subprocess


class CheckGitLfsInstalled:
    git_major_vr = 0
    git_sub_vr = 0
    git_minor_vr = 0

    git_lfs_major_vr = 0
    git_lfs_sub_vr = 0
    git_lfs_minor_vr = 0

    def __init__(self):
        self.git_installed = False
        self.git_lfs_installed = False

    def figure_out_git_lfs_installed(self):
        shell_cmd = ['git-lfs','version']
        p = subprocess.Popen(shell_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             shell=False)
        p.wait()
        line = p.stdout.readline()
        git_output = line.decode().rstrip()
        if "git-lfs" in git_output:
            self.git_lfs_installed = True
            self.parse_git_lfs_version(git_output)

    def figure_out_git_installed(self):
        shell_cmd = ['git','version']
        p = subprocess.Popen(shell_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             shell=False)
        p.wait()
        line = p.stdout.readline()
        git_output = line.decode().rstrip()
        if "git version" in git_output:
            self.git_installed = True
            # Check if the version supports git lfs properly
            self.parse_git_version(git_output)

    def parse_git_version(self, shell_str):
        split_list = shell_str.split(" ")
        if len(split_list) == 3:
            git_version = split_list[2]
            git_version_list = git_version.split(".")
            # Example: "2.17.0"
            if len(git_version_list) >= 3:
                self.git_major_vr = int(git_version_list[0])
                self.git_sub_vr = int(git_version_list[1])
                self.git_minor_vr = int(git_version_list[2])

    def parse_git_lfs_version(self, shell_str):
        shell_version_str_list = shell_str.split("/")
        if len(shell_version_str_list) == 2:
            version_str_list = shell_version_str_list[1]
            git_lfs_version_list = version_str_list.split(" ")
            git_lfs_version_str = git_lfs_version_list[0]
            version_list = git_lfs_version_str.split(".")
            if len(version_list) == 3:
                self.git_lfs_major_vr = int(version_list[0])
                self.git_lfs_sub_vr = int(version_list[1])
                self.git_lfs_minor_vr = int(version_list[2])

    def get_git_clone_str(self):
        if self.git_lfs_major_vr == 2:
            if self.git_lfs_sub_vr >= 3:
                return 'git clone'
        elif self.git_lfs_major_vr > 2:
            return 'git clone'
        elif self.git_major_vr == 2:
            if self.git_minor_vr >= 15:
                return 'git clone'
        elif self.git_major_vr > 2:
            return 'git clone'
        else:
            return 'git lfs clone'
