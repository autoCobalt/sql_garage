import sys
import subprocess
import importlib
import importlib.util
from typing import Set, Dict, List

class SimplePackageChecker:
    def __init__(self) -> None:
        
        # Mapping of import names to pip package names
        self.import_to_package_map: Dict[str, str] = {
            # Windows packages
            'win32com.client': 'pywin32',
            'win32api': 'pywin32',
            'win32gui': 'pywin32',
            'win32con': 'pywin32',
            'win32file': 'pywin32',
            'win32pipe': 'pywin32',
            'win32process': 'pywin32',
            'win32security': 'pywin32',
            'win32service': 'pywin32',
            'win32serviceutil': 'pywin32',
            'pywintypes': 'pywin32',
            'pythoncom': 'pywin32',
            
            # Common package mappings
            'bs4': 'beautifulsoup4',
            'cv2': 'opencv-python',
            'PIL': 'Pillow',
            'yaml': 'PyYAML',
            'dotenv': 'python-dotenv',
            'sklearn': 'scikit-learn',
            'skimage': 'scikit-image',
            'flask_cors': 'Flask-CORS',
            'jwt': 'PyJWT',
            'serial': 'pyserial',
        }
        
        # Special packages with multiple possible import names
        self.special_packages: Dict[str, List[str]] = {
            'pywin32': ['win32com.client', 'win32api', 'pywintypes', 'pythoncom'],
            'pypiwin32': ['win32com.client', 'win32api', 'pywintypes', 'pythoncom'], # Same as pywin32
            'beautifulsoup4': ['bs4'],
            'python-dotenv': ['dotenv'],
            'scikit-learn': ['sklearn'],
            'Pillow': ['PIL', 'PIL.Image'],
            'opencv-python': ['cv2'],
        }
    
    def _try_import(self, import_name: str) -> bool:
        # Method 1: Direct import
        try:
            importlib.import_module(import_name)
            return True
        except ImportError:
            pass
        
        # Method 2: Using find_spec (more robust)
        try:
            spec = importlib.util.find_spec(import_name)
            return spec is not None
        except (ImportError, AttributeError, ValueError, ModuleNotFoundError):
            pass
        
        return False
    
    def _check_special_package(self, package_name: str) -> bool:
        if package_name not in self.special_packages:
            return False
        
        import_names: List[str] = self.special_packages[package_name]
        
        for import_name in import_names:
            if self._try_import(import_name):
                return True
        
        return False
    
    def is_package_installed(self, package_identifier: str) -> bool:
        # Method 1: Check if it's a special package
        if self._check_special_package(package_identifier):
            return True
        
        # Method 2: Try direct import
        if self._try_import(package_identifier):
            return True
        
        # Method 3: If it's an import name, get the package name and check again
        if package_identifier in self.import_to_package_map:
            mapped_package: str = self.import_to_package_map[package_identifier]
            if self._check_special_package(mapped_package):
                return True
        
        return False
    
    def get_package_name_for_installation(self, package_identifier: str) -> str:
        return self.import_to_package_map.get(package_identifier, package_identifier)
    
    def _install_package(self, package_name: str) -> None:
        # Skip Windows-specific packages on non-Windows systems
        if package_name in ['pywin32', 'pypiwin32'] and not sys.platform.startswith('win'):
            print(f"Skipping {package_name} - Windows-only package")
            return
        
        try:
            print(f"<<<<<< installing: {package_name} >>>>>>")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package_name
            ], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            print(f"Failed to install {package_name}. You might need to run this script with administrator privileges.")
            sys.exit(1)
    
    def install_required_libraries(self, modules: Set[str]) -> None:
        if not modules:
            return
            
        missing_packages: List[str] = []
        
        # Check what's missing
        for module in modules:
            if not self.is_package_installed(module):
                package_name: str = self.get_package_name_for_installation(module)
                missing_packages.append(package_name)
        
        # Remove duplicates while preserving order
        missing_packages = list(dict.fromkeys(missing_packages))
        
        # Only show messages if there are missing packages
        if missing_packages:
            print(f"Installing missing libraries... {set(missing_packages)}")
            
            for package_name in missing_packages:
                self._install_package(package_name)
            
            print("<<<<<< All required packages have been installed. Continuing... >>>>>>\n")


# Global instance for easy use
_package_checker: SimplePackageChecker = SimplePackageChecker()


def install_required_libraries(modules: Set[str]) -> None:
    _package_checker.install_required_libraries(modules)


def is_package_installed(package_identifier: str) -> bool:
    return _package_checker.is_package_installed(package_identifier)
