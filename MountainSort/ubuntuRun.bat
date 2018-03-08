title run ubuntu shell
call "C:/Program Files/Oracle/VirtualBox/VBoxManage.exe" startvm "Ubuntu"
call "C:/Program Files/Oracle/VirtualBox/VBoxManage.exe" guestproperty wait "Ubuntu" RDONLYHOST
call "C:/Program Files/Oracle/VirtualBox/VBoxManage.exe" guestcontrol "Ubuntu" run --username alan --password 123ubuntubox --exe /media/sf_UbuntuShare/20171008/p3/tempShell.sh
