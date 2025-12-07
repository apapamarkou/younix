#!/usr/bin/env bash
# shellcheck disable=SC2034

iso_name="younix"
iso_label="ARCH_$(date --date="@${SOURCE_DATE_EPOCH:-$(date +%s)}" +%Y%m)"
iso_publisher="YoUNiX <https://younix.com>"
iso_application="Younix Live/Rescue DVD"
iso_version="$(date --date="@${SOURCE_DATE_EPOCH:-$(date +%s)}" +%Y.%m.%d)"
install_dir="younix"
buildmodes=('iso')
bootmodes=('bios.syslinux'
           'uefi.systemd-boot')
# bootmodes=('bios.syslinux' 'uefi.grub')



grub_cfg="grub/grub.cfg"
pacman_conf="pacman.conf"
airootfs_image_type="squashfs"
airootfs_image_tool_options=('-comp' 'xz' '-Xbcj' 'x86' '-b' '1M' '-Xdict-size' '1M')
bootstrap_tarball_compression=('zstd' '-c' '-T0' '--auto-threads=logical' '--long' '-19')
file_permissions=(
  ["/etc/shadow"]="0:0:400"
  ["/root"]="0:0:750"
  ["/root/.automated_script.sh"]="0:0:755"
  ["/root/.gnupg"]="0:0:700"
  ["/usr/local/bin/choose-mirror"]="0:0:755"
  ["/usr/local/bin/Installation_guide"]="0:0:755"
  ["/usr/local/bin/livecd-sound"]="0:0:755"
  ["/usr/local/bin/starthypr"]="0:0:755"
  ["/etc/skel/.local/bin/*"]="0:0:755"
  ["/etc/skel/.local/bin/appimage-integrator/*"]="0:0:755"
)
