import os
import sys

TEMPLATE = """
server {
       listen         80;
       server_name    {{subdomain}}{{domain}};
       return         301 https://{{subdomain}}{{domain}}/;
}

server {
       listen         80;
       server_name    www.{{subdomain}}{{domain}};
       return         301 https://{{subdomain}}{{domain}}/;
}

map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}

proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=cache:100m inactive=60m;

server
{
    listen 443 ssl;
    client_max_body_size 50M;
    server_name {{subdomain}}{{domain}};
    charset utf-8;

    resolver 127.0.0.11 valid=30s ipv6=off;

    ssl_certificate /etc/cert/cert.crt;
    ssl_certificate_key /etc/cert/cert.key;

    location ~ /(.*)/socket.io/$ {
        set $upstream_{{subdomain2}}_socket http://{{redirect}}/$1/socket.io/;
        proxy_http_version 1.1;
        proxy_pass $upstream_{{subdomain2}}_socket;

        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
    }

    location / {
        set $upstream_{{subdomain2}} http://{{redirect}};
        proxy_pass $upstream_{{subdomain2}};

        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        proxy_set_header X-Forwarded-Host {{subdomain}}{{domain}};
        proxy_set_header X-Forwarded-Proto https;

        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;

        proxy_connect_timeout      300;
        proxy_send_timeout         300;
        proxy_read_timeout         300;
        send_timeout               300;

        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Xss-Protection "1; mode=block" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "same-origin";
        add_header Permissions-Policy "autoplay=(), camera=(), geolocation=(), microphone=(), midi=()";
        add_header Content-Security-Policy "default-src https: data: 'self' 'unsafe-inline' 'unsafe-eval';";
        #add_header Content-Security-Policy "default-src https: data: 'self' 'unsafe-inline';";

        proxy_cache cache;
        proxy_cache_valid any 60m;
     }
}
"""

if len(sys.argv) > 1 and sys.argv[1]:
    domain = sys.argv[1]
    with open("services.txt", "rt") as f:
        for line in f:
            if "/" in line and "#" not in line:
                line2 = line.replace("\n", "").replace("\r", "").strip()
                x = line2.split("/")
                subdomain = x[0]
                subdomain2 = x[0].replace("-", "_")
                if subdomain:
                    subdomain = subdomain + "."
                else:
                    subdomain2 = "main"
                txt = (
                    TEMPLATE.replace("{{subdomain}}", subdomain)
                    .replace("{{redirect}}", x[1])
                    .replace("{{subdomain2}}", subdomain2)
                    .replace("{{domain}}", domain)
                )
                file_name = "app/" + subdomain2 + ".conf"
                if not os.path.exists(file_name):
                    with open("app/" + subdomain2 + ".conf", "wt") as f2:
                        f2.write(txt.replace("..", "."))
