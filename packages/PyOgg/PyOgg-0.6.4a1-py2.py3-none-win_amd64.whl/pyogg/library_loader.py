import ctypes
import os
import sys
import platform

_here = os.path.dirname(__file__)

class ExternalLibraryNotFoundError(Exception):
    pass

class ExternalLibraryNotSupportedError(Exception):
    pass

NotFoundError = ExternalLibraryNotFoundError

NotSupportedError = ExternalLibraryNotSupportedError

architecture = platform.architecture()[0]

windows_styles = ["{}", "{}.dll", "lib{}.dll", "lib{}_dynamic.dll", "{}_dynamic.dll"]

other_styles = ["{}.lib", "lib{}.lib", "{}.a", "lib{}.a", "{}.so", "lib{}.so", "{}.la", "lib{}.la"]

if architecture == "32bit":
    for arch_style in ["32bit", "32" "86", "win32", "x86", "_x86", "_32", "_win32", "_32bit"]:
        for style in ["{}.dll", "lib{}.dll"]:
            windows_styles.append(style.format("{}"+arch_style))
            
elif architecture == "64bit":
    for arch_style in ["64bit", "64" "86_64", "amd64", "win_amd64", "x86_64", "_x86_64", "_64", "_amd64", "_64bit"]:
        for style in ["{}.dll", "lib{}.dll"]:
            windows_styles.append(style.format("{}"+arch_style))


def load(name, paths = None):
    if sys.platform == "win32":
        return load_windows(name, paths)
    else:
        return load_other(name, paths)


def load_other(name, paths = None):
    library = ctypes.util.find_library(name)
    if library:
        return ctypes.CDLL(library)

    if paths:
        for path in paths:
            for style in other_styles:
                candidate = os.path.join(path, style.format(name))
                if os.path.exists(candidate):
                    try:
                        return ctypes.CDLL(candidate)
                    except:
                        pass
    else:
        for path in [os.getcwd(), _here]:
            for style in other_styles:
                candidate = os.path.join(path, style.format(name))
                if os.path.exists(candidate):
                    try:
                        return ctypes.CDLL(candidate)
                    except:
                        pass


def load_windows(name, paths = None):
    not_supported = [] # libraries that were found, but are not supported
    for style in windows_styles:
        candidate = style.format(name)
        try:
            return ctypes.CDLL(candidate)
        except WindowsError:
            pass
        except OSError:
            not_supported.append(candidate)

    if paths:
        for path in paths:
            for style in windows_styles:
                candidate = os.path.join(path, style.format(name))
                if os.path.exists(candidate):
                    try:
                        return ctypes.CDLL(candidate)
                    except OSError:
                        not_supported.append(candidate)

    else:
        for path in [os.getcwd(), _here]:
            for style in windows_styles:
                candidate = os.path.join(path, style.format(name))
                if os.path.exists(candidate):
                    try:
                        return ctypes.CDLL(candidate)
                    except OSError:
                        not_supported.append(candidate)

    if not_supported:
        raise ExternalLibraryNotSupportedError("library '{}' couldn't be loaded, because the following candidates were not supported:".format(name)
                             + ("\n{}" * len(not_supported)).format(*not_supported))

    raise ExternalLibraryNotFoundError("library '{}' couldn't be found".format(name))

        

        
