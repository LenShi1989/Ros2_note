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
