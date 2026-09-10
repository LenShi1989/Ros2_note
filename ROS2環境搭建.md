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
sudo add-apt-repository universe -y
```

安裝apt source

拷貝附件ros2-apt-source_1.1.0.noble_all.deb到ubuntu的目錄中

```sh
sudo chmod 777 ros2-apt-source_1.1.0.noble_all.deb    # 修改檔案權限
sudo dpkg -i ros2-apt-source_1.1.0.noble_all.deb      # 安裝檔案
sudo apt update                                       # 更新apt
```

# ROS必備環境

軟體工具包安裝

```sh
sudo apt update
sudo apt upgrade
sudo apt install tar bzip2 wget -y
sudo apt install ros-dev-tools -y
```

ROS核心庫

```sh
sudo apt install ros-jazzy-desktop -y
```

環境變量配置

```sh
echo 'source /opt/ros/jazzy/setup.bash' >> ~/.bashrc
source ~/.bashrc
```

檢驗ROS2安裝效果
若出現小烏龜視窗則為安裝成功

```sh
ros2 run turtlesim turtlesim_node
```

# 建立專案

`按兩次Tab鍵可以做指令查詢及補齊`

## 安裝查看資料結構tree

```sh
sudo apt install tree
```

## step1 先用mkdir命令把src建好

```sh
mkdir dev_ws/src
```

## step2 運行 colcon build 初始化整個園區

```sh
colcon build
```

## step3 創建包

```sh
cd src
ros2 pkg create --build-type ament_python --node-name my_node my_package
```

## step4 編譯執行packge

```sh
colcon build
source install/setup.bash
ros2 run my_package my_node
```
