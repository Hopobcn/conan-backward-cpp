# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
#from conans.error import ConanInvalidConfiguration
import os


class BackwardCppConan(ConanFile):
    name = "backward-cpp"
    version = "1.3"
    description = "A beautiful stack trace pretty printer for C++"
    topics = ("conan", "backward-cpp", "stack-trace")
    url = "https://github.com/hopobcn/conan-backward-cpp"
    homepage = "https://github.com/bombela/backward-cpp"
    author = "Hopobcn <hopobcn@gmail.com>"
    license = "MIT"
    exports = ["LICENSE.md"]
    exports_sources = [ "CMakeLists.txt", "0001-install.patch" ]
    generators = "cmake"

    settings = "os", "arch", "compiler", "build_type"
    default_options = {
        "shared": False,
        "fPIC": True
    }
    options = {
       "stack_walking_unwind": [True, False],
       "stack_walking_backtrace": [True, False],
       "stack_details_auto_detect": [False], # dont let backtrace auto decide
       "stack_details_backtrace_symbol": [True, False],
       "stack_details_dw": [True, False],
       "stack_details_bfd": [True, False],
       "shared": [True, False]
    }
    default_options = {
       "stack_walking_unwind": True,
       "stack_walking_backtrace": False,
       "stack_details_auto_detect": False,
       "stack_details_backtrace_symbol": False,
       "stack_details_dw": False,
     # "stack_details_bfd": False,
       "shared": False
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def configure(self):
        if self.settings.os not in ["Linux", "Macos", "Android"]:
            raise ConanInvalidConfiguration("backward-cpp is not supported by your platform.")
        if not self.settings.compiler.cppstd:
            self.settings.compiler.cppstd = 11
        
    # Warning: Setting options conditionally is FINAL and values will not be overridable
    #          from downstream dependent packages
    def config_options(self):
        if self.settings.os in ["Linux", "Android"]:
            # on Linux we want to define BACKWARD_HAS_UNWIND + BACKWARD_HAS_DWARF
            self.options.stack_details_bfd = False
        elif self.settings.os == "Macos":
            # on Macos we want to define BACKWARD_HAS_UNWIND + BACKWARD_HAS_BACKTRACE_SYMBOL
            self.options.stack_details_bfd = True
        
    def requirements(self):
        if self.settings.os == "Linux":
            self.requires("libdwarf/20190505@bincrafters/stable")
        
    def source(self):
        sha256 = "4bf3fb7029ff551acda6578d9d8e13d438ebdd82a787a82b157728e3af6b5dec"
        tools.get("{0}/archive/v{1}.tar.gz".format(self.homepage, self.version, sha256=sha256))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
        tools.patch(base_path=self._source_subfolder, patch_file="0001-install.patch")

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(build_folder=self._build_subfolder, defs={'BACKWARD_' + name.upper(): value for name, value in self.options.values.as_list()})
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
