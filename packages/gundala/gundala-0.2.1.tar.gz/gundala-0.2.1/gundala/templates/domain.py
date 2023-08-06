available = """<?xml version="1.0" encoding="UTF-8"?>
        <epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
            <command>
                <check>
                    <domain:check xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
                        <domain:name>%s</domain:name>
                    </domain:check>
                </check>
            </command>
        </epp>"""

create = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<epp xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:epp="urn:ietf:params:xml:ns:epp-1.0"
    xmlns:domain="urn:ietf:params:xml:ns:domain-1.0" xmlns:cozadomain="http://co.za/epp/extensions/cozadomain-1-0"
    xsi:schemaLocation="urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd">
    <command>
        <create>
            <domain:create xsi:schemaLocation="urn:ietf:params:xml:ns:domain-1.0 domain-1.0.xsd">
                <domain:name>%(domain)s</domain:name>
                <domain:period unit="y">%(regperiod)s</domain:period>
                <domain:ns>%(ns)s</domain:ns>
                <domain:registrant>%(registrant)s</domain:registrant>
                <domain:authInfo>
                    <domain:pw>%(eppcode)s</domain:pw>
                </domain:authInfo>
                <domain:contact type="admin">%(registrant)s</domain:contact>
                <domain:contact type="tech">%(registrant)s</domain:contact>
                <domain:contact type="billing">%(registrant)s</domain:contact>
            </domain:create>
        </create>
    </command>
</epp>"""

canceldelete = """<?xml version="1.0" encoding="UTF-8"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
    <extension>
        <sidn-ext-epp:command
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
 xmlns:sidn-ext-epp="http://rxsd.domain-registry.nl/sidn-ext-epp-1.0">
            <sidn-ext-epp:domainCancelDelete>
                <sidn-ext-epp:name>%s</sidn-ext-epp:name>
            </sidn-ext-epp:domainCancelDelete>
            <sidn-ext-epp:clTRID>OMVDC10T10</sidn-ext-epp:clTRID>
        </sidn-ext-epp:command>
    </extension>
</epp>"""

delete = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
 <epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
   <command>
     <delete>
       <domain:delete
        xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
         <domain:name>%s</domain:name>
       </domain:delete>
     </delete>
     <clTRID>TestVWDNC10T20</clTRID>
   </command>
 </epp>"""

info = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
  <command>
    <info>
      <domain:info xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name hosts="all">%s</domain:name>
      </domain:info>
    </info>
    <clTRID>ABC-12345</clTRID>
  </command>
</epp>"""

login = """<?xml version="1.0" encoding="UTF-8"?>
        <epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
            <command>
                <login>
                    <clID>%(user)s</clID>
                    <pw>%(pass)s</pw>
                    <options>
                        <version>1.0</version>
                        <lang>en</lang>
                    </options>
                    <svcs>
                        <objURI>urn:ietf:params:xml:ns:domain-1.0</objURI>
                        <objURI>urn:ietf:params:xml:ns:contact-1.0</objURI>
                    </svcs>
                </login>
            </command>
        </epp>"""

logout = """<?xml version="1.0" encoding="UTF-8"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi:schemaLocation="urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd">
    <command>
        <logout/>
    </command>
</epp>"""

nameserver = """<?xml version="1.0" encoding="UTF-8" standalone="no"?> <epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
  <command>
     <info>
<host:info xmlns:host="urn:ietf:params:xml:ns:host-1.0"> <host:name>%s</host:name>
       </host:info>
     </info>
     <clTRID>ABC-12345</clTRID>
  </command>
</epp>"""

poll = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
    <command>
        <poll op="req"/>
        <clTRID>ABC-12345</clTRID>
    </command>
</epp>"""

transfer = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
  <command>
    <transfer op="request">
      <domain:transfer
       xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name>%(domain)s</domain:name>
        <domain:authInfo>
          <domain:pw>%(token)s</domain:pw>
        </domain:authInfo>
      </domain:transfer>
    </transfer>
    <clTRID>C0101C10T10</clTRID>
  </command>
</epp>"""

transferstatus = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
  <command>
    <transfer op="query">
      <domain:transfer
         xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name>%s</domain:name>
      </domain:transfer>
    </transfer>
    <clTRID>CHKTEST1</clTRID>
  </command>
</epp>"""
