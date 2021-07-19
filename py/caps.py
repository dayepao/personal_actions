import ctypes


def CAPSLOCK_STATE():
    hllDll = ctypes.WinDLL("User32.dll")
    VK_CAPITAL = 0x14
    return hllDll.GetKeyState(VK_CAPITAL)


CAPSLOCK = CAPSLOCK_STATE()
if ((CAPSLOCK) & 0xffff) != 0:
    print("\
WARNING:  CAPS LOCK IS ENABLED!\
")
