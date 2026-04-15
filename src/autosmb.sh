#!/bin/bash
MOUNT_PATHS=()
for mount_path in $(grep "^[^#]*//192.168.1.3" /etc/fstab | sed "s/^ //g" | sed "s/\/\/192.168.1.3\/.* \(\/mnt\/.*\) cifs.*/\1/g")
do
    MOUNT_PATHS[${#MOUNT_PATHS[*]}]=${mount_path}
done

case $1 in
    start)
        mount -a
        ;;
    stop)
        for mount_path in ${MOUNT_PATHS[*]}
        do
            echo "umount ${mount_path}"
            umount ${mount_path}
        done
        ;;
    check)
        for mount_path in ${MOUNT_PATHS[*]}
        do
            if [[ $(mount | grep ${mount_path}) == "" ]];then
                echo "${mount_path} has been unmounted, restarting..."
                mount ${mount_path}
            fi
        done
        ;;
    *)
        echo -e "\033[31;1m [错误] \033[0m 参数错误"
        ;;
esac
