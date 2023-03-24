community=$(grep community /etc/pymea/config.json| awk '{print $2}' | sed 's/[",]//g')
lat=$(/etc/pymea/snmpget -v2c -Ovq -c$community acu.vessel.local .1.3.6.1.4.1.13745.100.1.1.4.0 2>/dev/null)
lon=$(/etc/pymea/snmpget -v2c -Ovq -c$community acu.vessel.local .1.3.6.1.4.1.13745.100.1.1.5.0 2>/dev/null)
hdg=$(/etc/pymea/snmpget -v2c -Ovq -c$community acu.vessel.local .1.3.6.1.4.1.13745.100.1.1.6.0 2>/dev/null)
echo "latitude: $lat";echo "longitude: $lon";echo "heading: $hdg"
cat /tmp/data.file
