from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.env import VirtualBuildEnv
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=2.5.0"

arch_mapping = {
    'armv8': 'aarch64',
    'armv8.3': 'aarch64',
    'arm64ec': 'aarch64',
    'armv7': 'armv7a',
    'armv7hf': 'armv7a',
    'armv7s': 'armv7a',
    'armv7k': 'armv7a',
}


class ZigConan(ConanFile):
    name = "zig"
    description = (
        "Zig is a general-purpose programming language and toolchain for maintaining robust, optimal and reusable software."
    )
    topics = ("zig", "compiler", "c", "c++")
    homepage = "https://ziglang.org"
    url = "https://github.com/ziglang/zig"
    license = "MIT"
    settings = "os", "arch"

    def build(self):
        dest = self.build_folder
        arch = str(self.settings.arch).lower()
        if arch in arch_mapping:
            arch = arch_mapping[arch]
        url_tpl: str = self.conan_data["url"] + \
            self.conan_data["archive_ext"][str(self.settings.os)]
        url: str = url_tpl.format(
            version=self.version,
            os=str(self.settings.os).lower(), arch=arch)
        self.output.info("Downloading: " + url)
        try:
            sha256: str = self.conan_data["sources"][self.version][arch][str(
                self.settings.os)]["sha256"]
        except:
            sha256: str = "<sha_not_found>"

        get(self, sha256=sha256, url=url,
            destination=dest, strip_root=True)

    def package(self):
        copy(self, '*', self.build_folder, self.package_folder)

    def package_info(self):

        zig = os.path.join(self.package_folder, f"zig")
        self.output.info("Creating ZIG env var with: " + zig)
        self.buildenv_info.define("ZIG", zig)
        self.output.info(
            "Creating ZIG_VERSION env var with: " + str(self.version))
        self.buildenv_info.define("ZIG_VERSION", str(self.version))

        for subcmd in [("CC", "cc"), ("CXX", "c++")]:
            zig_subcmd = zig + " " + subcmd[1]
            self.output.info(
                "Creating {} env var with: {}".format(subcmd[0], zig_subcmd))
            self.buildenv_info.define(subcmd[0], zig_subcmd)


class ZigBuild:
    zig_version = "0.13.0"
    settings = "os", "arch"
    options = {
        'optimize': ['Debug', 'ReleaseSafe', 'ReleaseFast', 'ReleaseSmall'],
        'target': [None, 'ANY'],
        'step': ['install', 'ANY'],
    }
    default_options = {
        'optimize': 'Debug',
        'target': None,
        'step': 'install',
    }

    def layout(self):
        basic_layout(self, src_folder='src')

    def generate(self):
        ms = VirtualBuildEnv(self)
        ms.environment().define(
            "ZIG_LOCAL_CACHE_DIR", f"{self.build_folder}/.zig-cache")
        ms.generate()

    def build_requirements(self):
        self.tool_requires(f"zig/{self.zig_version}")
        if hasattr(super(), 'build_requirements'):
            super().build_requirements()

    @property
    def zig_target(self):
        if self.options.target != None:
            return str(self.options.target)

        arch = str(self.settings.arch).lower()
        if arch in arch_mapping:
            arch = arch_mapping[arch]

        return arch + '-' + str(self.settings.os).lower()

    @property
    def zig_options(self):
        acc = []
        for k, v in self.options.items():
            if k in ['target', 'step']:
                continue
            acc.append(str("-D"+k+"="+v))
        return acc

    @property
    def zig_build_cmd(self):
        return ["build", "--verbose", f"-Dtarget={self.zig_target}"] + self.zig_options

    def run_zig_cmd(self, prefix: str, step: str, *args, **kwargs):
        if not 'cwd' in kwargs:
            kwargs['cwd'] = self.source_folder
        import shlex
        cmd = "$ZIG " + shlex.join(self.zig_build_cmd +
                                   ['--prefix', str(prefix), str(step)])
        self.run(cmd, *args, **kwargs)

    def build(self):
        self.run_zig_cmd(f"{self.build_folder}/zig-out", self.options.step)

    def package(self):
        self.run_zig_cmd(self.package_folder, self.options.step)
