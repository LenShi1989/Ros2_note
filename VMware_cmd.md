# 操作系統更新

```sh
sudo apt update
sudo apt upgrade
```

# 虛擬機無法全屏問題

```sh
sudo apt install open-vm-tools-desktop
sudo reboot
```

# 安裝OpenSSH

```sh
sudo apt install openssh-server    # 安裝ssh
sudo service ssh restart           # 重啟ssh
sudo systemctl enable ssh          # 啟用ssh
sudo service ssh status            # 查看ssh狀態
sudo systemctl enable ssh          # 開機啟動ssh
```
