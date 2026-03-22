LogLevel warn rewrite:trace3

DocumentRoot "/usr/local/apache2/htdocs"

<Directory "/usr/local/apache2/htdocs">
    Require all granted
    AllowOverride None
</Directory>

<Directory "/usr/local/apache2/cgi-bin">
    Require all granted
</Directory>

RewriteEngine On
RewriteRule "^/html/(.*)$" "/$1.html" [L]