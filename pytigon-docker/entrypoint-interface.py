#!/usr/bin/env python3

import subprocess
import os
import sys
import pwd
from os import environ


if __name__ == "__main__":
    from pytigon_lib.schtools.tools import get_executable
    from pytigon_lib.schtools.main_paths import get_main_paths

    site_packages = [path for path in sys.path if "site-packages" in path][0]

    environ["START_PATH"] = os.path.abspath(os.getcwd())

    if environ.get("LOGS_TO_DOCKER"):
        access_logfile = "--access-logfile -"
        access_log = "--access-log -"
        error_logfile = "--error-logfile -"
    else:
        access_logfile = "--access-logfile /var/log/pytigon-access.log"
        access_log = "--access-log /var/log/pytigon-access.log"
        error_logfile = "--error-logfile /var/log/pytigon-worker-err.log"

    paths = get_main_paths()

    STATIC_PATH = paths["STATIC_PATH"]
    DATA_PATH = paths["DATA_PATH"]
    PRJ_PATH = paths["PRJ_PATH"]
    PRJ_PATH_ALT = paths["PRJ_PATH_ALT"]
    LOCAL_IP = "http://127.0.0.1"

    sys.path.append(PRJ_PATH)
    sys.path.append(PRJ_PATH_ALT)

    env_main = os.environ.copy()
    env_main["PYTHONPATH"] = PRJ_PATH + ":" + PRJ_PATH_ALT
    env_sub = env_main.copy()

    uid, gid = pwd.getpwnam("www-data").pw_uid, pwd.getpwnam("www-data").pw_gid

    os.chown(DATA_PATH, uid, gid)
    os.chown("/var/log", uid, gid)

    os.makedirs("/var/log/nginx", exist_ok=True)

    if not os.path.exists(PRJ_PATH):
        os.makedirs(PRJ_PATH)
        os.chown(PRJ_PATH, uid, gid)

    os.makedirs("/home/www-data/.pytigon/static", exist_ok=True)

    # hack:
    subprocess.Popen("chmod -R 777 /home/www-data/.pytigon/static", shell=True)
    subprocess.Popen("chmod -R 777 %s/pytigon" % site_packages, shell=True)
    # hack end

    VIRTUAL_HOST = environ.get("VIRTUAL_HOST", "localhost")

    if "VIRTUAL_PORT" in environ:
        VIRTUAL_PORT = environ["VIRTUAL_PORT"]
    else:
        VIRTUAL_PORT = "443" if "CERT" in environ else "80"

    VIRTUAL_PORT_80 = environ.get("VIRTUAL_PORT_80", "80")
    PORT_80_REDIRECT = environ.get("PORT_80_REDIRECT")

    if "CERT" in environ:
        cert_parts = environ["CERT"].split(";")
        CRT = "ssl_certificate " + cert_parts[0] + ";"
        KEY = "ssl_certificate_key " + cert_parts[1] + ";"
        VIRTUAL_PORT += " ssl http2"
    else:
        CRT = ""
        KEY = ""

    NGINX_INCLUDE = environ.get("NGINX_INCLUDE")

    # NUMBER_OF_WORKER_PROCESSES formats:
    #   4                          -> main=4, additional=1
    #   4:1                        -> main=4, additional=1
    #   schportal:4,schdevtools:2  -> per-app worker counts
    NOWP = {"default-main": 4, "default-additional": 1}
    nowp_str = environ.get("NUMBER_OF_WORKER_PROCESSES")
    if nowp_str:
        if ":" in nowp_str and ("," in nowp_str or ";" in nowp_str):
            for pos in nowp_str.replace(",", ";").split(";"):
                if ":" in pos:
                    parts = pos.split(":")
                    NOWP[parts[0]] = int(parts[1])
                else:
                    NOWP[pos] = 1
        elif ":" in nowp_str:
            main_n, add_n = nowp_str.split(":")
            NOWP["default-main"] = int(main_n)
            NOWP["default-additional"] = int(add_n)
        else:
            NOWP["default-main"] = int(nowp_str)

    TIMEOUT = environ.get("TIMEOUT", "30")
    ADDITIONAL_TIMEOUT = environ.get("ADDITIONAL_TIMEOUT", TIMEOUT)
    WEBSOCKET_TIMEOUT = environ.get("WEBSOCKET_TIMEOUT", "30")
    MCP_TIMEOUT = environ.get("MCP_TIMEOUT", "300")

    # ASGI_SERVER_NAME: 0=gunicorn, 1=uvicorn, 2=daphne
    ASGI_SERVER_ID = 0
    asgi_name = environ.get("ASGI_SERVER_NAME", "")
    if "uvicorn" in asgi_name:
        ASGI_SERVER_ID = 1
    elif "daphne" in asgi_name:
        ASGI_SERVER_ID = 2

    START_PORT = int(environ.get("START_PORT", "8000"))

    MAIN_PRJ = environ.get("MAIN_PRJ")

    PRJS = []
    if "ADDITIONAL_PROJECTS" in environ:
        PRJS = [
            prj
            for prj in environ["ADDITIONAL_PROJECTS"].replace(",", ";").split(";")
            if prj
        ]

    CFG_SECURITY = """
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Xss-Protection "1; mode=block" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "same-origin";
        add_header Permissions-Policy "autoplay=(), camera=(), geolocation=(), microphone=(), midi=()";
        add_header Content-Security-Policy "default-src https: data: 'self' 'unsafe-inline' 'unsafe-eval' 'wasm-unsafe-eval';";
"""

    CFG_OLD = ""
    if PORT_80_REDIRECT:
        CFG_OLD = f"""server {{
    listen         {VIRTUAL_PORT_80};
    server_name    {VIRTUAL_HOST} www.{VIRTUAL_HOST};
    return         301 {PORT_80_REDIRECT}$request_uri;
}}

"""

    if CRT:
        CFG_START = f"""
server {{
    listen {VIRTUAL_PORT};
    client_max_body_size 50M;
    server_name www.{VIRTUAL_HOST};
    charset utf-8;

    {CRT}
    {KEY}

    return 301 {PORT_80_REDIRECT}$request_uri;
}}"""
    else:
        CFG_START = ""

    CFG_START += f"""

map $http_upgrade $connection_upgrade {{
    default upgrade;
    ''      close;
}}

server {{
    listen {VIRTUAL_PORT};
    client_max_body_size 50M;
    server_name {VIRTUAL_HOST};
    charset utf-8;
    resolver 127.0.0.11 valid=10s ipv6=off;
    resolver_timeout 5s; 
    
    {CRT}
    {KEY}

    location ^~ /static/ {{
        alias {STATIC_PATH}/$PRJ/;
        autoindex on;
        expires 1M;
        add_header Cache-Control "max-age=2629746, public";

    }}

    location /site_media/ {{
        alias {DATA_PATH}/$PRJ/media/;
        autoindex on;
    }}
    location /media_protected/ {{
        internal;
        alias {DATA_PATH}/$PRJ/media_protected/;
    }}
"""

    CFG_ELEM = f"""
    location ^~ /$SUBPRJ/static/ {{
        alias {STATIC_PATH}/$PRJ/;
        autoindex on;
        expires 1M;
        add_header Cache-Control "max-age=2629746, public";
    }}
    location /$SUBPRJ/site_media/ {{
        alias {DATA_PATH}/$SUBPRJ/media/;
        autoindex on;
    }}
    location /$SUBPRJ/media_protected/ {{
        internal;
        alias {DATA_PATH}/$SUBPRJ/media_protected/;
    }}
    location ~ ^/$SUBPRJ/(.*)/channel/$ {{
        proxy_http_version 1.1;

        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        set $$PRJ_backend "{LOCAL_IP}:$PORT2";
        proxy_pass $$PRJ_backend/$SUBPRJ/$1/channel/$is_args$args;

        proxy_connect_timeout       {WEBSOCKET_TIMEOUT};
        proxy_send_timeout          {WEBSOCKET_TIMEOUT};
        proxy_read_timeout          {WEBSOCKET_TIMEOUT};
        send_timeout                {WEBSOCKET_TIMEOUT};
    }}
    location ~ ^/$SUBPRJ/mcp/?$ {{
        proxy_http_version 1.1;
        proxy_set_header Connection "";

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;

        set $$PRJ_backend "{LOCAL_IP}:$PORT2";
        proxy_pass $$PRJ_backend/$SUBPRJ/mcp$is_args$args;

        proxy_buffering off;
        proxy_cache off;
        gzip off;
        proxy_request_buffering off;
        proxy_set_header Accept-Encoding "";

        proxy_connect_timeout       {MCP_TIMEOUT};
        proxy_send_timeout          {MCP_TIMEOUT};
        proxy_read_timeout          {MCP_TIMEOUT};
        send_timeout                {MCP_TIMEOUT};
    }}
    location ~ ^/$SUBPRJ/(.*)$ {{
        set  $$PRJ_backend "{LOCAL_IP}:$PORT/$SUBPRJ";
        proxy_pass $$PRJ_backend/$1$is_args$args;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $remote_addr;

        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;

        proxy_connect_timeout       {TIMEOUT};
        proxy_send_timeout          {TIMEOUT};
        proxy_read_timeout          {TIMEOUT};
        send_timeout                {TIMEOUT};
        [CFG_SECURITY]
    }}
"""

    CFG_END = f"""
    location ~ ^/(.*)/channel/$ {{
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        set $backend_channel "{LOCAL_IP}:$PORT2";
        proxy_pass $backend_channel/$1/channel/$is_args$args;
        
        proxy_connect_timeout       {WEBSOCKET_TIMEOUT};
        proxy_send_timeout          {WEBSOCKET_TIMEOUT};
        proxy_read_timeout          {WEBSOCKET_TIMEOUT};
        send_timeout                {WEBSOCKET_TIMEOUT};
    }}

    location ~ ^/mcp/?$ {{
        proxy_http_version 1.1;
        proxy_set_header Connection "";

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;

        set $backend_mcp "{LOCAL_IP}:$PORT2";
        proxy_pass $backend_mcp/mcp$is_args$args;

        proxy_buffering off;
        proxy_cache off;
        gzip off;
        proxy_request_buffering off;
        proxy_set_header Accept-Encoding "";

        proxy_connect_timeout       {MCP_TIMEOUT};
        proxy_send_timeout          {MCP_TIMEOUT};
        proxy_read_timeout          {MCP_TIMEOUT};
        send_timeout                {MCP_TIMEOUT};
    }}

    location ~ ^/(.*)$ {{
        set $backend "{LOCAL_IP}:$PORT";
        proxy_pass $backend/$1$is_args$args;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_connect_timeout       {TIMEOUT};
        proxy_send_timeout          {TIMEOUT};
        proxy_read_timeout          {TIMEOUT};
        send_timeout                {TIMEOUT};
        [CFG_SECURITY]
    }}
}}
"""

    CFG_ADDITIONAL = f"""
    
server {{
    listen         80;
    server_name    [host] www.[host];
    return         301 https://[host]$request_uri;
}}

server {{
    listen 443 ssl http2;
    client_max_body_size 50M;
    server_name www.[host];
    charset utf-8;

    ssl_certificate /etc/cert/fullchain.pem;
    ssl_certificate_key /etc/cert/privkey.pem;

    return 301 https://[host]$request_uri;
}}

map $http_upgrade $connection_upgrade {{
    default upgrade;
    ''      close;
}}

server {{
    listen 443 ssl http2;
    client_max_body_size 50M;
    server_name [host];
    charset utf-8;

    ssl_certificate /etc/cert/fullchain.pem;
    ssl_certificate_key /etc/cert/privkey.pem;

    location ~ ^/(.*)$ {{
        set $$PRJ_backend http://[service];
        proxy_pass $$PRJ_backend$1$is_args$args;
        
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_connect_timeout       {ADDITIONAL_TIMEOUT};
        proxy_send_timeout          {ADDITIONAL_TIMEOUT};
        proxy_read_timeout          {ADDITIONAL_TIMEOUT};
        send_timeout                {ADDITIONAL_TIMEOUT};
        [CFG_SECURITY]
    }}
}}
"""

    if not environ.get("NO_NGINX_CONF"):
        with open("/etc/nginx/sites-available/pytigon", "wt") as conf:
            if PORT_80_REDIRECT:
                conf.write(CFG_OLD)

            conf.write(CFG_START.replace("$PRJ", MAIN_PRJ))

            port = START_PORT + 2
            port2 = port + 1
            for prj in PRJS:
                if "-" in prj:
                    x = prj.split("-")
                    prj = x[0]
                    subprj = x[1]
                else:
                    subprj = prj
                conf.write(
                    CFG_ELEM.replace("$PRJ", prj)
                    .replace("$SUBPRJ", subprj)
                    .replace("$PORT2", str(port2))
                    .replace("$PORT", str(port))
                    .replace("[CFG_SECURITY]", CFG_SECURITY if CRT else "")
                )
                port += 2
                port2 = port + 1
            if MAIN_PRJ:
                if NGINX_INCLUDE:
                    conf.write("    include %s;\n\n" % NGINX_INCLUDE)
                conf.write(
                    CFG_END.replace("$PORT2", str(START_PORT + 1))
                    .replace("$PORT", str(START_PORT))
                    .replace("[CFG_SECURITY]", CFG_SECURITY if CRT else "")
                )

            if "ADDITIONAL_SERVICES" in environ:
                additional_services = environ["ADDITIONAL_SERVICES"].split(";")
                for item in additional_services:
                    if ":" in item:
                        host, service = item.strip().split(":", 1)
                        prj = service.split(":")[0]
                        conf.write(
                            CFG_ADDITIONAL.replace("[service]", service)
                            .replace("$PRJ", prj)
                            .replace("[host]", host)
                            .replace("[CFG_SECURITY]", CFG_SECURITY)
                        )

    if MAIN_PRJ:
        PRJS.insert(0, MAIN_PRJ)
    else:
        PRJS.insert(0, "")

    port = START_PORT
    ret_tab = []

    if environ.get("RUN_DJANGO", "1") != "0":
        main_prj = True
        for prj in PRJS:
            if not prj:
                main_prj = False
                port += 2
                continue

            subprj = "_"
            if "-" in prj:
                prj, subprj = prj.split("-")

            static_path = os.path.join(DATA_PATH, "static", prj)
            if not os.path.exists(static_path):
                os.makedirs(static_path)
                os.chown(static_path, uid, gid)

            cmd = (
                f"cd /home/www-data/pytigon && su -m www-data -s /bin/sh -c 'cd /home/www-data/pytigon; exec %s -m pytigon.ptig manage_{prj} collectstatic --noinput'"
                % get_executable()
            )

            fnull = open(os.devnull, "w")
            collectstatic = subprocess.Popen(
                cmd, shell=True, stdout=fnull, stderr=subprocess.STDOUT
            )
            collectstatic.wait()
            fnull.close()

            if prj in NOWP:
                count = NOWP[prj]
            else:
                count = (
                    NOWP["default-main"]
                    if prj == MAIN_PRJ
                    else NOWP["default-additional"]
                )

            if ASGI_SERVER_ID == 1:
                server = f"su -m www-data -s /bin/sh -c 'python -m waitress --listen=0.0.0.0:{port} --threads={count} {prj}.wsgi:application'"
            else:
                server = f"python -m gunicorn --preload -b 0.0.0.0:{port} --user www-data -w {count} {access_logfile} {error_logfile} {prj}.wsgi:application -t {TIMEOUT}"

            try:
                x = __import__(prj + ".apps")
            except Exception:
                continue
            if hasattr(x.apps, "NO_ASGI") and x.apps.NO_ASGI:
                asgi_server = None
            else:
                server1 = f"python -m gunicorn --preload -b 0.0.0.0:{port+1} --user www-data -w 1 -k uvicorn.workers.UvicornH11Worker {access_logfile} {error_logfile} {prj}.asgi:application -t {TIMEOUT}"
                server2 = f"su -m www-data -s /bin/sh -c 'python -m uvicorn --host 0.0.0.0 --port {port+1} {prj}.asgi:application'"
                server3 = f"su -m www-data -s /bin/sh -c 'python -m daphne -b 0.0.0.0 -p {port+1} --proxy-headers {access_log} {prj}.asgi:application'"
                asgi_server = (server1, server2, server3)[ASGI_SERVER_ID]

            if main_prj:
                e = env_main
            else:
                env_sub["PUBLISH_IN_SUBFOLDER"] = subprj
                e = env_sub

            cmd = f"{server}"
            print(cmd)
            ret_tab.append(subprocess.Popen(cmd, shell=True, env=e))
            if asgi_server:
                cmd = f"{asgi_server}"
                print(cmd)
                ret_tab.append(subprocess.Popen(cmd, shell=True, env=e))
            port += 2
            main_prj = False

    if environ.get("RUN_TASKS_QUEUE", "0") not in ("", "0"):
        if environ.get("ASYNC_TASKS", "0") not in ("", "0"):
            for prj in PRJS:
                cmd = (
                    "cd /home/www-data/.pytigon && su -m www-data -s /bin/sh -c 'exec %s -m pytigon.pytigon_task %s'"
                    % (get_executable(), prj)
                )
                ret_tab.append(subprocess.Popen(cmd, shell=True))
        else:
            task_queue_prj = environ.get("TASKS_QUEUE_PRJ") or "_schall"
            cmd = (
                "cd /home/www-data/.pytigon && su -m www-data -s /bin/sh -c 'exec %s -m pytigon.ptig manage_%s qcluster'"
                % (get_executable(), task_queue_prj)
            )
            ret_tab.append(subprocess.Popen(cmd, shell=True))

    if environ.get("RUN_NGINX", "1") != "0":
        restart = subprocess.Popen("nginx -g 'daemon off;'", shell=True)
        restart.wait()

    for pos in ret_tab:
        pos.wait()
