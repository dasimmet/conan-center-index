from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.layout import basic_layout
from conan.tools.env import VirtualBuildEnv


class TestPackageConan(ConanFile):
    settings = "arch", "os", "build_type", "compiler",

    def requirements(self):
        self.tool_requires(self.tested_reference_str)

    def layout(self):
        basic_layout(self)

    def generate(self):
        ms = VirtualBuildEnv(self)
        ms.environment().define(
            "ZIG_LOCAL_CACHE_DIR", f"{self.build_folder}/.zig-cache")
        ms.generate()

    def build(self):
        ms = VirtualBuildEnv(self)
        self.run("$ZIG env")
        cwd = f"{self.recipe_folder}/helloworld-" + \
            ms.vars()['ZIG_VERSION']
        self.run(
            f"$ZIG build --verbose --prefix {self.build_folder}", cwd=cwd)

    def package(self):
        ms = VirtualBuildEnv(self)
        cwd = f"{self.recipe_folder}/helloworld-" + \
            ms.vars()['ZIG_VERSION']
        self.run(
            f"$ZIG build --verbose --prefix {self.package_folder}", cwd=cwd)

    def test(self):
        if can_run(self):
            ms = VirtualBuildEnv(self)
            cwd = f"{self.recipe_folder}/helloworld-" + \
                ms.vars()['ZIG_VERSION']
            self.run("$ZIG build test --verbose",
                     cwd=cwd)
            self.run("$ZIG zen")
