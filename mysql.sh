#!/bin/bash
#This script installs mysql (latest build)
#Install MYSQL Server without to check the passwd
mysql_pass=teleskop
export DEBIAN_FRONTEND=noninteractive

 debconf-set-selections <<< 'mysql-server-5.5 mysql-server/root_password password '$mysql_pass''
debconf-set-selections <<< 'mysql-server-5.5 mysql-server/root_password_again password '$mysql_pass''
apt-get -y install mysql-server

#Configure Password and Settings for Remote Access
cp /etc/mysql/my.cnf /etc/mysql/my.bak.cnf

ip=`ifconfig eth0 | grep "inet addr"| cut -d ":" -f2 | cut -d " " -f1` ; sed -i "s/\(bind-address[\t ]*\)=.*/\1= $ip/" /etc/mysql/my.cnf
mysql -uroot -e "UPDATE mysql.user SET Password=PASSWORD('"$mysql_pass"') WHERE User='root'; FLUSH PRIVILEGES;"
sleep 10
mysql -uroot -p$mysql_pass -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY '"$mysql_pass"'; FLUSH PRIVILEGES;"

# change character set to utf8mb4
sed -i '/^\[client\]$/a\default-character-set = utf8mb4' /etc/mysql/my.cnf
sed -i '/^\[mysql\]$/a\default-character-set = utf8mb4' /etc/mysql/my.cnf
sed -i "/^\[mysqld\]/a\init-connect='SET NAMES utf8mb4'\\
init-connect='SET collation_connection = utf8mb4_unicode_ci'\\
character_set_server = utf8mb4\\
collation_server=utf8mb4_unicode_ci\\
skip-character-set-client-handshake" /etc/mysql/my.cnf



#Restart
service mysql restart
echo "MySQL Installation and Configuration is Complete."

