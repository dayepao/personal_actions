#!/bin/bash
NAME="onedrive"
REMOTE="server"
LOCAL="/onedrive"
PARAMETER="--contimeout=5s --timeout=5s --tpslimit 10 --transfers 4 --buffer-size 128M --low-level-retries 30 --vfs-read-chunk-size 128M --vfs-read-chunk-size-limit 256M --vfs-cache-mode writes"
case $1 in
    start)
        fusermount -zu ${LOCAL} >/dev/null 2>&1
        if [[ $(pgrep rclone) == "" ]];then
            rm -rf ${LOCAL}
        fi
        mkdir -p ${LOCAL}
        rclone mount ${NAME}:${REMOTE} ${LOCAL} ${PARAMETER} --copy-links --no-gzip-encoding --no-check-certificate --allow-other --allow-non-empty --umask 000
        ;;
    stop)
        fusermount -zu ${LOCAL} >/dev/null 2>&1
        sleep 5
        ;;
    check)
        key="0"
        rclone_log=$(journalctl -b -u rclone -n 3)

        if [[ ${rclone_log} =~ "30/30" ]];then
            key="1"
        elif [[ ${rclone_log} =~ "cannot create directory" ]];then
            key="1"
        fi

        if [[ ${key} == "1" ]];then
            sleep 30
            systemctl restart rclone
        fi
        ;;
    *)
        echo -e "\033[31;1m [错误] \033[0m 参数错误"
        ;;
esac
