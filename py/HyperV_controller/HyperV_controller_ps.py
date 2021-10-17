import re

from utils_dayepao import cmd_dayepao

# (Get-VM).Name
# (Get-VM -Name '{vm_name}').State
# Get-VMProcessor -VMName '下载' | Format-List
# Set-VMProcessor -VMName "下载" -ExposeVirtualizationExtensions $true
# Set-VMProcessor -VMName "下载" -Count 2 -Reserve 10 -Maximum 75 -RelativeWeight 200


def get_vms():
    vms = {}
    ps = "Get-VM | ForEach-Object {\"Name: \" + $_.Name + \" State: \" + $_.State}"
    out_queue = cmd_dayepao(["powershell", ps])[0]
    while (ps_result := out_queue.get()) != b"":
        re_result = re.match(re.compile(r'Name: (.+?) State: (.+?)$'), ps_result)
        if re_result:
            vms[re_result.group(1)] = re_result.group(2)
    return vms


def get_vmprocessor(vm_name: str):
    vmprocessor = {}
    ps = "Get-VMProcessor -VMName '{vm_name}' | Format-List | Out-String -Stream -Width 200".format(vm_name=vm_name)
    out_queue = cmd_dayepao(["powershell", ps])[0]
    while (ps_result := out_queue.get()) != b"":
        re_result = re.match(re.compile(r'(.*?) : (.*)$'), ps_result)
        if re_result:
            vmprocessor[re_result.group(1).strip()] = re_result.group(2).strip()
    return vmprocessor


def set_vmprocessor(vm_name: str, config: dict):
    result = []
    ps = "Set-VMProcessor -VMName \"{vm_name}\"".format(vm_name=vm_name)
    for key, value in config.items():
        ps = ps + " -{key} {value}".format(key=key, value=value)
    err_queue = cmd_dayepao(["powershell", ps])[1]
    while (ps_result := err_queue.get()) != b"":
        result.append(ps_result)
    return (not bool(result), result)


if __name__ == "__main__":
    print(get_vms())
    # print(set_vmprocessor("杂项", {"ExposeVirtualizationExtensions": "$false"}))
    print(get_vmprocessor("杂项")["ExposeVirtualizationExtensions"])
