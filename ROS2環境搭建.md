# 獲取本地編碼

```sh
locale
```

# 檢查編碼環境是否是 UTF-8 環境，如果不是則進行以下設置

```sh
sudo apt update && sudo apt install locales
sudo locale-gen en_US
en_US.UTF-8
sudo update-locale
LC_ALL=en_US.UTF-8
LANG=en_US.UTF-8
export LANG=en_US.UTF-8
```

# 安裝必備倉庫

加載倉庫

```sh
sudo apt install software-properties-common
sudo add -apt-repository universe
```

安裝apt source

拷貝附件ros2-apt-source_1.1.0.noble_all.deb到ubuntu的目錄中

```sh
sudo chomd 777 ros2-apt-source_1.1.0.noble_all.deb    # 修改檔案權限
sudo dpkg -i ros2-apt-source_1.1.0.noble_all.deb      # 安裝檔案
sudo apt update                                       # 更新apt
```
