# Logging Module

This library can handle colored log-output and write directly into a logfile.

## Init
```
#!/usr/bin/env python3

import logbuddy

log = logbuddy.log()
```

## Loglevel
At the moment there are a few loglevels defined by default.
- [x] Info
- [x] Warning
- [x] Error
- [x] Pass
- [X] Debug

```
log.Pass("I am a pass-message")
log.Warn("I am a warning-message")
log.Error("I am an error-message")
log.Debug("I am a debug-message")
log.Info("I am an info-message")
```

## Change the color of the levels
```
log.Info("I am an info-message")

log.setInfo("\x1b[1;36m")

log.Info("And now I have a different color")
``` 

## If you don't like colors
```
log.setColor(False)
```

## Need a logfile?
```
log.setLogfile("somelogfile")
```

## Need a logfile with date?
```
log.setLogfile("somelogfile")
log.setLogfileDate(True)
```

## Future Plans
- [ ] Creating your own loglevels
