import xml.etree.cElementTree as et
import subprocess
import pathlib
from django.conf import settings


def generate_xml_report(file_name):
    subprocess.call(
        f"nmap -A -T5 --privilege --min-hostgroup 256 --min-parallelism 100 -iL {settings.SITE_ROOT}/attack_eye/apps/amass/generated_subdomains/{file_name}.txt -oX {settings.SITE_ROOT}/attack_eye/apps/nmap/port_scanning_reports/{file_name}.xml", shell=True,)


def parse_nmap_xml_report(xml_file_name: str, host_name: str):
    try:
        tree = et.parse(f'{settings.SITE_ROOT}/attack_eye/apps/nmap/port_scanning_reports/{xml_file_name}.xml')
    except:
        return f'No XML file with name {xml_file_name}.xml'
    root = tree.getroot()

    for host in root.iter('host'):
        if host.find('hostnames').find('hostname').attrib['name'] == host_name:
            def closedPorts():
                return host.find('ports').findall('extraports')[1].attrib['count'] if len(host.find('ports').findall('extraports')) > 1 else None

            def CPE(port):
                return port.find('service').find('cpe').text if port.find('service').find('cpe') is not None else None

            def closedPortUsedOs():
                return host.find('os').findall('portused')[1].attrib if len(host.find('os').findall('portused')) > 1 else None

            report = {"host": host.find('hostnames').find('hostname').attrib['name'], "address": host.find('address').attrib['addr'], "filtered_ports": host.find('ports').findall('extraports')[0].attrib['count'], "closed_ports": closedPorts(), "open_ports": [{"protocol": port.attrib['protocol'], "port_id": port.attrib['portid'], "state": port.find('state').attrib['state'], "services": port.find(
                'service').attrib, "cpe": CPE(port)} for port in host.find('ports').findall('port')], "open_port_used_os": host.find('os').find('portused').attrib, "closed_port_used_os": closedPortUsedOs(), "os_detail": [{"os_match": os.attrib, "os_class": os.find('osclass').attrib, "cpe": os.find('osclass').find('cpe').text} for os in host.find('os').findall('osmatch')], "trace_route_port": host.find('trace').attrib, "hops": [hop.attrib for hop in host.find('trace').findall('hop')]}

            return report

    return f'No host with name {host_name}'


# print(parse_nmap_xml_report('testscan', 'example.com'))
