from sslyze.server_connectivity_tester import ServerConnectivityTester, ServerConnectivityError
from sslyze.synchronous_scanner import SynchronousScanner
from sslyze.concurrent_scanner import ConcurrentScanner, PluginRaisedExceptionScanResult
from sslyze.plugins.openssl_cipher_suites_plugin import Sslv30ScanCommand, Tlsv10ScanCommand, Sslv20ScanCommand, Tlsv11ScanCommand, Tlsv12ScanCommand
from sslyze.plugins.heartbleed_plugin import HeartbleedScanCommand
from sslyze.plugins.http_headers_plugin import HttpHeadersScanCommand
from sslyze.plugins.robot_plugin import RobotScanCommand
from sslyze.plugins.certificate_info_plugin import CertificateInfoScanCommand
from robot.api import logger
import json

class RoboSslyze(object):
    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def __init__(self):
        logger.info("Sslyze initialized")
        self.results = {}

    def test_ssl_basic(self, hostname, port = 443):
        '''
        Uses the `ServerConnectivityTester` functionality of SSlyze to perform a basic test.
        Port defaults to 443 unless provided otherwise
        hostname is mandatory

        | test ssl basic  | hostname  | port (optional |

        '''
        try:
            tester = ServerConnectivityTester(hostname=hostname, port=port)
            server_info = tester.perform()

            scanner = ConcurrentScanner()
            # scanner.queue_scan_command(info, certificate_info_plugin.CertificateInfoScanCommand())
            scanner.queue_scan_command(server_info, Sslv20ScanCommand())
            scanner.queue_scan_command(server_info, Sslv30ScanCommand())
            scanner.queue_scan_command(server_info, Tlsv10ScanCommand())
            scanner.queue_scan_command(server_info, Tlsv10ScanCommand())
            scanner.queue_scan_command(server_info, Tlsv11ScanCommand())
            scanner.queue_scan_command(server_info, Tlsv12ScanCommand())
            scanner.queue_scan_command(server_info, HeartbleedScanCommand())
            scanner.queue_scan_command(server_info, RobotScanCommand())
            # scanner.queue_scan_command(server_info, CertificateInfoScanCommand())

            for scan_result in scanner.get_results():
                # logger.info("Scan result for: {} on hostname: {}".format(scan_result.scan_command.__class__.__name__, scan_result.server_info.hostname))

                if isinstance(scan_result, PluginRaisedExceptionScanResult):
                    raise Exception("Scan Command Failed: {}".format(scan_result.as_text()))

                if isinstance(scan_result.scan_command, Sslv20ScanCommand):
                    if scan_result.accepted_cipher_list:
                        logger.warn("SSLv2 ciphersuites accepted")
                        self.results['SSLv2'] = {}
                        self.results['SSLv2']['Description'] = "This server supports SSLv2 which is a known-insecure SSL/TLS negotiation protocol"
                        self.results['SSLv2']['CWE'] = 326
                        self.results['SSLv2']['suites'] = []
                        for suite in scan_result.accepted_cipher_list:
                            logger.info("\t{}".format(suite.name))
                            self.results['SSLv2']['suites'].append(suite.name)
                    else:
                        logger.info("SSLv2 ciphersuites not accepted")

                if isinstance(scan_result.scan_command, Sslv30ScanCommand):
                    if scan_result.accepted_cipher_list:
                        logger.warn("SSLv3 Cipher Suites accepted")
                        self.results['SSLv3'] = {}
                        self.results['SSLv3']['Description'] = "This server supports SSLv3 which is a known-insecure SSL/TLS negotiation protocol"
                        self.results['SSLv3']['CWE'] = 326
                        self.results['SSLv3']['suites'] = []
                        for suite in scan_result.accepted_cipher_list:
                            logger.info("\t{}".format(suite.name))
                            self.results['SSLv3']['suites'].append(suite.name)
                    else:
                        logger.info("SSLv3 ciphersuites not accepted")

                if isinstance(scan_result.scan_command, Tlsv10ScanCommand):
                    if scan_result.accepted_cipher_list:
                        logger.warn("TLSv1 Cipher Suites accepted")
                        self.results['TLSv1'] = {}
                        self.results['TLSv1']['CWE'] = 326
                        self.results['TLSv1']['suites'] = []
                        for suite in scan_result.accepted_cipher_list:
                            logger.info("\t{}".format(suite.name))
                            self.results['TLSv1']['suites'].append(suite.name)
                    else:
                        logger.info("TLSv1 ciphersuites not accepted")

                if isinstance(scan_result.scan_command, Tlsv11ScanCommand):
                    if scan_result.accepted_cipher_list:
                        logger.info("TLSv1.1 Cipher Suites accepted")
                        self.results['TLSv1.1'] = {}
                        self.results['TLSv1.1']['suites'] = []
                        for suite in scan_result.accepted_cipher_list:
                            logger.info("\t{}".format(suite.name))
                            self.results['TLSv1.1']['suites'].append(suite.name)
                    else:
                        logger.info("TLSv1.1 ciphersuites not accepted")

                if isinstance(scan_result.scan_command, Tlsv12ScanCommand):
                    if scan_result.accepted_cipher_list:
                        logger.info("TLSv1.2 Cipher Suites accepted")
                        self.results['TLSv1.2'] = {}
                        self.results['TLSv1.2']['suites'] = []
                        for suite in scan_result.accepted_cipher_list:
                            logger.info("\t{}".format(suite.name))
                            self.results['TLSv1.2']['suites'].append(suite.name)
                    else:
                        logger.info("TLSv1.2 ciphersuites not accepted")

                if isinstance(scan_result.scan_command, HeartbleedScanCommand):
                    if scan_result.is_vulnerable_to_heartbleed:
                        logger.warn("Server TLS implementation is vulnerable to Heartbleed")
                        self.results['Heartbleed'] = {}

                        self.results['Heartbleed']['CWE'] = 126
                    else:
                        logger.info("Server TLS Implementation not vulnerable to Heartbleed")

                if isinstance(scan_result.scan_command, RobotScanCommand):
                    logger.info("Test for ROBOT Vulnerability")
                    if scan_result.robot_result_enum.NOT_VULNERABLE_NO_ORACLE:
                        logger.info("\tNot Vulnerable: The server supports RSA cipher suites but does not act as an oracle")
                    elif scan_result.robot_result_enum.VULNERABLE_WEAK_ORACLE:
                        logger.warn("\tVulnerable: The server is vulnerable but the attack would take too long")
                    elif scan_result.robot_result_enum.VULNERABLE_STRONG_ORACLE:
                        self.results['ROBOT Vulnerability'] = {}
                        self.results['ROBOT Vulnerability']["Description"] = "TLS implementations may disclose side channel information via discrepancies between valid and invalid PKCS#1 padding, and may therefore be vulnerable to Bleichenbacher-style attacks. This attack is known as a \"ROBOT attack\"."
                        self.results['Heartbleed']['CWE'] = 203
                        logger.warn("\tVulnerable: The server is vulnerable and real attacks are feasible")
                    elif scan_result.robot_result_enum.NOT_VULNERABLE_RSA_NOT_SUPPORTED:
                        logger.info("\tNot Vulnerable: The server does not supports RSA cipher suites")
                    else:
                        logger.info("\tUnable to determine if implementation is vulnerable")


                # if isinstance(scan_result.scan_command, CertificateInfoScanCommand):
                #     logger.info(u'Server Certificate CN: {}'.format(
                #         dict(scan_result.certificate_chain[0])[u'subject'][u'commonName']
                #     ))


        except ServerConnectivityError as e:
            logger.error('Error when trying to connect to {}: {}'.format(e.server_info.hostname, e.error_message))


    def test_ssl_server_headers(self, hostname, port = 443):
        '''
                Uses the ServerConnectivityTester to identify host headers specific to TLS/SSL implementations to identify
                apparent security flaws with SSL/TLS implementations at the web server level.

                Currently, we can enumerate HSTS and Expect-CT Headers. HPKP is available, but is not being included because
                its being deprecated by Chrome.

                | test ssl server headers  | hostname  | port (optional |

        '''
        try:
            tester = ServerConnectivityTester(hostname = hostname, port = port)
            server_info = tester.perform()

            scanner = SynchronousScanner()
            result = scanner.run_scan_command(server_info, HttpHeadersScanCommand())
            logger.info("Test for HSTS Header")

            if result.hsts_header:
                preload = result.hsts_header.preload
                include_subdomains = result.hsts_header.include_subdomains
                max_age = result.hsts_header.max_age
                logger.info("\tHSTS Header with Preload: {}, Include Subdomains: {} and max_age: {}".format(preload, include_subdomains, max_age))
            else:
                self.results['HSTS'] = {}
                self.results['HSTS']['Description'] = "No HTTP Strict Transport Security configured for the application"
                self.results['HSTS']['CWE'] = 16
                logger.warn("\tNo HSTS Header found")

            logger.info("Test for Expect-CT Header")
            if result.expect_ct_header:
                logger.info("\tExpect-CT Header found: {}".format(result.expect_ct_header))
            else:
                logger.warn("\tNo Expect-CT Header found.")
                self.results['Expect-CT'] = {}
                self.results['Expect-CT']['Description'] = "The Expect-CT header allows sites to opt in to reporting and/or enforcement of Certificate Transparency requirements, which prevents the use of misissued certificates for that site from going unnoticed."
                self.results['Expect-CT']['CWE'] = 16


        except ServerConnectivityError as e:
            logger.error('Error when trying to connect to {}: {}'.format(e.server_info.hostname, e.error_message))



    def write_results_to_json_file(self, json_file = 'sslyze.json'):
        '''
        Writes a JSON report with the findings of the SSLyze run.

        | write results to json file  | json_file (optional full path) |

        '''
        with open(json_file, 'w') as resultfile:
            resultfile.write(json.dumps(self.results))