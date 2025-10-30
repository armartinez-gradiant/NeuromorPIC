
try:
    from lumerical_path_detector import auto_detect_and_load_lumapi
    lumapi = auto_detect_and_load_lumapi()
except Exception as e:
    print("❌ Error cargando 'lumapi':", e)
    lumapi = None
