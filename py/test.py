from utils_dayepao import cmd_dayepao, set_powershell_cmd


def test1():
    ps = "write-output 'test1'; Start-Sleep -s 5; write-output 'test2'"
    queue = cmd_dayepao(ps)
    while (ps_result := queue.get()) != b'':
        print(ps_result)
    print("123")
    ps = "write-output 'test3'; Start-Sleep -s 5; write-output 'test4'"
    queue = cmd_dayepao(ps)
    while (ps_result := queue.get()) != b'':
        print(ps_result)
    print("456")


def test2():
    ps = set_powershell_cmd(
        "write-output '输入命令为空'",
        "Start-Sleep -s 5",
        "write-output 'test2'"
    )
    # ps = set_powershell_cmd()
    print(repr(ps))
    queue = cmd_dayepao(["powershell", ps])
    while (ps_result := queue.get()) != b'':
        print(ps_result)


if __name__ == "__main__":
    print("*" * 100)
    test2()
