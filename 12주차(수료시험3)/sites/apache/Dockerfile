FROM httpd:2.4.59-bookworm

RUN grep -q '^LoadModule rewrite_module' /usr/local/apache2/conf/httpd.conf || \
    echo 'LoadModule rewrite_module modules/mod_rewrite.so' >> /usr/local/apache2/conf/httpd.conf && \
    grep -q '^LoadModule proxy_module' /usr/local/apache2/conf/httpd.conf || \
    echo 'LoadModule proxy_module modules/mod_proxy.so' >> /usr/local/apache2/conf/httpd.conf && \
    grep -q '^LoadModule proxy_fcgi_module' /usr/local/apache2/conf/httpd.conf || \
    echo 'LoadModule proxy_fcgi_module modules/mod_proxy_fcgi.so' >> /usr/local/apache2/conf/httpd.conf && \
    printf '\nServerName localhost\nInclude conf/extra/php-disclosure.conf\n' >> /usr/local/apache2/conf/httpd.conf

COPY conf/php-disclosure.conf /usr/local/apache2/conf/extra/php-disclosure.conf