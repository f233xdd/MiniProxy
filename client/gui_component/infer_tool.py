def verify_ip(ip: str) -> bool:
    if isinstance(ip, str):
        sep_str = ip.split('.')

        if len(sep_str) == 4:
            try:
                for s in sep_str:
                    if not 0 <= int(s) <= 999:
                        return False
                return True
            except ValueError:
                pass

    raise ValueError(ip)


def verify_port(port: str) -> bool:
    if isinstance(port, str):
        try:
            if 0 <= int(port) <= 65535:
                return True
        except ValueError:
            pass

    raise ValueError(port)