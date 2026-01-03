#!/bin/bash
PIDFILE="/run/app.pid"

PROGRAM="poetry"
ARGS="run start"
OUTPUT="/proc/1/fd/1"

start() {
  if [ -f "$PIDFILE" ]; then
    echo "Program already running (PID: $(cat $PIDFILE))"
    exit 1
  fi
  
  echo "Starting program..."
  nohup $PROGRAM $ARGS > $OUTPUT 2>&1 &
  echo $! > "$PIDFILE"
  echo "Program started with PID $(cat $PIDFILE)"
}

startfg() {
  if [ -f "$PIDFILE" ]; then
    echo "Program already running (PID: $(cat $PIDFILE))"
    exit 1
  fi
  
  echo "Starting program in foreground..."
  $PROGRAM $ARGS
}

stop() {
  if [ ! -f "$PIDFILE" ]; then
    echo "No PID file found. Is the program running?"
    exit 1
  fi
  
  PID=$(cat "$PIDFILE")
  echo "Stopping program with PID $PID..."
  kill "$PID" && rm -f "$PIDFILE"
  echo "Program stopped."
}

restart() {
  echo "Restarting program..."
  stop
  start
}

case "$1" in
  start)
    start
    ;;
  startfg)
    startfg
    ;;
  stop)
    stop
    ;;
  restart)
    restart
    ;;
  *)
    echo "Usage: $0 {start|startfg|stop|restart}"
    exit 1
    ;;
esac
