#!/usr/bin/env python

from __future__ import print_function
import unittest
import os
import sys
import re
import matplotlib
from pmagpy import pmag
from pmagpy import ipmag
from pmagpy import new_builder as nb
#from pmagpy import find_pmag_dir
WD = pmag.get_test_WD()


class TestIGRF(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        os.chdir(WD)

    def test_igrf_output(self):
        result = ipmag.igrf([1999.1, 30, 20, 50])
        reference = [1.20288657e+00, 2.82331112e+01, 3.9782338913649881e+04]
        for num, item in enumerate(result):
            self.assertAlmostEqual(item, reference[num])

class TestUploadMagic(unittest.TestCase):

    def setUp(self):
        self.dir_path = os.path.join(WD, 'data_files', 'testing')

    def tearDown(self):
        tables = ['measurements', 'specimens', 'samples',
                  'sites', 'locations', 'ages', 'criteria',
                  'contribution']
        tables.extend([tname + "_errors" for tname in tables])
        possible_files = os.listdir(WD)
        for table in tables:
            fname = table + ".txt"
            if fname in possible_files:
                try:
                    print('trying to remove', os.path.join(WD, fname))
                    os.remove(os.path.join(WD, fname))
                except OSError:
                    pass
        # get rid of partial upload files
        # like: Tel-Hazor_Tel-Megiddo_14.Jun.2017-1.txt
        pattern = re.compile('.*\w*[.]\w*[.]\w*[20]\d{2}\w*.txt$')
        remove = []
        for f in possible_files:
            if pattern.match(f):
                remove.append(f)
        pmag.remove_files(remove, WD)
        # and any in core_depthplot
        core_depthplot_dir = os.path.join(WD, 'data_files', 'core_depthplot')
        possible_files = os.listdir(core_depthplot_dir)
        remove = []
        for f in possible_files:
            if pattern.match(f):
                remove.append(f)
        pmag.remove_files(remove, core_depthplot_dir)
        # return to WD
        os.chdir(WD)


    def test_empty_dir(self):
        directory = os.path.join(self.dir_path, 'empty_dir')
        outfile, error_message, errors = ipmag.upload_magic(dir_path=directory)
        self.assertFalse(errors)
        self.assertFalse(outfile)
        self.assertEqual(error_message, "no data found, upload file not created")
        files = os.listdir(directory)
        self.assertEqual(['blank.txt'], files)

    def test_with_invalid_files(self):
        directory = os.path.join(self.dir_path, 'my_project_with_errors')
        outfile, error_message, errors = ipmag.upload_magic(dir_path=directory)
        self.assertTrue(errors)
        self.assertFalse(outfile)
        self.assertEqual(error_message, "file validation has failed.  You may run into problems if you try to upload this file.")
        directory = os.path.join(self.dir_path, 'my_project_with_errors')

        # delete any upload file that was partially created
        import re
        pattern = re.compile('\w*[.]\w*[.]\w*[20]\d{2}\w*.txt$')
        possible_files = os.listdir(directory)
        files = []
        for f in possible_files:
            if pattern.match(f):
                files.append(f)
        pmag.remove_files(files, directory)

    def test_with_valid_files(self):
        #print os.path.join(self.dir_path, 'my_project')
        outfile, error_message, errors = ipmag.upload_magic(dir_path=os.path.join(self.dir_path, 'my_project'))
        self.assertTrue(outfile)
        self.assertEqual(error_message, '')
        self.assertFalse(errors)
        assert os.path.isfile(outfile)
        directory = os.path.join(self.dir_path, 'my_project_with_errors')
        os.remove(os.path.join(directory, outfile))

    def test3_with_invalid_files(self):
        dir_path = os.path.join(WD, 'data_files', '3_0', 'Megiddo')
        outfile, error_message, errors, all_errors = ipmag.upload_magic3(dir_path=dir_path)
        msg = "file validation has failed.  You may run into problems if you try to upload this file."
        self.assertEqual(error_message, msg)
        # delete any upload file that was partially created
        import re
        pattern = re.compile('\w*[.]\w*[.]\w*[20]\d{2}\w*.txt$')
        possible_files = os.listdir(dir_path)
        files = []
        for f in possible_files:
            if pattern.match(f):
                files.append(f)
        pmag.remove_files(files, dir_path)


    def test3_with_contribution(self):
        dir_path = os.path.join(WD, 'data_files', '3_0', 'Megiddo')
        con = nb.Contribution(directory=dir_path)
        outfile, error_message, errors, all_errors = ipmag.upload_magic3(contribution=con)
        msg = "file validation has failed.  You may run into problems if you try to upload this file."
        self.assertEqual(error_message, msg)
        # delete any upload file that was partially created
        import re
        pattern = re.compile('\A[^.]*\.[a-zA-Z]*\.\d{4}\_?\d*\.txt')
        possible_files = os.listdir(dir_path)
        files = []
        for f in possible_files:
            if pattern.match(f):
                files.append(f)
        pmag.remove_files(files, dir_path)

    @unittest.skipIf(sys.platform in ['win32', 'win62'], "data file isn't properly moved on windows")
    def test_depth_propagation(self):
        dir_path = os.path.join(WD, 'data_files', 'core_depthplot')
        #con = nb.Contribution(dir_path)
        #self.assertNotIn('core_depth', con.tables['sites'].df.index)
        #con.propagate_cols(['core_depth'], 'sites', 'samples', down=False)
        #self.assertIn('core_depth', con.tables['sites'].df.columns)
        #self.assertEqual(con.tables['sites'].df.loc['15-1-013', 'core_depth'], 55.23)
        #
        outfile, error_message, errors, all_errors = ipmag.upload_magic3(dir_path=dir_path)
        print('mv {} {}'.format(outfile, WD))
        os.system('mv {} {}'.format(outfile, WD))
        outfile = os.path.join(WD, os.path.split(outfile)[1])
        ipmag.download_magic(outfile)
        con = nb.Contribution(WD)
        self.assertIn('core_depth', con.tables['sites'].df.columns)
        self.assertEqual(con.tables['sites'].df.loc['15-1-013', 'core_depth'], 55.23)

class TestCombineMagic(unittest.TestCase):

    def setUp(self):
        self.input_dir = os.path.join(WD, 'data_files', '3_0', 'McMurdo')

    def tearDown(self):
        outfiles = ['custom_outfile.txt']
        pmag.remove_files(outfiles, self.input_dir)
        pmag.remove_files(['custom.out'], WD)


    def test_with_custom_name(self):
        outfile = os.path.join(self.input_dir, 'custom_outfile.txt')
        if os.path.exists(outfile):
            os.remove(outfile)
        flist = ['locations.txt', 'new_locations.txt']
        flist = [os.path.join(self.input_dir, fname) for fname in flist]
        #res = ipmag.combine_magic(flist, 'custom_outfile.txt', 3, 'locations')
        res = ipmag.combine_magic(flist, outfile, 3, 'locations')
        self.assertTrue(res)
        self.assertEqual(res, outfile)
        self.assertTrue(os.path.exists(outfile))

    def test_with_remove_rows(self):
        flist = ['extra_specimens.txt', 'specimens.txt']
        flist = [os.path.join(self.input_dir, fname) for fname in flist]
        #flist = [os.path.join(self.input_dir, fname) for fname in flist]
        res = ipmag.combine_magic(flist, 'custom.out', data_model=3)
        with open(os.path.join(WD, 'custom.out')) as f:
            n = len(f.readlines()) - 2
        self.assertEqual(n, 2747)




class Test_iodp_samples_magic(unittest.TestCase):

    def setUp(self):
        self.input_dir = os.path.join(WD, 'data_files', 'Measurement_Import',
                                      'IODP_srm_magic')

    def tearDown(self):
        os.chdir(WD)
        filelist = ['er_samples.txt']
        pmag.remove_files(filelist, WD)

    def test_with_wrong_format(self):
        infile = os.path.join(self.input_dir, 'GCR_U1359_B_coresummary.csv')
        program_ran, error_message = ipmag.iodp_samples_magic(infile)
        self.assertFalse(program_ran)
        expected_error = 'Could not extract the necessary data from your input file.\nPlease make sure you are providing a correctly formated IODP samples csv file.'
        self.assertEqual(error_message, expected_error)


    def test_with_right_format(self):
        reference_file = os.path.join(WD, 'testing', 'odp_magic',
                                      'odp_magic_er_samples.txt')
        infile = os.path.join(self.input_dir, 'samples_318_U1359_B.csv')
        program_ran, outfile = ipmag.iodp_samples_magic(infile, data_model_num=2)
        self.assertTrue(program_ran)
        expected_file = os.path.join('.', 'er_samples.txt')
        self.assertEqual(outfile, expected_file)
        self.assertTrue(os.path.isfile(outfile))


    def test_content_with_right_format(self):
        reference_file = os.path.join(WD, 'data_files', 'testing',
                                      'odp_magic', 'odp_magic_er_samples.txt')
        infile = os.path.join(self.input_dir, 'samples_318_U1359_B.csv')
        program_ran, outfile = ipmag.iodp_samples_magic(infile, data_model_num=2)
        with open(reference_file) as ref_file:
            ref_lines = ref_file.readlines()
        with open(outfile) as out_file:
            out_lines = out_file.readlines()
        self.assertTrue(program_ran)
        self.assertEqual(ref_lines, out_lines)

    def test_with_data_model3(self):
        infile = os.path.join(self.input_dir, 'samples_318_U1359_B.csv')
        program_ran, outfile = ipmag.iodp_samples_magic(infile, data_model_num=3)
        self.assertTrue(program_ran)
        self.assertEqual(os.path.realpath('samples.txt'), os.path.realpath(outfile))



class TestKly4s_magic(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        filelist= ['magic_measurements.txt', 'my_magic_measurements.txt', 'er_specimens.txt', 'er_samples.txt', 'er_sites.txt', 'rmag_anisotropy.txt', 'my_rmag_anisotropy.txt']
        pmag.remove_files(filelist, WD)
        os.chdir(WD)

    def test_kly4s_without_infile(self):
        with self.assertRaises(TypeError):
            ipmag.kly4s_magic()

    def test_kly4s_with_invalid_infile(self):
        program_ran, error_message = ipmag.kly4s_magic('hello.txt')
        expected_file = os.path.join('.', 'hello.txt')
        self.assertFalse(program_ran)
        self.assertEqual(error_message, 'Error opening file: {}'.format(expected_file))

    def test_kly4s_with_valid_infile(self):
        in_dir = os.path.join(WD, 'data_files', 'Measurement_Import', 'kly4s_magic')
        program_ran, outfile = ipmag.kly4s_magic('KLY4S_magic_example.dat', output_dir_path=WD,
                                                 input_dir_path=in_dir, data_model_num=2)
        self.assertTrue(program_ran)
        self.assertEqual(outfile, os.path.join(WD, 'magic_measurements.txt'))

    def test_kly4s_fail_option4(self):
        in_dir = os.path.join(WD, 'data_files', 'Measurement_Import', 'kly4s_magic')
        program_ran, error_message = ipmag.kly4s_magic('KLY4S_magic_example.dat', samp_con="4",
                                                       output_dir_path=WD, input_dir_path=in_dir,
                                                       data_model_num=2)
        self.assertFalse(program_ran)
        self.assertEqual(error_message, "option [4] must be in form 4-Z where Z is an integer")

    def test_kly4s_succeed_option4(self):
        in_dir = os.path.join(WD, 'data_files', 'Measurement_Import', 'kly4s_magic')
        program_ran, outfile = ipmag.kly4s_magic('KLY4S_magic_example.dat', samp_con="4-2",
                                                 output_dir_path=WD, input_dir_path=in_dir,
                                                 data_model_num=2)
        self.assertTrue(program_ran)
        self.assertEqual(outfile, os.path.join(WD, 'magic_measurements.txt'))
        self.assertTrue(os.path.isfile(os.path.join(WD, 'magic_measurements.txt')))

    def test_kly4s_with_options(self):
        in_dir = os.path.join(WD, 'data_files', 'Measurement_Import', 'kly4s_magic')
        program_ran, outfile = ipmag.kly4s_magic('KLY4S_magic_example.dat', specnum=1,
                                                 locname="location", inst="instrument",
                                                 samp_con=3, or_con=2,
                                                 measfile='my_magic_measurements.txt',
                                                 aniso_outfile="my_rmag_anisotropy.txt",
                                                 output_dir_path=WD, input_dir_path=in_dir,
                                                 data_model_num=2)
        self.assertTrue(program_ran)
        self.assertEqual(outfile, os.path.join(WD, 'my_magic_measurements.txt'))
        self.assertTrue(os.path.isfile(os.path.join(WD, 'my_rmag_anisotropy.txt')))


    def test_kly4s_with_valid_infile_data_model3(self):
        in_dir = os.path.join(WD, 'data_files', 'Measurement_Import', 'kly4s_magic')
        program_ran, outfile = ipmag.kly4s_magic('KLY4S_magic_example.dat', output_dir_path=WD,
                                                 input_dir_path=in_dir, data_model_num=3)

        con = nb.Contribution(WD)
        self.assertEqual(['measurements', 'samples', 'sites', 'specimens'], sorted(con.tables))



class TestK15_magic(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        filelist = ['magic_measurements.txt', 'my_magic_measurements.txt',
                    'er_specimens.txt', 'er_samples.txt', 'my_er_samples.txt',
                    'er_sites.txt', 'rmag_anisotropy.txt',
                    'my_rmag_anisotropy.txt', 'rmag_results.txt',
                    'my_rmag_results.txt']
        pmag.remove_files(filelist, WD)
        os.chdir(WD)

    #def test_k15_with_no_files(self):
    #    with self.assertRaises(TypeError):
    #        ipmag.k15_magic()

    def test_k15_with_files(self):
        input_dir = os.path.join(WD, 'data_files',
                                 'Measurement_Import', 'k15_magic')
        program_ran, outfile  = ipmag.k15_magic('k15_example.dat',
                                                input_dir_path=input_dir,
                                                data_model_num=2)
        self.assertTrue(program_ran)
        self.assertEqual(outfile, os.path.join('.', 'magic_measurements.txt'))

    def test_k15_fail_option4(self):
        input_dir = os.path.join(WD, 'data_files', 'Measurement_Import',
                                 'k15_magic')
        program_ran, error_message = ipmag.k15_magic('k15_example.dat',
                                                     sample_naming_con="4",
                                                     input_dir_path=input_dir,
                                                     data_model_num=2)
        self.assertFalse(program_ran)
        self.assertEqual(error_message, "option [4] must be in form 4-Z where Z is an integer")

    def test_k15_succeed_option4(self):
        input_dir = os.path.join(WD, 'data_files', 'Measurement_Import', 'k15_magic')
        program_ran, outfile = ipmag.k15_magic('k15_example.dat', sample_naming_con="4-2",
                                               input_dir_path=input_dir,
                                               data_model_num=2)
        self.assertTrue(program_ran)
        self.assertEqual(outfile, os.path.join(".", "magic_measurements.txt"))

    def test_k15_with_options(self):
        input_dir = os.path.join(WD, 'data_files', 'Measurement_Import',
                                 'k15_magic')
        program_ran, outfile = ipmag.k15_magic('k15_example.dat', specnum=2,
                                               sample_naming_con="3",
                                               er_location_name="Here",
                                               measfile="my_magic_measurements.txt",
                                               sampfile="my_er_samples.txt",
                                               aniso_outfile="my_rmag_anisotropy.txt",
                                               result_file="my_rmag_results.txt",
                                               input_dir_path=input_dir,
                                                   data_model_num=2)
        self.assertTrue(program_ran)
        self.assertEqual(outfile, os.path.join(".", "my_magic_measurements.txt"))

    def test_data_model3(self):
        input_dir = os.path.join(WD, 'data_files', 'Measurement_Import',
                                 'k15_magic')
        program_ran, outfile = ipmag.k15_magic('k15_example.dat', specnum=2,
                                               input_dir_path=input_dir)
        print(program_ran, outfile)
        self.assertTrue(program_ran)
        print('outfile', outfile)
        self.assertEqual(os.path.realpath('./measurements.txt'), os.path.realpath(outfile))


class TestSUFAR_asc_magic(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        filelist = ['magic_measurements.txt', 'my_magic_measurements.txt',
                    'er_specimens.txt', 'er_samples.txt', 'my_er_samples.txt',
                    'er_sites.txt', 'rmag_anisotropy.txt', 'my_rmag_anisotropy.txt',
                    'rmag_results.txt', 'my_rmag_results.txt', 'measurements.txt',
                    'specimens.txt', 'samples.txt', 'sites.txt', 'locations.txt']
        pmag.remove_files(filelist, WD)
        os.chdir(WD)


    def test_SUFAR4_with_no_files(self):
        with self.assertRaises(TypeError):
            ipmag.SUFAR4_magic()

    def test_SUFAR4_with_invalid_file(self):
        input_dir = os.path.join(WD, 'data_files',
                                 'Measurement_Import', 'SUFAR_asc_magic')
        infile = 'fake_sufar4-asc_magic_example.txt'
        program_ran, error_message = ipmag.SUFAR4_magic(infile,
                                                        input_dir_path=input_dir,
                                                        data_model_num=2)
        self.assertFalse(program_ran)
        self.assertEqual(error_message,
                         'Error opening file: {}'.format(os.path.join(input_dir,
                                                                      infile)))


    def test_SUFAR4_with_infile(self):
        input_dir = os.path.join(WD, 'data_files', 'Measurement_Import',
                                 'SUFAR_asc_magic')
        infile = 'sufar4-asc_magic_example.txt'
        program_ran, outfile = ipmag.SUFAR4_magic(infile,
                                                  input_dir_path=input_dir,
                                                  data_model_num=2)
        self.assertTrue(program_ran)
        self.assertEqual(outfile, os.path.join('.', 'magic_measurements.txt'))
        with open(outfile, 'r') as ofile:
            lines = ofile.readlines()
            self.assertEqual(292, len(lines))


    def test_SUFAR4_succeed_data_model3(self):
        input_dir = os.path.join(WD, 'data_files', 'Measurement_Import',
                                 'SUFAR_asc_magic')
        infile = 'sufar4-asc_magic_example.txt'
        program_ran, outfile = ipmag.SUFAR4_magic(infile,
                                                  input_dir_path=input_dir)
        self.assertTrue(program_ran)
        self.assertEqual(outfile, os.path.join('.', 'measurements.txt'))
        with open(outfile, 'r') as ofile:
            lines = ofile.readlines()
            self.assertEqual(292, len(lines))
            self.assertEqual('measurements', lines[0].split('\t')[1].strip())
        con = nb.Contribution(WD)
        self.assertEqual(sorted(con.tables),
                         sorted(['measurements', 'specimens',
                                 'samples', 'sites']))



    def test_SUFAR4_fail_option4(self):
        input_dir = os.path.join(WD, 'data_files',
                                 'Measurement_Import', 'SUFAR_asc_magic')
        infile = 'sufar4-asc_magic_example.txt'
        program_ran, error_message = ipmag.SUFAR4_magic(infile,
                                                        input_dir_path=input_dir,
                                                        sample_naming_con='4',
                                                        data_model_num=2)
        self.assertFalse(program_ran)
        self.assertEqual(error_message, "option [4] must be in form 4-Z where Z is an integer")

    def test_SUFAR4_succeed_option4(self):
        input_dir = os.path.join(WD, 'data_files', 'Measurement_Import',
                                 'SUFAR_asc_magic')
        print('WD', WD)
        print('input_dir', input_dir)
        infile = 'sufar4-asc_magic_example.txt'
        ofile = 'my_magic_measurements.txt'
        program_ran, outfile = ipmag.SUFAR4_magic(infile,
                                                  meas_output=ofile,
                                                  input_dir_path=input_dir,
                                                  sample_naming_con='4-2',
                                                  data_model_num=2)
        self.assertTrue(program_ran)
        self.assertEqual(outfile, os.path.join('.', ofile))

    def test_SUFAR4_with_options(self):
        input_dir = os.path.join(WD, 'data_files',
                                 'Measurement_Import', 'SUFAR_asc_magic')
        infile = 'sufar4-asc_magic_example.txt'
        program_ran, outfile = ipmag.SUFAR4_magic(infile, meas_output='my_magic_measurements.txt',
                                                  aniso_output="my_rmag_anisotropy.txt",
                                                  specnum=2, locname="Here", instrument="INST",
                                                  static_15_position_mode=True, input_dir_path=input_dir,
                                                  sample_naming_con='5',
                                                  data_model_num=2)
        self.assertTrue(program_ran)
        self.assertEqual(outfile, os.path.join('.', 'my_magic_measurements.txt'))

class TestAgmMagic(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        filelist = ['magic_measurements.txt', 'my_magic_measurements.txt', 'er_specimens.txt', 'er_samples.txt', 'my_er_samples.txt', 'er_sites.txt', 'rmag_anisotropy.txt', 'my_rmag_anisotropy.txt', 'rmag_results.txt', 'my_rmag_results.txt', 'agm_magic_example.magic']
        pmag.remove_files(filelist, WD)
        pmag.remove_files(filelist, os.path.join(WD, 'data_files', 'Measurement_import', 'agm_magic'))
        dir_path = os.path.join(WD, 'data_files', 'Measurement_Import', 'agm_magic')
        for f in os.listdir(dir_path):
            if 'IS0' in f:
                os.remove(os.path.join(dir_path, f))
        os.chdir(WD)

    def test_agm_with_no_files(self):
        with self.assertRaises(TypeError):
            ipmag.agm_magic()

    def test_agm_with_bad_file(self):
        program_ran, error_message = ipmag.agm_magic('bad_file.txt')
        self.assertFalse(program_ran)
        self.assertEqual(error_message, 'You must provide a valid agm file')

    def test_agm_success(self):
        input_dir = os.path.join(WD, 'data_files',
                                 'Measurement_Import', 'agm_magic')
        program_ran, filename = ipmag.agm_magic('agm_magic_example.agm',
                                                outfile='agm_magic_example.magic',
                                                input_dir_path=input_dir)
        self.assertTrue(program_ran)
        self.assertEqual(filename, os.path.join('.', 'agm_magic_example.magic'))


#@unittest.skipIf(sys.platform in ['darwin'], 'currently causing fatal errors on OSX')
class TestCoreDepthplot(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        filelist = ['magic_measurements.txt', 'my_magic_measurements.txt', 'er_specimens.txt', 'er_samples.txt', 'my_er_samples.txt', 'er_sites.txt', 'rmag_anisotropy.txt', 'my_rmag_anisotropy.txt', 'rmag_results.txt', 'my_rmag_results.txt']
        pmag.remove_files(filelist, WD)
        os.chdir(WD)

    def test_core_depthplot_with_no_files(self):
        program_ran, error_message = ipmag.core_depthplot()
        self.assertFalse(program_ran)
        self.assertEqual("You must provide either a magic_measurements file or a pmag_specimens file", error_message)

    def test_core_depthplot_bad_params(self):
        path = os.path.join(WD, 'data_files', 'core_depthplot')
        program_ran, error_message = ipmag.core_depthplot(input_dir_path=path,
                                                          samp_file='samples.txt')
        self.assertFalse(program_ran)
        self.assertEqual('No data found to plot\nTry again with different parameters', error_message)

    def test_core_depthplot_bad_method(self):
        path = os.path.join(WD, 'data_files', 'core_depthplot')
        program_ran, error_message = ipmag.core_depthplot(input_dir_path=path, step=5, meth='NA', age_file='ages.txt')
        self.assertFalse(program_ran)
        self.assertEqual(error_message, 'method: "{}" not supported'.format('NA'))


    def test_core_depthplot_success(self):
        path = os.path.join(WD, 'data_files', 'core_depthplot')
        program_ran, plot_name = ipmag.core_depthplot(input_dir_path=path, spc_file='pmag_specimens.txt', samp_file='er_samples.txt', meth='AF', step=15, data_model_num=2)
        #program_ran, plot_name = True, 'DSDP Site 522_m:_LT-AF-Z_core-depthplot.svg'
        self.assertTrue(program_ran)
        self.assertEqual(plot_name, 'DSDP Site 522_m:_LT-AF-Z_core-depthplot.svg')

    def test_core_depthplot_with_sum_file(self):
        path = os.path.join(WD, 'data_files', 'UTESTA', 'UTESTA_MagIC')
        sum_file = 'CoreSummary_XXX_UTESTA.csv'
        program_ran, plot_name = ipmag.core_depthplot(input_dir_path=path, spc_file='pmag_specimens.txt', samp_file='er_samples.txt', meth='AF', step=15, sum_file=sum_file, data_model_num=2)
        self.assertTrue(program_ran)
        outfile = 'UTESTA_m:_LT-AF-Z_core-depthplot.svg'
        self.assertEqual(plot_name, outfile)


    def test_core_depthplot_without_full_time_options(self):
        path = os.path.join(WD, 'data_files', 'core_depthplot')
        program_ran, error_message = ipmag.core_depthplot(input_dir_path=path, spc_file='pmag_specimens.txt', samp_file='er_samples.txt', meth='AF', step=15, fmt='png', pltInc=False, logit=True, pltTime=True)#, timescale='gts12', amin=0, amax=3) # pltDec = False causes failure with these data
        self.assertFalse(program_ran)
        self.assertEqual(error_message, "To plot time, you must provide amin, amax, and timescale")

    def test_core_depthplot_success_with_options(self):
        path = os.path.join(WD, 'data_files', 'core_depthplot')
        program_ran, plot_name = ipmag.core_depthplot(input_dir_path=path, spc_file='pmag_specimens.txt', samp_file='er_samples.txt', meth='AF', step=15, fmt='png', pltInc=False, logit=True, pltTime=True, timescale='gts12', amin=0, amax=3, data_model_num=2) # pltDec = False causes failure with these data
        self.assertTrue(program_ran)
        self.assertEqual(plot_name, 'DSDP Site 522_m:_LT-AF-Z_core-depthplot.png')

    def test_core_depthplot_success_with_other_options(self):
        path = os.path.join(WD, 'data_files', 'core_depthplot')
        program_ran, plot_name = ipmag.core_depthplot(input_dir_path=path,
                                                      spc_file='pmag_specimens.txt',
                                                      age_file='er_ages.txt',
                                                      meth='AF', step=15,
                                                      fmt='png', pltInc=False,
                                                      logit=True, pltTime=True,
                                                      timescale='gts12',
                                                      amin=0, amax=3, data_model_num=2) # pltDec = False causes failure with these data
        self.assertTrue(program_ran)
        self.assertEqual(plot_name, 'DSDP Site 522_m:_LT-AF-Z_core-depthplot.png')

    def test_core_depthplot_data_model3(self):
        path = os.path.join(WD, 'data_files', 'core_depthplot')
        program_ran, plot_name = ipmag.core_depthplot(input_dir_path=path,
                                                      spc_file='specimens.txt',
                                                      age_file='ages.txt',
                                                      meth='AF', step=15,
                                                      fmt='png', pltInc=False,
                                                      logit=True, pltTime=True,
                                                      timescale='gts12',
                                                      amin=0, amax=3, data_model_num=3)
        self.assertTrue(program_ran)
        self.assertEqual(plot_name, 'DSDP Site 522_m:_LT-AF-Z_core-depthplot.png')


    def test_core_depthplot_data_model3_options(self):
        path = os.path.join(WD, 'data_files', 'core_depthplot')
        program_ran, plot_name = ipmag.core_depthplot(input_dir_path=path, samp_file='samples.txt',
                                                      meth='AF', step=15)
        self.assertTrue(program_ran)
        self.assertEqual(plot_name, 'DSDP Site 522_m:_LT-AF-Z_core-depthplot.svg')

#@unittest.skipIf(sys.platform in ['darwin'], 'currently causing fatal errors on OSX')
class TestAniDepthplot(unittest.TestCase):

    def setUp(self):
        self.aniso_WD = os.path.join(WD, 'data_files', 'ani_depthplot')

    def tearDown(self):
        filelist = ['magic_measurements.txt', 'my_magic_measurements.txt', 'er_specimens.txt', 'er_samples.txt', 'my_er_samples.txt', 'er_sites.txt', 'rmag_anisotropy.txt', 'my_rmag_anisotropy.txt', 'rmag_results.txt', 'my_rmag_results.txt', 'my_samples.txt']
        pmag.remove_files(filelist, WD)
        os.chdir(WD)

    def test_aniso_depthplot_with_no_files(self):
        program_ran, error_message = ipmag.ani_depthplot2()
        expected_file = pmag.resolve_file_name('rmag_anisotropy.txt')
        self.assertFalse(program_ran)
        self.assertEqual(error_message, "Could not find rmag_anisotropy type file: {}.\nPlease provide a valid file path and try again".format(expected_file))

    def test_aniso_depthplot_with_files(self):
        #dir_path = os.path.join(WD, 'data_files', 'UTESTA')
        main_plot, plot_name = ipmag.ani_depthplot2(dir_path=self.aniso_WD, sum_file='CoreSummary_XXX_UTESTA.csv')
        assert(isinstance(main_plot, matplotlib.figure.Figure))
        self.assertEqual(plot_name, 'U1361A_ani_depthplot.svg')


    def test_aniso_depthplot_with_sum_file(self):
        dir_path = os.path.join(WD, 'data_files', 'UTESTA', 'UTESTA_MagIC')
        sum_file = 'CoreSummary_XXX_UTESTA.csv'
        main_plot, plot_name = ipmag.ani_depthplot2(dir_path=dir_path, sum_file=sum_file)
        assert(isinstance(main_plot, matplotlib.figure.Figure))
        self.assertEqual(plot_name, 'UTESTA_ani_depthplot.svg')

    def test_aniso_depthplot_with_age_option(self):
        main_plot, plot_name = ipmag.ani_depthplot2(age_file='er_ages.txt', dir_path=self.aniso_WD)
        assert(isinstance(main_plot, matplotlib.figure.Figure))
        self.assertEqual(plot_name, 'U1361A_ani_depthplot.svg')

    def test_aniso_depthplot_with_options(self):
        main_plot, plot_name = ipmag.ani_depthplot2(dmin=20, dmax=40, depth_scale='sample_core_depth', fmt='png', dir_path=self.aniso_WD)
        assert(isinstance(main_plot, matplotlib.figure.Figure))
        self.assertEqual(plot_name, 'U1361A_ani_depthplot.png')


class TestAnisoDepthplot3(unittest.TestCase):

    def setUp(self):
        self.aniso_WD = os.path.join(WD, 'data_files', 'ani_depthplot')

    def tearDown(self):
        filelist = ['measurements.txt', 'specimens.txt', 'samples.txt', 'sites.txt']
        pmag.remove_files(filelist, WD)
        os.chdir(WD)

    def test_aniso_depthplot_with_no_files(self):
        program_ran, error_message = ipmag.ani_depthplot()
        self.assertFalse(program_ran)
        self.assertEqual(error_message, "missing required file type: specimen")

    def test_aniso_depthplot_with_files(self):
        #dir_path = os.path.join(WD, 'data_files', 'UTESTA')
        main_plot, plot_name = ipmag.ani_depthplot(dir_path=self.aniso_WD,
                                                      meas_file="fake.txt",
                                                      sum_file='CoreSummary_XXX_UTESTA.csv')
        assert(isinstance(main_plot, matplotlib.figure.Figure))
        self.assertEqual(plot_name, 'U1361A_ani_depthplot.svg')

    def test_aniso_depthplot_with_meas_file(self):
        main_plot, plot_name = ipmag.ani_depthplot(dir_path=self.aniso_WD,
                                                      sum_file='CoreSummary_XXX_UTESTA.csv')
        assert(isinstance(main_plot, matplotlib.figure.Figure))
        self.assertEqual(plot_name, 'U1361A_ani_depthplot.svg')

    def test_aniso_depthplot_with_sum_file(self):
        dir_path = os.path.join(WD, 'data_files', 'UTESTA', 'UTESTA_MagIC3')
        sum_file = 'CoreSummary_XXX_UTESTA.csv'
        main_plot, plot_name = ipmag.ani_depthplot(dir_path=dir_path,
                                                      sum_file=sum_file,
                                                      depth_scale='core_depth')
        assert(isinstance(main_plot, matplotlib.figure.Figure))
        self.assertEqual(plot_name, 'UTESTA_ani_depthplot.svg')

    def test_aniso_depthplot_with_age_option(self):
        main_plot, plot_name = ipmag.ani_depthplot(age_file='ages.txt', dir_path=self.aniso_WD)
        assert(isinstance(main_plot, matplotlib.figure.Figure))
        self.assertEqual(plot_name, 'U1361A_ani_depthplot.svg')

    def test_aniso_depthplot_with_options(self):
        main_plot, plot_name = ipmag.ani_depthplot(dmin=20, dmax=40,
                                                      depth_scale='core_depth',
                                                      fmt='png', dir_path=self.aniso_WD)
        assert(isinstance(main_plot, matplotlib.figure.Figure))
        self.assertEqual(plot_name, 'U1361A_ani_depthplot.png')


class TestPmagResultsExtract(unittest.TestCase):

    def setUp(self):
        self.result_WD = os.path.join(WD, 'data_files', 'download_magic')
        os.chdir(self.result_WD)

    def tearDown(self):
        filelist = ['magic_measurements.txt', 'my_magic_measurements.txt',
                    'er_specimens.txt', 'er_samples.txt', 'my_er_samples.txt',
                    'er_sites.txt', 'rmag_anisotropy.txt',
                    'my_rmag_anisotropy.txt', 'rmag_results.txt',
                    'my_rmag_results.txt', 'my_samples.txt', 'Directions.txt',
                    'Directions.tex', 'Intensities.txt', 'Intensities.tex',
                    'SiteNfo.txt', 'SiteNfo.tex', 'Specimens.txt',
                    'Specimens.tex', 'Criteria.txt', 'Criteria.tex']
        pmag.remove_files(filelist, self.result_WD)
        os.chdir(WD)

    def test_extract(self):
        direction_file = os.path.join(self.result_WD, 'Directions.txt')
        intensity_file = os.path.join(self.result_WD, 'Intensities.txt')
        site_file = os.path.join(self.result_WD, 'SiteNfo.txt')
        specimen_file = os.path.join(self.result_WD, 'Specimens.txt')
        crit_file = os.path.join(self.result_WD, 'Criteria.txt')
        files = [direction_file, intensity_file, site_file, specimen_file,
                 crit_file]
        for f in files:
            self.assertFalse(os.path.exists(f))
        res, outfiles = ipmag.pmag_results_extract()
        self.assertTrue(res)
        files = [os.path.join(self.result_WD, f) for f in outfiles]
        for f in files:
            self.assertTrue(os.path.exists(f))

    def test_extract_latex(self):
        direction_file = os.path.join(self.result_WD, 'Directions.tex')
        intensity_file = os.path.join(self.result_WD, 'Intensities.tex')
        site_file = os.path.join(self.result_WD, 'SiteNfo.tex')
        specimen_file = os.path.join(self.result_WD, 'Specimens.tex')
        crit_file = os.path.join(self.result_WD, 'Criteria.tex')
        files = [direction_file, intensity_file, site_file, specimen_file,
                 crit_file]
        for f in files:
            self.assertFalse(os.path.exists(f))
        res, outfiles = ipmag.pmag_results_extract(latex=True)
        self.assertTrue(res)
        files = [os.path.join(self.result_WD, f) for f in outfiles]
        for f in files:

            self.assertTrue(os.path.exists(f))





if __name__ == '__main__':
    unittest.main()
