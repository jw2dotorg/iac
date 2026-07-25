#CAMERAS=(side garage)   # add your other camera IPs
CAMERAS=(side shed sidegarage driveway front porch backyard garage)
USER=admin
PASS='Trekker-Bagged8-Browse'

for cam in "${CAMERAS[@]}"; do
  echo "== $cam =="

  # 1. Force the clock right now (assumes this box's own time is correct)
  curl --digest -u "$USER:$PASS" -G "http://cam-$cam.jw2.org/cgi-bin/global.cgi" \
    --data-urlencode "action=setCurrentTime" \
    --data-urlencode "time=$(date '+%Y-%m-%d %H:%M:%S')"

  # 2. Push the confirmed NTP + timezone + DST config so it stays correct
  curl --digest -u "$USER:$PASS" \
    "http://cam-$cam.jw2.org/cgi-bin/configManager.cgi?action=setConfig&NTP.Enable=true&NTP.Address=192.168.30.254&NTP.Port=123&NTP.UpdatePeriod=10&NTP.TimeZone=25&Locales.DSTEnable=true&Locales.DSTStart.Month=3&Locales.DSTStart.Week=2&Locales.DSTStart.Day=0&Locales.DSTStart.Hour=2&Locales.DSTStart.Minute=0&Locales.DSTEnd.Month=11&Locales.DSTEnd.Week=1&Locales.DSTEnd.Day=0&Locales.DSTEnd.Hour=2&Locales.DSTEnd.Minute=0"
done
