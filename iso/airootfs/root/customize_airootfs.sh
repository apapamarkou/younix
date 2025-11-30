#!/usr/bin/env bash
set -e

# Create live user
useradd -m user
echo "user:user" | chpasswd

# Add to wheel group
usermod -aG wheel user

# Set login shell (bash recommended for greetd/hyprland env vars)
chsh -s /usr/bin/fish user

# Copy skel files (redundant normally, but safe)
cp -aT /etc/skel /home/user
chown -R user:user /home/user

# Fix permissions for scripts inside skel-derived home
chmod a+x /home/user/.config/autostart/* 2>/dev/null || true
chmod a+x /home/user/.local/bin/* 2>/dev/null || true
chmod a+x /usr/local/bin/*

sed -i 's/^#en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen
sed -i 's/^#el_GR.UTF-8 UTF-8/el_GR.UTF-8 UTF-8/' /etc/locale.gen
locale-gen
echo "LANG=en_US.UTF-8" > /etc/locale.conf


# Enable services
systemctl enable greetd.service
systemctl enable seatd.service

systemctl disable systemd-networkd.service
systemctl disable systemd-resolved.service
systemctl enable NetworkManager
systemctl enable NetworkManager-wait-online.service

