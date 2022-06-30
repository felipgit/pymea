# pymea
start a threaded tcp stream server.
reading content from a file and pushing every 2 second.
# Install
## Files
git clone $repo
cd $repo
mkdir /etc/pymea/
cp app.py config.json /etc/pymea/
cp pymea.service /etc/systemd/system/
## Service
```bash
systemctl daemon-reload
systemctl enable pymea.service
systemctl start pymea.service
```
## thank you
[nettux](https://stackoverflow.com/users/2814626/) at stackoverflow: https://stackoverflow.com/a/23828265
