# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
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
    exports_sources = [ "CMakeLists.txt" ]
    generators = "cmake"

    settings = "os", "arch", "compiler", "build_type"
    default_options = {
        "shared": False,
        "fPIC": True
    }
    options = {
       "stack_walking_unwind": [True, False],
       "stack_walking_backtrace": [True, False],
       "stack_details_auto_detect": [True, False],
       "stack_details_backtrace_symbol": [True, False],
       "stack_details_dw": [True, False],
       "stack_details_bfd": [True, False],
       "shared": [True, False]
    }
    default_options = {
       "stack_walking_unwind": True,
       "stack_walking_backtrace": False,
       "stack_details_auto_detect": True,
       "stack_details_backtrace_symbol": False,
       "stack_details_dw": False,
       "stack_details_bfd": False,
       "shared": False
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def configure(self):
        if not self.settings.compiler.cppstd:
            self.settings.compiler.cppstd = 11
        elif self.settings.compiler.cppstd.value < "11":
                raise ConanInvalidConfiguration("backward-cpp requires c++11")

    def source(self):
        sha256 = "4bf3fb7029ff551acda6578d9d8e13d438ebdd82a787a82b157728e3af6b5dec"
        tools.get("{0}/archive/v{1}.tar.gz".format(self.homepage, self.version, sha256=sha256))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

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
