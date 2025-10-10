"""
Configuración de componentes para la plataforma SiN (Silicon Nitride)
Por ahora usa componentes ideales genéricos - se personalizarán más adelante
"""

COMPONENTS = {
    'phase_shifter': {
        # Tipo de elemento en INTERCONNECT (componente ideal genérico)
        'type': 'Optical Phase Shift Unidirectional',
        
        # Nombre del parámetro que controla la fase
        'phase_param': 'phase shift',
        
        # Parámetros adicionales (vacío por ahora, componente ideal)
        'params': {
            # Los componentes ideales no necesitan parámetros adicionales
        }
    },
    
    'directional_coupler': {
        # Tipo de elemento en INTERCONNECT (componente ideal genérico)
        'type': 'Waveguide Coupler Unidirectional',
        
        # Nombre del parámetro que controla el coupling
        'coupling_param': 'coupling coefficient 1',
        
        # Parámetros adicionales (vacío por ahora, componente ideal)
        'params': {
            # Los componentes ideales no necesitan parámetros adicionales
        }
    }
}