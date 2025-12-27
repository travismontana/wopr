sysctl fs.inotify.max_user_watches=1048576
sysctl fs.inotify.max_user_instances=1024

find /proc/*/fd -lname 'anon_inode:inotify' 2>/dev/null | cut -d'/' -f3 | xargs -I '{}' ps -p '{}' -o pid,comm= | sort | uniq -c | sort -nr | head -20


