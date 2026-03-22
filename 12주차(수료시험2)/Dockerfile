FROM httpd:2.4.59-bookworm

RUN grep -q '^LoadModule rewrite_module' /usr/local/apache2/conf/httpd.conf || \
    echo 'LoadModule rewrite_module modules/mod_rewrite.so' >> /usr/local/apache2/conf/httpd.conf && \
    grep -q '^LoadModule cgid_module' /usr/local/apache2/conf/httpd.conf || \
    echo 'LoadModule cgid_module modules/mod_cgid.so' >> /usr/local/apache2/conf/httpd.conf && \
    printf '\nServerName localhost\nInclude conf/extra/cgi-disclosure.conf\n' >> /usr/local/apache2/conf/httpd.conf

COPY conf/cgi-disclosure.conf /usr/local/apache2/conf/extra/cgi-disclosure.conf