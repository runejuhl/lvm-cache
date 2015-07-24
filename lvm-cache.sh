#!/bin/sh

# place in /etc/initramfs-tools/hooks and make executable to have it
# automatically run on `update-initramfs`

. /usr/share/initramfs-tools/hook-functions

# add modules to initramfs
for x in dm_cache dm_cache_mq dm_persistent_data; do
    manual_add_modules ${x}
done

# copy all libraries needed for cache_check
/usr/local/bin/lddr.py /usr/sbin/cache_check --copy ${DESTDIR}

# copy cache_check binary
mkdir -p ${DESTDIR}/usr/sbin/
cp /usr/sbin/cache_check ${DESTDIR}/usr/sbin/
