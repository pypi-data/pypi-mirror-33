"""
Quantizer class and functions.
"""
import os
import csv
import tempfile
import subprocess as sp
from shutil import copyfile
import numpy as np
import pandas as pd
from datasmash.config import BIN_PATH
from datasmash.utils import genesess_libfile, wait_for_file


def vectorize_label(X, y):
    """

    """
    label_vec = []
    for lib_file, label in zip(X, y):
        lib_io = open(lib_file)
        num_lines = sum(1 for line in lib_io)
        label_vec.append([label] * num_lines)
        lib_io.close()
    label_vec = np.hstack(label_vec)
    return label_vec


def mkqdir(X, *, parent_dir, labels=None):
    """

    """
    tmp_dir = tempfile.mkdtemp(dir=parent_dir)
    if labels is None:
        copyfile(X, os.path.join(tmp_dir, os.path.basename(X)))
    else:
        library_list = []
        for lib_file, label in zip(X, labels):
            num_lines = sum(1 for line in open(lib_file))
            lib_file_name = os.path.basename(lib_file)
            library_list_line = [lib_file_name, label, num_lines]
            library_list.append(library_list_line)

            copyfile(lib_file, os.path.join(tmp_dir, lib_file_name))

        with open(os.path.join(tmp_dir, 'library_list'), 'w+') as csvfile:
            ll_writer = csv.writer(csvfile, delimiter=' ')
            for line in library_list:
                ll_writer.writerow(line)

    return tmp_dir


class Quantizer(object):
    """

    """
    def __init__(self, *,
                 problem_type,
                 num_streams=-1,
                 sample_size=1,
                 bin_path=BIN_PATH,
                 pooled=True,
                 epsilon=-1,
                 min_alphabet_size=2,
                 max_alphabet_size=3,
                 use_genesess=False,
                 gen_epsilon=0.02,
                 num_steps=20000,
                 num_models=1,
                 partition=None,
                 detrending=None,
                 normalization=None,
                 runfile=False,
                 multi_partition=False,
                 featurization=None,
                 featurization_params=None,
                 verbose=False):
        self._problem_type = problem_type
        self._num_streams = num_streams
        self._sample_size = sample_size
        self._bin_path = bin_path
        self._pooled = pooled
        self._epsilon = epsilon
        self._min_alphabet_size = min_alphabet_size
        self._max_alphabet_size = max_alphabet_size
        self._use_genesess = use_genesess
        self._gen_epsilon = gen_epsilon
        self._num_steps = num_steps
        self._num_models = num_models
        self._partition = partition
        self._detrending = detrending
        self._normalization = normalization
        self._runfile = runfile
        self._featurization = featurization
        self._featurization_params = featurization_params
        self._multi_partition = multi_partition
        self._verbose = verbose
        self._command_list = []
        self._fitted = False
        self._feature_order = []

        self.quantized_data_dir = ''
        self.parameters = {}
        self.data = []
        self._partition_success_set = set()
        self.training_X = None
        self.parameter_index_map = {}
        #self.data = {}

    def fit(self, data_dir):
        """
        use_genesess=True only for GSmashClassification()
        """
        self.quantized_data_dir = tempfile.mkdtemp(prefix='quantized_data_',
                                                   dir=data_dir)

        self._get_command_list(data_dir)
        raw_output = sp.check_output(self._command_list, encoding='utf-8')

        if self._problem_type == 'supervised':
            self._note_lib_files(data_dir)
        #else:
        #    self.data['dataset'] = {}
        #    self.data['dataset']['files'] = {}

        if not self._multi_partition:
            parameters = raw_output.strip().split('\n')[-1]
            pr, d, n, pa = self._read_quantizer_params(parameters)
            prune_range_list = [pr]
            detrending_list = [d]
            normalization_list = [n]
            partition_list = [pa]
        else:
            prune_range_list = []
            detrending_list = []
            normalization_list = []
            partition_list = []

            # TODO: testing Quantizer_v1
            #valid_params_path = os.path.join(data_dir, 'valid_parameters')
            valid_params_path = os.path.join(data_dir, 'valid_parameter')
            parameters = open(valid_params_path).read().splitlines()
            for param in parameters:
                #parameter_zip.append(self._read_quantizer_params(param))
                pr, d, n, pa = self._read_quantizer_params(param)
                prune_range_list.append(pr)
                detrending_list.append(d)
                normalization_list.append(n)
                partition_list.append(pa)

        parameter_zip = zip(prune_range_list, detrending_list, normalization_list,
                            partition_list)
        parameters = {}
        for pr, d, n, pa in parameter_zip:
            key = self._write_quantizer_params(pr, d, n, pa)
            param_set = {'prune_range': pr,
                         'detrending': d,
                         'normalization': n,
                         'partition': pa}
            parameters[key] = param_set

            # don't include duplicate quantizations
            if key not in self._feature_order:
                self._feature_order.append(key)
        self.parameters = parameters

        self._fitted = True

    def transform(self, data_file):
        """

        """
        assert self._fitted, ("'fit()' or 'fit_transform()' must be called"
                              + " prior to running 'transform()'")


        data_name = os.path.basename(data_file)
        data_prefix = os.path.basename(data_name) + '_'
        qdata_dir = tempfile.mkdtemp(prefix=data_prefix,
                                     dir=self.quantized_data_dir)
        data = {}
        data[data_name] = {}
        data[data_name]['files'] = {}
        data[data_name]['directory'] = qdata_dir

        # TODO: TESTING 
        partition_total = len(self.parameters)
        partition_fail_num = 0
        # TODO: END TESTING

        for name in self._feature_order:
        #for name, p_dict in self.parameters.items():
            p_dict = self.parameters[name]
            data_with_params = data_prefix + name
            data_with_params_path = os.path.join(qdata_dir, data_with_params)
            success = self._try_apply_quantizer(data_file,
                                                outfile=data_with_params_path,
                                                **p_dict)

            if self._featurization is not None:
                if not success:
                    # TODO: TESTING
                    partition_fail_num += 1
                    print('Unsuccessful: {}'.format(p_dict))
                    # TODO: TESTING

                    #self._feature_order.remove(name)
                    self._partition_success_set.remove(name)
                    continue
                else:
                    self._partition_success_set.add(name)
                    feature_file = self._featurization(data_with_params_path,
                                                       **self._featurization_params)
                    #with open(feature_file) as ff:
                    #    first_line = ff.readline()
                    #first_line_list = first_line.split(' ')
                    #if first_line_list[-1] == '\n':
                    #    first_line_list.remove('\n')
                    #num_col = self._get_num_cols

                    #feature_file = self._line_by_line(outfile,
                    #                                  function=self._featurization,
                    #                                  **self._featurization_params)
                    data_with_params_path = os.path.basename(feature_file)
            elif self._use_genesess:
                alphabet_size = len(p_dict['partition']) + 1
                genesess_libfile(data_with_params_path, alphabet_size,
                                 gen_epsilon=self._gen_epsilon,
                                 num_steps=self._num_steps,
                                 num_models=self._num_models,
                                 runfile=self._runfile)

            data[data_name]['files'][name] = data_with_params_path

            #if not success:
            #    # TODO: TESTING
            #    partition_fail_num += 1
            #    print('Unsuccessful: {}'.format(p_dict))
            #    # TODO: TESTING

            #    self.feature_order.remove(name)
            #    continue
            #else:
            #    if self._featurization is not None:
            #        feature_file = self._featurization(data_with_params_path,
            #                                           **self._featurization_params)
            #        #feature_file = self._line_by_line(outfile,
            #        #                                  function=self._featurization,
            #        #                                  **self._featurization_params)
            #        data_with_params = os.path.basename(feature_file)

            #    if self._use_genesess:
            #        alphabet_size = len(p_dict['partition']) + 1
            #        genesess_libfile(data_with_params_path, alphabet_size,
            #                         gen_epsilon=self._gen_epsilon,
            #                         num_steps=self._num_steps,
            #                         num_models=self._num_models,
            #                         runfile=self._runfile)

            #    data[data_name]['files'][name] = data_with_params

        # TODO: TESTING
        print('{}/{} failed partitions.'.format(partition_fail_num,
                                                partition_total))
        # TODO: TESTING

        X = self.combine_data(data)
        #if self.training_X is None:
        #    self.training_X = X
        #    print(X.shape)
        #else:
        #if self.training_X is not None:
        #valid_indices = [i for parameter, index in
        #                 self.parameter_index_map.items() for i in index if
        #                 parameter ]
        if self.training_X is not None:
            valid_indices = []
            all_indices = []
            for parameter, index in self.parameter_index_map.items():
                if parameter in self._partition_success_set:
                    #print(index[0], index[-1])
                    valid_indices += index
                all_indices += index
            valid_indices = sorted(valid_indices)
            self.training_X = self.training_X[:, valid_indices]

        return X

    def fit_transform(self, data_dir):
        """

        """
        self.fit(data_dir)

        #lib_list = self.data #list(self.data.keys())
        X = []
        for lib_file in self.data: #lib_list:
            lib_path = os.path.join(data_dir, lib_file)
            X_ = self.transform(lib_path)
            X.append(X_)
        X = np.vstack(X)
        self.training_X = X
        return X

    def combine_data(self, data_dict):
        """

        """
        assert self._fitted, ("'fit()' or 'fit_transform()' must be called"
                              + " prior to calling 'transform()'")
        X = []
        X2 = []
        index_start = 0

        for i, (lib_file, feat_files) in enumerate(data_dict.items()):
            matrix_list = []
            matrix_list2 = []
            feat_dir = feat_files['directory']
            for f in self._feature_order:
                if f in feat_files['files']:
                    feat_file_path = os.path.join(feat_dir,
                                                  feat_files['files'][f])
                    wait_for_file(feat_file_path)
                    matrix = np.loadtxt(feat_file_path)
                    #matrix2 = pd.read_csv(feat_file_path, sep=' ', header=None)

                    # (X)genESeSS feature files end each line with a space
                    # -> the last column when loading from pandas is just NaNs
                    # -> -> we drop the last column
                    #matrix2.drop(matrix2.columns[-1], axis=1, inplace=True)

                    matrix_list.append(matrix)
                    #matrix_list2.append(matrix2)
                else:
                    continue

                if i == 0 and self.training_X is None:
                    col_len = np.shape(matrix)[1]
                    index_end = index_start + col_len
                    index_range = list(range(index_start, index_end))
                    self.parameter_index_map[f] = index_range
                    index_start = index_end

            X_ = pd.DataFrame(np.hstack(matrix_list))
            #X_2 = pd.concat(matrix_list2, axis=1)
            X.append(X_)
            #X2.append(X_2)
        #X = np.vstack(X)
        X = pd.concat(X, axis=0, ignore_index=True)
        print(X.shape)
        #print(X2.shape)
        return X


    @staticmethod
    def _line_by_line(data_file, *, function, **kwargs):
        """

        """
        directory = os.path.dirname(os.path.realpath(data_file))
        tmp_dir = tempfile.mkdtemp(dir=directory)

        feature_file = data_file + '_features'
        with open(data_file, 'r') as infile:
            for i, line in enumerate(infile):
                line_file = os.path.join(tmp_dir, str(i))
                with open(line_file, 'w') as outfile:
                    outfile.write(line)
                new_line_file = function(line_file, **kwargs)
                lines = []

                wait_for_file(new_line_file)

                with open(new_line_file, 'r') as infile:
                    for line_ in infile:
                        lines.append(line_)
                with open(feature_file, 'a+') as outfile:
                    for line__ in lines:
                        outfile.write(line__)
        #rmtree(tmp_dir)
        return feature_file

    def _get_command_list(self, data_dir):
        """

        """
        problem_type = ['-t']
        num_streams = ['-T']
        if self._problem_type == 2 or self._problem_type == 'supervised':
            problem_type.append("2")
            num_streams.append("-1")
        else:
            num_streams.append(str(self._num_streams))
            if self._problem_type == 1 or self._problem_type == 'unsupervised_with_targets':
                problem_type.append("1")
            elif self._problem_type == 0 or self._problem_type == 'unsupervised':
                problem_type.append("0")

        quantizer_path = os.path.join(self._bin_path, 'Quantizer')
        quantizer_binary = [os.path.abspath(quantizer_path)]
        data_dir = ['-D', data_dir]

        sample_size = ['-x', str(self._sample_size)]

        pooled = ['-w']
        if self._pooled:
            pooled.append("1")
        else:
            pooled.append("0")

        epsilon = ['-e', str(self._epsilon)]

        min_alphabet_size = ['-a', str(self._min_alphabet_size)]
        max_alphabet_size = ['-A', str(self._max_alphabet_size)]

        if self._detrending is not None:
            detrending = ['-d', str(self._detrending)]
        else:
            detrending = []

        if self._normalization is not None:
            normalization = ['-n', str(int(self._normalization))]
        else:
            normalization = []

        command_list = (quantizer_binary +
                        data_dir +
                        problem_type +
                        #num_streams + # TODO: testing Quantizer_v1
                        sample_size +
                        #pooled + # TODO: testing Quantizer_v1
                        epsilon +
                        min_alphabet_size +
                        max_alphabet_size +
                        detrending +
                        normalization)
        self._command_list = command_list

    def _note_lib_files(self, data_dir):
        """

        """
        library_list = os.path.join(data_dir, 'library_list')
        train_data = [row.split(' ')[:2] for row in
                      open(library_list).read().splitlines()]
        for lib, label_str in train_data:
            self.data.append(lib)
            #self.data[lib] = {}
            #self.data[lib]['files'] = {}
            #self.data[lib]['label'] = int(label_str)

    @staticmethod
    def _detrend(df, *, detrend_level):
        """

        """
        return df.diff(axis=1).dropna(how='all', axis=1)

    @staticmethod
    def _normalize(df):
        """

        """
        standard_normal_rows = df.subtract(df.mean(axis=1),
                                           axis=0).divide(df.std(axis=1),
                                                          axis=0)
        return standard_normal_rows

    @staticmethod
    def _prune(df, lower_bound, upper_bound):
        """

        """
        for index in df.index:
            X = []
            for val in df.iloc[index].values:
                if val <= float(lower_bound) or val >= float(upper_bound):
                    X = np.append(X,val)
            pruned_ = np.empty([1, len(df.iloc[index].values) - len(X)])
            pruned_[:] = np.nan
            X = np.append(X, pruned_)
            df.loc[index] = X
        return df

    def _try_apply_quantizer(self, filename, *, partition, prune_range=None,
                             detrending=None, normalization=None, outfile=None,
                             verbose=False):
        """

        """
        max_col_len = 0
        with open(filename, 'r') as infile:
            csv_reader = csv.reader(infile, delimiter=' ')
            for row in csv_reader:
                len_ = len(row)
                if len_ > max_col_len:
                    max_col_len = len_
        unquantized = pd.read_csv(filename, delimiter=' ', dtype='float',
                                  header=None, names=range(max_col_len))

        if prune_range:
            if verbose:
                print('PRUNING')
            unquantized = self._prune(unquantized, prune_range[0], prune_range[1])
        if detrending:
            if verbose:
                print('DETRENDING')
            unquantized = self._detrend(unquantized, detrend_level=detrending)
        if normalization:
            if verbose:
                print('NORMALIZING')
            unquantized = self._normalize(unquantized)

        if outfile is None:
            _outfile = filename
        else:
            _outfile = outfile
        quantized = np.digitize(unquantized, bins=partition)
        #np.savetxt(_outfile, quantized, fmt='%d', delimiter=' ')
        pd.DataFrame(quantized).to_csv(_outfile, sep=' ', index=False, header=False)

        wait_for_file(_outfile)

        if self._correct_num_symbols(quantized, partition):
            return 1
        else:
            return 0


    @staticmethod
    def _correct_num_symbols(quantized_matrix, partition):
        """

        """
        expected_num_symbols = len(partition) + 1
        i = 0
        for row in quantized_matrix:
            num_symbols = len(np.unique(row))
            if num_symbols != expected_num_symbols:
                return False
            i += 1

        return True


    @staticmethod
    def _read_quantizer_params(parameters):
        """

        """
        parameters_ = parameters.split('L')[0]
        prune_range = []
        for index, char in enumerate(parameters_):
            if char == 'R':
                for char_ in parameters_[index+2:]:
                    if char_ != ']':
                        prune_range.append(char_)
                    else:
                        break
            elif char == 'D':
                detrending = int(parameters_[index+1])
            elif char == 'N':
                normalization = int(parameters_[index+1])
        if prune_range:
            prune_range = ''.join(prune_range).split(' ')

        partition = parameters_.split('[')[-1].strip(']').split()
        no_negative_zero_partition = []
        for p in partition:
            if repr(float(p)) == '-0.0':
                p_ = p[1:]
            else:
                p_ = p
            no_negative_zero_partition.append(p_)

        return prune_range, detrending, normalization, no_negative_zero_partition

    @staticmethod
    def _write_quantizer_params(prune_range, detrending, normalization,
                                partition):
        """

        """
        params = []
        if prune_range:
            params.append('R')
            params += prune_range
        if detrending:
            params.append('D')
            params.append(detrending)
        if normalization:
            params.append('N')
            params.append(normalization)
        if partition:
            params.append('P')
            params += str([float(p) for p in partition]).replace(' ', '')
        params_string = ''.join([str(p) for p in params])
        return params_string

    @staticmethod
    def _get_num_cols(infile):
        with open(infile) as f:
            first_line = f.readline()
        first_line_list = first_line.strip.split(' ')
        num_col = len(first_line_list)
        return num_col

