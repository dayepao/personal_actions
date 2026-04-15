#!/usr/bin/env bash

# 主要负责关闭系统的函数
function pve_poweroff() {
    logger -t upssched-cmd "准备关闭 PVE..."
    upsmon -c fsd
}

# 判断 upssched 触发的事件
case $1 in
upssched_shutdown)
    logger -t upssched-cmd "触发关机条件, 准备安全关闭系统..."
    pve_poweroff
    ;;
*)
    logger -t upssched-cmd "Unrecognized command: $1"
    ;;
esac
