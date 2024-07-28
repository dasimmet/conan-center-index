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

    def layout(self):
        basic_layout(self)

    def generate(self):
        ms = VirtualBuildEnv(self)
        ms.environment().define(
            "ZIG_LOCAL_CACHE_DIR", f"{self.build_folder}/.zig-cache")
        ms.generate()

    def requirements(self):
        self.tool_requires(f"zig/{self.zig_version}")
        if hasattr(super(), 'requirements'):
            super().requirements()

    def build(self):
        self.run(
            f"$ZIG build --verbose --prefix {self.build_folder}", cwd=self.source_folder)

    def package(self):
        self.run(
            f"$ZIG build --verbose --prefix {self.package_folder}", cwd=self.source_folder)
