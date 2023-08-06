#!/usr/bin/env python
"""
NAME
    iodp_srm_magic.py

DESCRIPTION
    converts IODP LIMS and LORE SRM archive half sample format files to measurements format files

SYNTAX
    iodp_srm_magic.py [command line options]

OPTIONS
    -h: prints the help message and quits.
    -ID: directory for input file if not included in -f flag
    -f FILE: specify infile file, required
    -WD: directory to output files to (default : current directory)
    -F FILE: specify output  measurements file, default is measurements.txt
    -Fsp FILE: specify output specimens.txt file, default is specimens.txt
    -Fsa FILE: specify output samples.txt file, default is samples.txt
    -Fsi FILE: specify output sites.txt file, default is sites.txt
    -Flo FILE: specify output locations.txt file, default is locations.txt
    -lat LAT: latitude of site (also used as bounding latitude for location)
    -lon LON: longitude of site (also used as bounding longitude for location)
    -A: don't average replicate measurements

INPUTS
    IODP .csv file format exported from LIMS database
"""
from __future__ import print_function
from builtins import str
from builtins import range
import sys
import os
import time
import pmagpy.pmag as pmag
import pmagpy.new_builder as nb
import datetime
import functools


def convert(**kwargs):
    # initialize defaults
    version_num = pmag.get_version()
    citations = "This study"
    dir_path, demag = '.', 'NRM'
    depth_method = 'a'

    dir_path = kwargs.get('dir_path', '.')
    input_dir_path = kwargs.get('input_dir_path', dir_path)
    output_dir_path = dir_path  # rename dir_path after input_dir_path is set
    noave = kwargs.get('noave', 0)  # default (0) is DO average
    csv_file = kwargs.get('csv_file', '')
    meas_file = kwargs.get('meas_file', 'measurements.txt')
    spec_file = kwargs.get('spec_file', 'specimens.txt')
    samp_file = kwargs.get('samp_file', 'samples.txt')
    site_file = kwargs.get('site_file', 'sites.txt')
    loc_file = kwargs.get('loc_file', 'locations.txt')
    lat = kwargs.get('lat', '')
    lon = kwargs.get('lon', '')

    # format variables
    if csv_file == "":
        # read in list of files to import
        filelist = os.listdir(input_dir_path)
    else:
        filelist = [csv_file]

    # parsing the data
    MeasRecs, SpecRecs, SampRecs, SiteRecs, LocRecs = [], [], [], [], []
    file_found = False
    for f in filelist:  # parse each file
        year_warning = True
        if f[-3:].lower() == 'csv':
            print('processing:', f)
            file_found = True
            # get correct full filename and read data
            fname = pmag.resolve_file_name(f, input_dir_path)
            full_file = open(fname)
            file_input = full_file.readlines()
            full_file.close()
            keys = file_input[0].replace('\n', '').split(
                ',')  # splits on underscores
            keys = [k.strip('"') for k in keys]
            if "Interval Top (cm) on SHLF" in keys:
                interval_key = "Interval Top (cm) on SHLF"
            elif " Interval Bot (cm) on SECT" in keys:
                interval_key = " Interval Bot (cm) on SECT"
            elif "Offset (cm)" in keys:
                interval_key = "Offset (cm)"
            else:
                print("couldn't find interval or offset amount")
            # get depth key
            if "Top Depth (m)" in keys:
                depth_key = "Top Depth (m)"
            elif "CSF-A Top (m)" in keys:
                depth_key = "CSF-A Top (m)"
            elif "Depth CSF-A (m)" in keys:
                depth_key = "Depth CSF-A (m)"
            else:
                print("couldn't find depth")
            # get comp depth key
            if "CSF-B Top (m)" in keys:
                comp_depth_key = "CSF-B Top (m)"  # use this model if available
            elif "Depth CSF-B (m)" in keys:
                comp_depth_key = "Depth CSF-B (m)"
            else:
                comp_depth_key = ""
                print("couldn't find composite depth")
            if "Demag level (mT)" in keys:
                demag_key = "Demag level (mT)"
            elif "Demag Level (mT)" in keys:
                demag_key = "Demag Level (mT)"
            elif "Treatment Value" in keys:
                demag_key = "Treatment Value"
            else:
                print("couldn't find demag type")
            # Get inclination key
            if "Inclination (Tray- and Bkgrd-Corrected) (deg)" in keys:
                inc_key = "Inclination (Tray- and Bkgrd-Corrected) (deg)"
            elif "Inclination background + tray corrected  (deg)" in keys:
                inc_key = "Inclination background + tray corrected  (deg)"
            elif "Inclination background + tray corrected  (\xc2\xb0)" in keys:
                inc_key = "Inclination background + tray corrected  (\xc2\xb0)"
            elif "Inclination background &amp; tray corrected (deg)" in keys:
                inc_key = "Inclination background &amp; tray corrected (deg)"
            elif "Inclination background & tray corrected (deg)" in keys:
                inc_key = "Inclination background & tray corrected (deg)"
            elif "Inclination background & drift corrected (deg)" in keys:
                inc_key = "Inclination background & drift corrected (deg)"
            elif "Inclination background + tray corrected  (\N{DEGREE SIGN})" in keys:
                inc_key = "Inclination background + tray corrected  (\N{DEGREE SIGN})"
            else:
                print("couldn't find inclination")
            # get declination key
            if "Declination (Tray- and Bkgrd-Corrected) (deg)" in keys:
                dec_key = "Declination (Tray- and Bkgrd-Corrected) (deg)"
            elif "Declination background + tray corrected (\N{DEGREE SIGN})" in keys:
                dec_key = "Declination background + tray corrected (\N{DEGREE SIGN})"
            elif "Declination background + tray corrected (deg)" in keys:
                dec_key = "Declination background + tray corrected (deg)"
            elif "Declination background + tray corrected (\xc2\xb0)" in keys:
                dec_key = "Declination background + tray corrected (\xc2\xb0)"
            elif "Declination background &amp; tray corrected (deg)" in keys:
                dec_key = "Declination background &amp; tray corrected (deg)"
            elif "Declination background & tray corrected (deg)" in keys:
                dec_key = "Declination background & tray corrected (deg)"
            elif "Declination background & drift corrected (deg)" in keys:
                dec_key = "Declination background & drift corrected (deg)"
            else:
                print("couldn't find declination")
            if "Intensity (Tray- and Bkgrd-Corrected) (A/m)" in keys:
                int_key = "Intensity (Tray- and Bkgrd-Corrected) (A/m)"
            elif "Intensity background + tray corrected  (A/m)" in keys:
                int_key = "Intensity background + tray corrected  (A/m)"
            elif "Intensity background &amp; tray corrected (A/m)" in keys:
                int_key = "Intensity background &amp; tray corrected (A/m)"
            elif "Intensity background & tray corrected (A/m)" in keys:
                int_key = "Intensity background & tray corrected (A/m)"
            elif "Intensity background & drift corrected (A/m)" in keys:
                int_key = "Intensity background & drift corrected (A/m)"
            else:
                print("couldn't find magnetic moment")
            if "Core Type" in keys:
                core_type = "Core Type"
            elif "Type" in keys:
                core_type = "Type"
            else:
                print("couldn't find core type")
            if 'Run Number' in keys:
                run_number_key = 'Run Number'
            elif 'Test No.' in keys:
                run_number_key = 'Test No.'
            else:
                print("couldn't find run number")
            if 'Test Changed On' in keys:
                date_key = 'Test Changed On'
            elif "Timestamp (UTC)" in keys:
                date_key = "Timestamp (UTC)"
            else:
                print("couldn't find timestamp")
            if "Section" in keys:
                sect_key = "Section"
            elif "Sect" in keys:
                sect_key = "Sect"
            else:
                print("couldn't find section number")
            if 'Section Half' in keys:
                half_key = 'Section Half'
            elif "A/W" in keys:
                half_key = "A/W"
            else:
                print("couldn't find half number")
            if "Text ID" in keys:
                text_id = "Text ID"
            elif "Text Id" in keys:
                text_id = "Text Id"
            else:
                print("couldn't find ID number")
            for line in file_input[1:]:
                InRec = {}
                test = 0
                recs = line.split(',')
                for k in range(len(keys)):
                    if len(recs) == len(keys):
                        InRec[keys[k]] = line.split(',')[k].strip(""" " ' """)
                if 'Exp' in list(InRec.keys()) and InRec['Exp'] != "":
                    # get rid of pesky blank lines (why is this a thing?)
                    test = 1
                if not test:
                    continue
                run_number = ""
                inst = "IODP-SRM"
                volume = '15.59'  # set default volume to this
                if 'Sample Area (cm?)' in list(InRec.keys()) and InRec['Sample Area (cm?)'] != "":
                    volume = InRec['Sample Area (cm?)']
                MeasRec, SpecRec, SampRec, SiteRec, LocRec = {}, {}, {}, {}, {}
                expedition = InRec['Exp']
                location = InRec['Site']+InRec['Hole']
# Maintain backward compatibility for the ever-changing LIMS format (Argh!)
                while len(InRec['Core']) < 3:
                    InRec['Core'] = '0'+InRec['Core']
                # assume discrete sample
                if "Last Tray Measurment" in list(InRec.keys()) and "SHLF" not in InRec[text_id] or 'dscr' in csv_file:
                    specimen = expedition+'-'+location+'-' + \
                        InRec['Core']+InRec[core_type]+"-"+InRec[sect_key] + \
                        '-'+InRec[half_key]+'-'+str(InRec[interval_key])
                else:  # mark as continuous measurements
                    specimen = expedition+'-'+location+'-' + \
                        InRec['Core']+InRec[core_type]+"_"+InRec[sect_key] + \
                        InRec[half_key]+'-'+str(InRec[interval_key])
                sample = expedition+'-'+location + \
                    '-'+InRec['Core']+InRec[core_type]
                site = expedition+'-'+location

                if not InRec[dec_key] or not InRec[inc_key]:
                    print("No dec or inc found for specimen %s, skipping" % specimen)
                    continue

                if specimen != "" and specimen not in [x['specimen'] if 'specimen' in list(x.keys()) else "" for x in SpecRecs]:
                    SpecRec['specimen'] = specimen
                    SpecRec['sample'] = sample
                    SpecRec['citations'] = citations
                    SpecRec['volume'] = volume
                    SpecRec['specimen_alternatives'] = InRec[text_id]
                    SpecRecs.append(SpecRec)
                if sample != "" and sample not in [x['sample'] if 'sample' in list(x.keys()) else "" for x in SampRecs]:
                    SampRec['sample'] = sample
                    SampRec['site'] = site
                    SampRec['citations'] = citations
                    SampRec['azimuth'] = '0'
                    SampRec['dip'] = '0'
                    SampRec['core_depth'] = InRec[depth_key]
                    if comp_depth_key != '':
                        SampRec['composite_depth'] = InRec[comp_depth_key]
                        SiteRec['composite_depth'] = InRec[comp_depth_key]
                    if "SHLF" not in InRec[text_id]:
                        SampRec['method_codes'] = 'FS-C-DRILL-IODP:SP-SS-C:SO-V'
                    else:
                        SampRec['method_codes'] = 'FS-C-DRILL-IODP:SO-V'
                    SampRecs.append(SampRec)
                if site != "" and site not in [x['site'] if 'site' in list(x.keys()) else "" for x in SiteRecs]:
                    SiteRec['site'] = site
                    SiteRec['location'] = location
                    SiteRec['citations'] = citations
                    SiteRec['lat'] = lat
                    SiteRec['lon'] = lon
                    SiteRecs.append(SiteRec)
                    SiteRec['core_depth'] = InRec[depth_key]
                if location != "" and location not in [x['location'] if 'location' in list(x.keys()) else "" for x in LocRecs]:
                    LocRec['location'] = location
                    LocRec['citations'] = citations
                    LocRec['expedition_name'] = expedition
                    LocRec['lat_n'] = lat
                    LocRec['lon_e'] = lon
                    LocRec['lat_s'] = lat
                    LocRec['lon_w'] = lon
                    LocRecs.append(LocRec)

                MeasRec['specimen'] = specimen
                MeasRec['software_packages'] = version_num
                MeasRec["treat_temp"] = '%8.3e' % (273)  # room temp in kelvin
                MeasRec["meas_temp"] = '%8.3e' % (273)  # room temp in kelvin
                MeasRec["treat_ac_field"] = 0
                MeasRec["treat_dc_field"] = '0'
                MeasRec["treat_dc_field_phi"] = '0'
                MeasRec["treat_dc_field_theta"] = '0'
                MeasRec["quality"] = 'g'  # assume all data are "good"
                MeasRec["standard"] = 'u'  # assume all data are "good"
                if run_number_key in list(InRec.keys()) and InRec[run_number_key] != "":
                    run_number = InRec[run_number_key]
                # date time is second line of file
                datestamp = InRec[date_key].split()
                if '/' in datestamp[0]:
                    # break into month day year
                    mmddyy = datestamp[0].split('/')
                    if len(mmddyy[0]) == 1:
                        mmddyy[0] = '0'+mmddyy[0]  # make 2 characters
                    if len(mmddyy[1]) == 1:
                        mmddyy[1] = '0'+mmddyy[1]  # make 2 characters
                    if len(mmddyy[2]) == 1:
                        mmddyy[2] = '0'+mmddyy[2]  # make 2 characters
                    if len(datestamp[1]) == 1:
                        datestamp[1] = '0'+datestamp[1]  # make 2 characters
                    hour, minute = datestamp[1].split(':')
                    if len(hour) == 1:
                        hour = '0' + hour
                    date = mmddyy[0]+':'+mmddyy[1]+":" + \
                        mmddyy[2] + ':' + hour + ":" + minute + ":00"
                    #date=mmddyy[2] + ':'+mmddyy[0]+":"+mmddyy[1] +':' + hour + ":" + minute + ":00"
                if '-' in datestamp[0]:
                    # break into month day year
                    mmddyy = datestamp[0].split('-')
                    date = mmddyy[0]+':'+mmddyy[1]+":" + \
                        mmddyy[2] + ':' + datestamp[1]+":0"
                if len(date.split(":")) > 6:
                    date = date[:-2]
                # try with month:day:year
                try:
                    utc_dt = datetime.datetime.strptime(
                        date, "%m:%d:%Y:%H:%M:%S")
                except ValueError:
                    # try with year:month:day
                    try:
                        utc_dt = datetime.datetime.strptime(
                            date, "%Y:%m:%d:%H:%M:%S")
                    except ValueError:
                        # if all else fails, assume the year is in the third position
                        # and try padding with '20'
                        new_date = pad_year(
                            date, ind=2, warn=year_warning, fname=os.path.split(f)[1])
                        utc_dt = datetime.datetime.strptime(
                            new_date, "%m:%d:%Y:%H:%M:%S")
                        # only give warning once per csv file
                        year_warning = False
                MeasRec['timestamp'] = utc_dt.strftime("%Y-%m-%dT%H:%M:%S")+"Z"
                MeasRec["method_codes"] = 'LT-NO'
                if 'Treatment Type' in list(InRec.keys()) and InRec['Treatment Type'] != "":
                    if "AF" in InRec['Treatment Type'].upper():
                        MeasRec['method_codes'] = 'LT-AF-Z'
                        inst = inst+':IODP-SRM-AF'  # measured on shipboard in-line 2G AF
                        treatment_value = float(
                            InRec[demag_key].strip('"'))*1e-3  # convert mT => T
                        # AF demag in treat mT => T
                        MeasRec["treat_ac_field"] = treatment_value
                    elif "T" in InRec['Treatment Type'].upper():
                        MeasRec['method_codes'] = 'LT-T-Z'
                        inst = inst+':IODP-TDS'  # measured on shipboard Schonstedt thermal demagnetizer
                        try:
                            treatment_value = float(
                                InRec['Treatment Value'])+273  # convert C => K
                        except KeyError:
                            try:
                                treatment_value = float(
                                    InRec["Treatment value<br> (mT or \N{DEGREE SIGN}C)"]) + 273
                            except KeyError:
                                print([k for k in InRec.keys() if 'treat' in k.lower()])
                                print("-W- Couldn't find column for Treatment Value")
                                treatment_value = ""
                        MeasRec["treat_temp"] = str(treatment_value)
                    elif 'Alternating Frequency' in InRec['Treatment Type']:
                        MeasRec['method_codes'] = 'LT-AF-Z'
                        inst = inst+':IODP-DTECH'  # measured on shipboard Dtech D2000
                        treatment_value = float(
                            InRec[demag_key])*1e-3  # convert mT => T
                        # AF demag in treat mT => T
                        MeasRec["treat_ac_field"] = treatment_value
                    elif 'Thermal' in InRec['Treatment Type']:
                        MeasRec['method_codes'] = 'LT-T-Z'
                        inst = inst+':IODP-TDS'  # measured on shipboard Schonstedt thermal demagnetizer
                        treatment_value = float(
                            InRec[demag_key])+273  # convert C => K
                        MeasRec["treat_temp"] = '%8.3e' % (treatment_value)
                elif InRec[demag_key] != "0":
                    MeasRec['method_codes'] = 'LT-AF-Z'
                    inst = inst+':IODP-SRM-AF'  # measured on shipboard in-line 2G AF
                    try:
                        treatment_value = float(
                            InRec[demag_key])*1e-3  # convert mT => T
                    except ValueError:
                        print("Couldn't determine treatment value was given treatment value of %s and demag key %s; setting to blank you will have to manually correct this (or fix it)" % (
                            InRec[demag_key], demag_key))
                        treatment_value = ''
                    # AF demag in treat mT => T
                    MeasRec["treat_ac_field"] = treatment_value
                MeasRec["standard"] = 'u'  # assume all data are "good"
                vol = float(volume)*1e-6  # convert from cc to m^3
                if run_number != "":
                    MeasRec['external_database_ids'] = {'LIMS': run_number}
                else:
                    MeasRec['external_database_ids'] = ""
                MeasRec['dir_inc'] = InRec[inc_key]
                MeasRec['dir_dec'] = InRec[dec_key]
                intens = InRec[int_key]
                try:
                    # convert intensity from A/m to Am^2 using vol
                    MeasRec['magn_moment'] = '%8.3e' % (float(intens)*vol)
                except ValueError:
                    print("couldn't find magnetic moment for specimen %s and int_key %s; leaving this field blank you'll have to fix this manually" % (
                        specimen, int_key))
                    MeasRec['magn_moment'] = ''
                MeasRec['instrument_codes'] = inst
                MeasRec['treat_step_num'] = '1'
                MeasRec['dir_csd'] = '0'
                MeasRec['meas_n_orient'] = ''
                MeasRecs.append(MeasRec)
    if not file_found:
        print("No .csv files were found")
        return (False, "No .csv files were found")

    con = nb.Contribution(output_dir_path, read_tables=[])

    con.add_magic_table_from_data(dtype='specimens', data=SpecRecs)
    con.add_magic_table_from_data(dtype='samples', data=SampRecs)
    con.add_magic_table_from_data(dtype='sites', data=SiteRecs)
    con.add_magic_table_from_data(dtype='locations', data=LocRecs)
    #MeasSort=sorted(MeasRecs,key=lambda x: (x['specimen'], float(x['treat_ac_field'])))
    #MeasSort=sorted(MeasRecs,key=lambda x: float(x['treat_ac_field']))
    # MeasOuts=pmag.measurements_methods3(MeasSort,noave)
    MeasOuts = pmag.measurements_methods3(MeasRecs, noave)
    con.add_magic_table_from_data(dtype='measurements', data=MeasOuts)

    con.write_table_to_file('specimens', custom_name=spec_file)
    con.write_table_to_file('samples', custom_name=samp_file)
    con.write_table_to_file('sites', custom_name=site_file)
    con.write_table_to_file('locations', custom_name=loc_file)
    con.write_table_to_file('measurements', custom_name=meas_file)

    return (True, meas_file)

# helper


def pad_year(date, ind, warn=False, fname=''):
    """
    Parameters
    ----------
    Date: str
        date as colon-delimited string, i.e. 04:10:2015:06:45:00
    ind: int
        index of year position
    warn : bool (default False)
        verbose or not
    fname: str (default '')
        filename for more informative warning

    Returns
    ---------
    new_date: str
       date as colon-delimited,
       with year padded if it wasn't before
    """
    date_list = date.split(':')
    year = date_list[ind]
    if len(year) == 2:
        padded_year = '20' + year
        date_list[ind] = padded_year
        if warn:
            print('-W- Ambiguous year "{}" in {}.'.format(year, fname))
            print('    Assuming {}.'.format(padded_year))
    new_date = ':'.join(date_list)
    if new_date != date and warn:
        print('    Date translated to {}'.format(new_date))
    return new_date


def do_help():
    return __doc__


def main():
    kwargs = {}
    if "-h" in sys.argv:
        help(__name__)
        sys.exit()
    if '-WD' in sys.argv:
        ind = sys.argv.index("-WD")
        kwargs['dir_path'] = sys.argv[ind+1]
    if '-ID' in sys.argv:
        ind = sys.argv.index('-ID')
        kwargs['input_dir_path'] = sys.argv[ind+1]
    if "-A" in sys.argv:
        kwargs['noave'] = 1
    if '-f' in sys.argv:
        ind = sys.argv.index("-f")
        kwargs['csv_file'] = sys.argv[ind+1]
    if '-F' in sys.argv:
        ind = sys.argv.index("-F")
        kwargs['meas_file'] = sys.argv[ind+1]
    if '-Fsp' in sys.argv:
        ind = sys.argv.index("-Fsp")
        kwargs['spec_file'] = sys.argv[ind+1]
    if '-Fsi' in sys.argv:
        ind = sys.argv.index("-Fsi")
        kwargs['site_file'] = sys.argv[ind+1]
    if '-Fsa' in sys.argv:
        ind = sys.argv.index("-Fsa")
        kwargs['samp_file'] = sys.argv[ind+1]
    if '-Flo' in sys.argv:  # Kevin addition
        ind = sys.argv.index("-Flo")
        kwargs['loc_file'] = sys.argv[ind+1]
    if "-lat" in sys.argv:
        ind = sys.argv.index("-lat")
        kwargs['lat'] = sys.argv[ind+1]
    if "-lon" in sys.argv:
        ind = sys.argv.index("-lon")
        kwargs['lon'] = sys.argv[ind+1]

    convert(**kwargs)


if __name__ == '__main__':
    main()
