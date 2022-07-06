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
StackOverflow user [nettux](https://stackoverflow.com/users/2814626/) at [StackOverflow](https://stackoverflow.com/a/23828265).  
And some other resources that have helped me:  
- [RL.SE GPRMC Decoder](https://rl.se/gprmc)
- [EQTH.NET NMEA Checksum Calculator](https://nmeachecksum.eqth.net/)
- [BLUECOVER.PT NMEA Analyzer](https://swairlearn.bluecover.pt/nmea_analyser)
