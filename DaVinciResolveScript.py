import sys
import os

def load_dynamic(module_name, file_path):
    if sys.version_info[0] >= 3 and sys.version_info[1] >= 5:
        import importlib.machinery
        import importlib.util

        module = None
        spec = None
        loader = importlib.machinery.ExtensionFileLoader(module_name, file_path)
        if loader:
            spec = importlib.util.spec_from_loader(module_name, loader)
        if spec:
            module = importlib.util.module_from_spec(spec)
        if module:
            loader.exec_module(module)
        return module
    else:
        import imp
        return imp.load_dynamic(module_name, file_path)

script_module = None
try:
    import fusionscript as script_module
except ImportError:
    # Look for installer based environment variables:
    lib_path = os.getenv("RESOLVE_SCRIPT_LIB")
    if lib_path:
        try:
            script_module = load_dynamic("fusionscript", lib_path)
        except ImportError:
            pass
    if not script_module:
        # Look for default install locations:
        path = ""
        ext = ".so"
        if sys.platform.startswith("darwin"):
            path = "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/"
        elif sys.platform.startswith("win") or sys.platform.startswith("cygwin"):
            ext = ".dll"
            path = "C:\\Program Files\\Blackmagic Design\\DaVinci Resolve\\"
        elif sys.platform.startswith("linux"):
            path = "/opt/resolve/libs/Fusion/"

        script_module = load_dynamic("fusionscript", path + "fusionscript" + ext)

if script_module:
    sys.modules[__name__] = script_module
else:
    raise ImportError("Could not locate module dependencies")
