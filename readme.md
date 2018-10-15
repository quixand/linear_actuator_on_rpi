sync to github folder
rsync -nvcaEhi --delete --progress --stats ../door_control/ /media/nick/msi-data/Documents/scripts_and_code/github_projects/linear_actuator_on_rpi

cp -rv garage_automation/ systemd/ garage_control.py readme.md start_door_control.sh wiring-diagram /media/nick/msi-data/Documents/scripts_and_code/github_projects/linear_actuator_on_rpi/