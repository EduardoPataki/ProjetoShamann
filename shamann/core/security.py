def sanitize_input(cmd):
    # Prevenção contra RCE
    return cmd.replace(';', '').replace('&', '')