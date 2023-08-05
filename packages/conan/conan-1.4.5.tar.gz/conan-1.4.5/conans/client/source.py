import os
import shutil

import six

from conans import tools
from conans.errors import ConanException, conanfile_exception_formatter, \
    ConanExceptionInUserConanfileMethod
from conans.model.conan_file import get_env_context_manager
from conans.model.scm import SCM
from conans.paths import EXPORT_TGZ_NAME, EXPORT_SOURCES_TGZ_NAME, CONANFILE, CONAN_MANIFEST
from conans.util.files import rmdir, set_dirty, is_dirty, clean_dirty, mkdir


def get_scm(conanfile, src_folder):
    data = getattr(conanfile, "scm", None)
    if data is not None and isinstance(data, dict):
        return SCM(data, src_folder)
    else:
        # not an instance of dict or None, skip SCM feature.
        pass


def complete_recipe_sources(remote_manager, client_cache, registry, conanfile, conan_reference):
    sources_folder = client_cache.export_sources(conan_reference, conanfile.short_paths)
    if os.path.exists(sources_folder):
        return None

    if not hasattr(conanfile, "exports_sources"):
        mkdir(sources_folder)
        return None

    # If not path to sources exists, we have a problem, at least an empty folder
    # should be there
    current_remote = registry.get_ref(conan_reference)
    if not current_remote:
        raise ConanException("Error while trying to get recipe sources for %s. "
                             "No remote defined" % str(conan_reference))

    export_path = client_cache.export(conan_reference)
    remote_manager.get_recipe_sources(conan_reference, export_path, sources_folder,
                                      current_remote)


def merge_directories(src, dst):
    for src_dir, _, files in os.walk(src):
        dst_dir = os.path.join(dst, os.path.relpath(src_dir, src))
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            shutil.copy2(src_file, dst_file)


def _clean_source_folder(folder):
    for f in (EXPORT_TGZ_NAME, EXPORT_SOURCES_TGZ_NAME, CONANFILE+"c",
              CONANFILE+"o", CONANFILE, CONAN_MANIFEST):
        try:
            os.remove(os.path.join(folder, f))
        except OSError:
            pass


def config_source(export_folder, export_source_folder, local_sources_path, src_folder,
                  conan_file, output, force=False):
    """ creates src folder and retrieve, calling source() from conanfile
    the necessary source code
    """

    def remove_source(raise_error=True):
        output.warn("This can take a while for big packages")
        try:
            rmdir(src_folder)
        except BaseException as e_rm:
            set_dirty(src_folder)
            msg = str(e_rm)
            if six.PY2:
                msg = str(e_rm).decode("latin1")  # Windows prints some chars in latin1
            output.error("Unable to remove source folder %s\n%s" % (src_folder, msg))
            output.warn("**** Please delete it manually ****")
            if raise_error or isinstance(e_rm, KeyboardInterrupt):
                raise ConanException("Unable to remove source folder")

    if force:
        output.warn("Forced removal of source folder")
        remove_source()
    elif is_dirty(src_folder):
        output.warn("Trying to remove corrupted source folder")
        remove_source()
    elif conan_file.build_policy_always:
        output.warn("Detected build_policy 'always', trying to remove source folder")
        remove_source()

    if not os.path.exists(src_folder):
        output.info('Configuring sources in %s' % src_folder)
        shutil.copytree(export_folder, src_folder, symlinks=True)
        # Now move the export-sources to the right location
        merge_directories(export_source_folder, src_folder)
        _clean_source_folder(src_folder)
        try:
            shutil.rmtree(os.path.join(src_folder, "__pycache__"))
        except OSError:
            pass

        set_dirty(src_folder)
        os.chdir(src_folder)
        conan_file.source_folder = src_folder
        try:
            with get_env_context_manager(conan_file):
                with conanfile_exception_formatter(str(conan_file), "source"):
                    conan_file.build_folder = None
                    conan_file.package_folder = None

                    scm = get_scm(conan_file, src_folder)
                    if scm:
                        # scm.capture_origin before exporting
                        if local_sources_path and os.path.exists(local_sources_path):
                            output.info("Getting sources from folder: %s" % local_sources_path)
                            merge_directories(local_sources_path, src_folder)
                            _clean_source_folder(src_folder)
                        else:
                            output.info("Getting sources from url: '%s'" % scm.url)
                            scm.clone()
                            scm.checkout()

                    conan_file.source()
            clean_dirty(src_folder)  # Everything went well, remove DIRTY flag
        except Exception as e:
            os.chdir(export_folder)
            # in case source() fails (user error, typically), remove the src_folder
            # and raise to interrupt any other processes (build, package)
            output.warn("Trying to remove corrupted source folder")
            remove_source(raise_error=False)
            if isinstance(e, ConanExceptionInUserConanfileMethod):
                raise e
            raise ConanException(e)


def config_source_local(dest_dir, conan_file, conanfile_folder, output):
    output.info('Configuring sources in %s' % dest_dir)
    conan_file.source_folder = dest_dir
    with tools.chdir(dest_dir):
        try:
            with conanfile_exception_formatter(str(conan_file), "source"):
                with get_env_context_manager(conan_file):
                    conan_file.build_folder = None
                    conan_file.package_folder = None
                    scm = get_scm(conan_file, dest_dir)
                    if scm:
                        if scm.capture_origin or scm.capture_revision:
                            output.info("Getting sources from folder: %s" % conanfile_folder)
                            merge_directories(conanfile_folder, dest_dir)
                            _clean_source_folder(dest_dir)
                        else:
                            output.info("Getting sources from url: '%s'" % scm.url)
                            scm.clone()
                            scm.checkout()

                    conan_file.source()
        except ConanExceptionInUserConanfileMethod:
            raise
        except Exception as e:
            raise ConanException(e)
