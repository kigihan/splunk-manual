#!/usr/bin/env python
#    This file is part of python-evtx.
#
#   Copyright 2012, 2013 Willi Ballenthin <william.ballenthin@mandiant.com>
#                    while at Mandiant <http://www.mandiant.com>
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
#   Version v0.1.1
import Evtx.Evtx as evtx
import Evtx.Views as e_views
import re


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Dump a binary EVTX file into XML.")
    parser.add_argument("evtx", type=str,
                        help="Path to the Windows EVTX event log file")
    args = parser.parse_args()

    with evtx.Evtx(args.evtx) as log:
        with open(str(args.evtx)[:-5]+ "_new.xml", "w") as xout:
            xout.write(e_views.XML_HEADER)
            xout.write("<Events>")
            for record in log.records():
                #print(record.xml())
                sx = record.xml().split("\n")
                for lx in sx:
                    lx = lx.replace(" SystemTime=\"", ">").replace("\"></TimeCreated>", "</TimeCreated>")
                    if "<Execution ProcessID=\"" in lx:
                        regex = re.compile(r"ProcessID=\"(\d*)\" ThreadID=\"(\d*)\">")
                        match = regex.search(lx)
                        lx = "<ProcessID>" + match.group(1) + "</ProcessID>\n" \
                             + "<ThreadID>" + match.group(2) + "</ThreadID>"
                    if "<Data Name=\"" in lx:
                        #print("<><><><><>" + lx)
                        regex = re.compile(r"Name=\"(\w*)\">(.*)</Data>")
                        match = regex.search(lx)
                        #print(match.group(1), match.group(2))
                        try:
                            lx = lx.replace("Data Name=\"","").replace("\">",">")[:-5] + match.group(1) + ">"
                        #print("<><><><><>" + lx)
                        except:
                            lx = lx.replace("Data Name=\"","")
                            #print("    [?] " + lx)
                    #print(lx)
                    xout.write(lx + "\n")
                #xout.write(record.xml())
            xout.write("</Events>")


if __name__ == "__main__":
    main()