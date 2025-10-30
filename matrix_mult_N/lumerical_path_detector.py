#!/usr/bin/env python3
"""
Sistema automático de detección de Lumerical
Detecta automáticamente la instalación de Lumerical en cualquier sistema
"""

import os
import platform
import glob
import imp
import sys
import re

class LumericalPathDetector:
    def __init__(self):
        self.system = platform.system().lower()
        self.detected_paths = []
        self.lumapi = None
        
    def detect_lumerical_installations(self):
        """Detectar todas las instalaciones de Lumerical en el sistema"""
        
        if self.system == "windows":
            self._detect_windows_installations()
        elif self.system == "darwin":  # macOS
            self._detect_macos_installations()
        elif self.system == "linux":
            self._detect_linux_installations()
            
        return self.detected_paths
    
    def _detect_windows_installations(self):
        """Detectar instalaciones en Windows"""
        
        search_patterns = [
            "C:\\Program Files\\ANSYS Inc\\v*\\Lumerical\\api\\python\\lumapi.py",
            "C:\\Program Files\\ANSYS Inc\\*\\Artemis\\LumericalFDTD\\api\\python\\lumapi.py",
            "C:\\Program Files\\Lumerical\\v*\\api\\python\\lumapi.py",
            "C:\\Program Files\\Lumerical\\*\\api\\python\\lumapi.py",
            "C:\\Program Files (x86)\\ANSYS Inc\\v*\\Lumerical\\api\\python\\lumapi.py",
            "C:\\Program Files (x86)\\Lumerical\\v*\\api\\python\\lumapi.py",
        ]
        
        for pattern in search_patterns:
            matches = glob.glob(pattern)
            for match in matches:
                if os.path.isfile(match):
                    version = self._extract_version_from_path(match)
                    self.detected_paths.append({
                        'path': match,
                        'version': version,
                        'type': 'ANSYS' if 'ANSYS' in match else 'Standalone'
                    })
    
    def _detect_macos_installations(self):
        """Detectar instalaciones en macOS"""
        
        search_patterns = [
            "/Applications/Lumerical*/api/python/lumapi.py",
            "/Applications/Lumerical*/*.app/Contents/API/Python/lumapi.py",
            "/opt/lumerical/v*/api/python/lumapi.py",
        ]
        
        for pattern in search_patterns:
            matches = glob.glob(pattern)
            for match in matches:
                if os.path.isfile(match):
                    version = self._extract_version_from_path(match)
                    self.detected_paths.append({
                        'path': match,
                        'version': version,
                        'type': 'Mac App' if '.app' in match else 'Standalone'
                    })
    
    def _detect_linux_installations(self):
        """Detectar instalaciones en Linux"""
        
        search_patterns = [
            "/opt/lumerical/v*/api/python/lumapi.py",
            "/usr/local/lumerical/v*/api/python/lumapi.py",
        ]
        
        for pattern in search_patterns:
            matches = glob.glob(pattern)
            for match in matches:
                if os.path.isfile(match):
                    version = self._extract_version_from_path(match)
                    self.detected_paths.append({
                        'path': match,
                        'version': version,
                        'type': 'Linux'
                    })
    
    def _extract_version_from_path(self, path):
        """Extraer versión de la ruta"""
        
        patterns = [
            r'v(\d{4}[a-z]?)',
            r'(\d{4}[a-z]?)',
            r'v(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, path, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return "unknown"
    
    def get_best_installation(self):
        """Seleccionar la mejor instalación disponible"""
        
        if not self.detected_paths:
            self.detect_lumerical_installations()
        
        if not self.detected_paths:
            return None
        
        sorted_installations = sorted(
            self.detected_paths, 
            key=lambda x: self._version_sort_key(x['version']), 
            reverse=True
        )
        
        return sorted_installations[0]
    
    def _version_sort_key(self, version):
        """Clave para ordenar versiones"""
        match = re.search(r'(\d+)', version)
        if match:
            return int(match.group(1))
        return 0
    
    def load_lumapi_automatically(self):
        """Cargar lumapi automáticamente con la mejor instalación"""
        
        best_installation = self.get_best_installation()
        
        if not best_installation:
            raise FileNotFoundError(
                "No se encontró ninguna instalación de Lumerical.\n"
                "Buscado en: Program Files\\Lumerical, Program Files\\ANSYS Inc, /Applications"
            )
        
        path = best_installation['path']
        version = best_installation['version']
        install_type = best_installation['type']
        
        print(f"Lumerical detectado: {version} ({install_type})")
        print(f"Ruta: {path}")
        
        self.lumapi = imp.load_source("lumapi", path)
        return self.lumapi

def auto_detect_and_load_lumapi():
    """Función principal para usar en interface.py"""
    detector = LumericalPathDetector()
    return detector.load_lumapi_automatically()

if __name__ == "__main__":
    print("=== Detector de Lumerical ===")
    detector = LumericalPathDetector()
    detector.detect_lumerical_installations()
    
    if detector.detected_paths:
        print(f"\nInstalaciones encontradas: {len(detector.detected_paths)}")
        for install in detector.detected_paths:
            print(f"- Version {install['version']} ({install['type']})")
            print(f"  {install['path']}")
    else:
        print("No se encontraron instalaciones de Lumerical")